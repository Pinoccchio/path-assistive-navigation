"""Freeze full-image visual decisions for 18 newly flagged OI images."""

import csv
import hashlib
import json
from collections import Counter

from audit_v15_person_960_all import DATASET, OUT
from build_v16_person_quarantine import CLASSES, LEDGER, ROOT

LEDGER_OUT = ROOT / "data/source/oi_vehicle_v10/person_review_v17_additional.json"
RUN = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"
QUEUE_OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v17.csv"

# Decisions made from all five whole-image sheets, with full-size checks of ambiguous cases.
DECISIONS = {
    "00c86ad45b7a1c9b": "visible_person_without_person_box",
    "ce833bef051b8b12": "visible_person_without_person_box",
    "f99c945524367c87": "visible_person_without_person_box",
    "ec274de4ef22499f": "visible_person_without_person_box",
    "61341e263872270a": "uncertain_tiny_proposal",
    "70f19b59313561ef": "visible_person_without_person_box",
    "1aa5a8f4f5a28219": "visible_person_without_person_box",
    "017482da6cb1d140": "visible_person_without_person_box",
    "ae42371d04b01e6c": "false_person_poster",
    "ad36465df2063c13": "visible_person_without_person_box",
    "4cda73e840f5672d": "uncertain_edge_crop",
    "5b429fba2f25dc15": "visible_person_without_person_box",
    "005753525902c0a1": "visible_person_without_person_box",
    "79f5fd4f9f0149cf": "visible_person_without_person_box",
    "b46048fdbde0db62": "false_person_helmet",
    "37a47598b32fd815": "false_person_vehicle_detail",
    "e02fb1199de88ab1": "uncertain_blurred_rider",
    "9ae736386924710c": "false_person_poster",
}


def main():
    if LEDGER_OUT.exists() or (RUN / "draft_v17_120.json").exists() or QUEUE_OUT.exists():
        raise SystemExit("Review expansion already frozen; refusing to overwrite")
    audit = json.loads((OUT / "audit.json").read_text(encoding="utf-8"))
    candidates = {row["image_id"]: row for row in audit["rows"] if row["category"] == "new_zero_person_candidate"}
    assert set(candidates) == set(DECISIONS) and len(candidates) == 18
    sheet_index = {row["image_id"]: row for row in
                   json.loads((OUT / "new_zero_person_sheets/index.json").read_text(encoding="utf-8"))}
    decisions = {}
    for image_id, decision in sorted(DECISIONS.items()):
        row = candidates[image_id]
        image = DATASET / "images/train" / f"oi_v10_train_{image_id}.jpg"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"]
        assert row["existing_person_boxes"] == 0
        decisions[image_id] = {"decision": decision, "image_sha256": row["image_sha256"],
                               "review_sheet": sheet_index[image_id]["sheet"],
                               "sheet_slot": sheet_index[image_id]["slot"]}
    ledger = {"scope": "Image-level visual triage of 18 new zero-person-label candidates from 960px scan; no proposal is ground truth.",
              "review_method": "All five whole-image sheets inspected; eight ambiguous/false cases also checked at full image size.",
              "decisions": decisions,
              "counts": dict(Counter(DECISIONS.values())),
              "remaining_work": "Confirmed images still require exhaustive box annotation and second review; uncertain images stay out of the approved set."}
    LEDGER_OUT.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

    old_draft = json.loads((RUN / "draft.json").read_text(encoding="utf-8"))
    old_ids = {row["image_id"] for row in old_draft["rows"]}
    assert len(old_ids) == 109 and not old_ids.intersection(candidates)
    extra = []
    for image_id, decision in DECISIONS.items():
        if decision != "visible_person_without_person_box":
            continue
        row = candidates[image_id]
        proposals = []
        for p in row["proposals"]:
            x1, y1, x2, y2 = p["box_xyxy"]
            proposals.append({"xyxy_pixels": [x1, y1, x2, y2], "confidence": p["confidence"],
                              "yolo_normalized": [round((x1+x2)/(2*row["width"]), 8),
                                                  round((y1+y2)/(2*row["height"]), 8),
                                                  round((x2-x1)/row["width"], 8),
                                                  round((y2-y1)/row["height"], 8)]})
        extra.append({"image_id": image_id, "image_sha256": row["image_sha256"],
                      "width": row["width"], "height": row["height"],
                      "proposals": proposals, "review_status": "unverified_draft"})
    assert len(extra) == 11
    combined = {key: value for key, value in old_draft.items() if key != "rows"}
    combined.update({"images": 120, "proposals": old_draft["proposals"] + sum(len(r["proposals"]) for r in extra),
                     "review_expansion_ledger_sha256": hashlib.sha256(LEDGER_OUT.read_bytes()).hexdigest(),
                     "rows": old_draft["rows"] + extra})
    (RUN / "draft_v17_120.json").write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")

    with (ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority.csv").open(newline="", encoding="utf-8") as handle:
        priorities = list(csv.DictReader(handle))
    for row in extra:
        image_id = row["image_id"]
        stem = f"oi_v10_train_{image_id}"
        counts = Counter(CLASSES[int(line.split()[0])] for line in
                         (DATASET / "labels/train" / f"{stem}.txt").read_text().splitlines())
        info = decisions[image_id]
        priorities.append({"image_id": image_id,
                           "review_sheet": str(OUT / "new_zero_person_sheets" / info["review_sheet"]),
                           "sheet_slot": info["sheet_slot"],
                           "image_path": str(DATASET / "images/train" / f"{stem}.jpg"),
                           "label_path": str(DATASET / "labels/train" / f"{stem}.txt"),
                           "bicycle_boxes": counts["bicycle"], "motorcycle_boxes": counts["motorcycle"],
                           "car_boxes": counts["car"],
                           "status": "person annotation needed; vehicle completeness unverified"})
    assert len(priorities) == 120 and len({row["image_id"] for row in priorities}) == 120
    priorities.sort(key=lambda r: (-(int(r["bicycle_boxes"])+int(r["motorcycle_boxes"])),
                                   -int(r["bicycle_boxes"]), r["image_id"]))
    with QUEUE_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(priorities[0]))
        writer.writeheader()
        writer.writerows(priorities)
    print(json.dumps({"new_confirmed": len(extra), "combined_review_images": len(priorities),
                      "decision_counts": ledger["counts"]}, indent=2))


if __name__ == "__main__":
    main()

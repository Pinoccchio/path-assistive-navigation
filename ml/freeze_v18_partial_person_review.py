"""Prepare candidate review of 59 partially labeled OI images; no labels changed."""

import csv
import hashlib
import json
from collections import Counter

from audit_v15_person_960_all import DATASET, OUT
from build_v16_person_quarantine import CLASSES, ROOT

RUN = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"
LEDGER = ROOT / "data/source/oi_vehicle_v10/person_review_v18_partial.json"
QUEUE = ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v18.csv"
DRAFT = RUN / "draft_v18_179.json"


def main():
    if LEDGER.exists() or QUEUE.exists() or DRAFT.exists():
        raise SystemExit("v18 review expansion already frozen; refusing to overwrite")
    audit = json.loads((OUT / "audit.json").read_text(encoding="utf-8"))
    rows = [row for row in audit["rows"] if row["category"] == "existing_person_candidate"]
    assert len(rows) == 59
    index = {row["image_id"]: row for row in
             json.loads((OUT / "partial_person_sheets/index.json").read_text(encoding="utf-8"))}
    old = json.loads((RUN / "draft_v17_120.json").read_text(encoding="utf-8"))
    old_ids = {row["image_id"] for row in old["rows"]}
    assert len(old_ids) == 120 and not old_ids.intersection(row["image_id"] for row in rows)
    new_rows, decisions = [], {}
    with (ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v17.csv").open(newline="", encoding="utf-8") as handle:
        priorities = list(csv.DictReader(handle))
    for row in rows:
        image_id = row["image_id"]
        stem = f"oi_v10_train_{image_id}"
        image = DATASET / "images/train" / f"{stem}.jpg"
        label = DATASET / "labels/train" / f"{stem}.txt"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"]
        labels = label.read_text().splitlines()
        existing = []
        counts = Counter()
        for line in labels:
            cls, xc, yc, bw, bh = map(float, line.split())
            counts[CLASSES[int(cls)]] += 1
            if int(cls) == 0:
                existing.append([(xc-bw/2)*row["width"], (yc-bh/2)*row["height"],
                                 (xc+bw/2)*row["width"], (yc+bh/2)*row["height"]])
        assert len(existing) == row["existing_person_boxes"] > 0
        proposals = [{"xyxy_pixels": [round(v, 1) for v in box], "confidence": None,
                      "origin": "source_person_label"} for box in existing]
        proposals += [{"xyxy_pixels": p["box_xyxy"], "confidence": p["confidence"],
                       "origin": "model_review_proposal"} for p in row["proposals"]]
        new_rows.append({"image_id": image_id, "image_sha256": row["image_sha256"],
                         "width": row["width"], "height": row["height"],
                         "source_person_boxes": len(existing), "proposals": proposals,
                         "review_status": "unverified_draft"})
        decisions[image_id] = {"review_category": "existing_person_candidate_needs_instance_review",
                               "image_sha256": row["image_sha256"], "label_sha256": hashlib.sha256(label.read_bytes()).hexdigest(),
                               "source_person_boxes": len(existing), "unmatched_model_proposals": len(row["proposals"]),
                               "review_sheet": index[image_id]["sheet"], "sheet_slot": index[image_id]["slot"]}
        priorities.append({"image_id": image_id,
                           "review_sheet": str(OUT / "partial_person_sheets" / index[image_id]["sheet"]),
                           "sheet_slot": index[image_id]["slot"], "image_path": str(image),
                           "label_path": str(label), "bicycle_boxes": counts["bicycle"],
                           "motorcycle_boxes": counts["motorcycle"], "car_boxes": counts["car"],
                           "status": "partial person labels; instance review needed"})
    ledger = {"scope": "59 Open Images training images with existing person labels and unmatched 960px person proposals.",
              "review_method": "All 15 whole-image sheets visually inspected; many missing people and some false model proposals visible. Individual image completeness is not approved.",
              "decisions": decisions,
              "policy": "Preserve source person boxes as editable starting boxes. No model proposal is ground truth."}
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    combined = {key: value for key, value in old.items() if key != "rows"}
    combined.update({"images": 179, "proposals": old["proposals"] + sum(len(r["proposals"]) for r in new_rows),
                     "partial_review_ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
                     "rows": old["rows"] + new_rows})
    DRAFT.write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")
    assert len(priorities) == 179 and len({row["image_id"] for row in priorities}) == 179
    priorities.sort(key=lambda r: (-(int(r["bicycle_boxes"])+int(r["motorcycle_boxes"])),
                                   -int(r["bicycle_boxes"]), r["image_id"]))
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(priorities[0]))
        writer.writeheader()
        writer.writerows(priorities)
    print(json.dumps({"confirmed_zero_person_images": 120,
                      "partially_labeled_review_candidates": len(new_rows),
                      "total_review_images": len(priorities)}, indent=2))


if __name__ == "__main__":
    main()

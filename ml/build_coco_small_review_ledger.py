"""Create an evidence ledger for the 80-image COCO small-bicycle review batch."""

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/source/coco_external/small_bicycle_review_v1"

# Screen-level findings only. No row in this ledger authorizes training use.
FINDINGS = {
    "000000430342": ("suspect_label", "Selected bicycle box is on a skateboard scene; no bicycle is visible at the marked target."),
    "000000213527": ("suspect_label", "Selected box is in a beach scene with surfboards; no bicycle is visible at the marked target."),
    "000000539793": ("suspect_label", "Selected small box is on a skateboard sequence; inspect any distant bicycles separately."),
    "000000330649": ("unresolvable_target", "Selected box lies in a narrow bus/car gap; bicycle identity is not visually clear."),
    "000000526514": ("unresolvable_target", "Selected distant box is too dark and small to establish a bicycle from the review crop."),
    "000000023094": ("unresolvable_target", "Very small cyclist-like shape behind the horse cart; bike geometry is not clear."),
    "000000488990": ("unresolvable_target", "Selected box lies on pedestrians/railing; bicycle is not clearly visible."),
    "000000555355": ("unresolvable_target", "Selected box is a narrow object at the image edge beside a parked truck."),
    "000000015486": ("class_confusion_risk", "Crowded bicycle/motorcycle retail scene needs instance-by-instance class review."),
    "000000122302": ("class_confusion_risk", "Crowded vehicle parking scene contains motorcycles and bicycles; review all classes and boxes."),
    "000000004489": ("incomplete_annotation_risk", "Many parked bicycles overlap; verify each distinct instance and full box."),
    "000000305885": ("incomplete_annotation_risk", "Street bicycle cluster has many overlapping boxes; verify completeness."),
    "000000027975": ("incomplete_annotation_risk", "Street scene has bicycles in the shopfront; verify all instances and small boxes."),
    "000000429759": ("incomplete_annotation_risk", "Crowded cycle-cart scene has dense overlapping source boxes."),
    "000000090218": ("incomplete_annotation_risk", "Cycle race has many small bicycles; verify visible riders and boxes."),
    "000000197705": ("incomplete_annotation_risk", "Cycle race has many small bicycles; verify visible riders and boxes."),
    "000000449638": ("promising_context", "Street scene contains multiple cyclists at varied distances; verify complete labels."),
    "000000421893": ("promising_context", "Path scene contains cyclists at varied distances; verify complete labels."),
    "000000517612": ("promising_context", "Foggy square has a visible distant bicycle; verify box and all target instances."),
}

# Original-size bicycle/motorcycle overlay screening of all 18 images with
# Attribution or Attribution-ShareAlike metadata. These still need rights and
# exhaustive instance review before any training use.
PRIORITY_VISUAL = {
    "000000234755", "000000429759", "000000126028", "000000476841",
    "000000331386", "000000070321", "000000472169",
}


def main():
    selection = json.loads((REVIEW / "selection.json").read_text(encoding="utf-8"))
    selected_ids = {row["image_id"] for row in selection["rows"]}
    assert set(FINDINGS) <= selected_ids, sorted(set(FINDINGS) - selected_ids)
    assert PRIORITY_VISUAL <= selected_ids
    comparison_path = REVIEW / "official_annotation_comparison.jsonl"
    comparisons = ({row["image_id"]: row for row in
                    (json.loads(line) for line in comparison_path.read_text(encoding="utf-8").splitlines())}
                   if comparison_path.exists() else {})
    if comparisons:
        assert set(comparisons) == selected_ids
    rows = []
    for row in selection["rows"]:
        image_id = row["image_id"]
        image = REVIEW / "images" / f"{image_id}.jpg"
        assert image.exists(), image
        status, finding = FINDINGS.get(image_id, ("screened_unresolved", "Contact/detail sheets screened; full instance-level verification pending."))
        official = comparisons.get(image_id)
        lower_restriction_metadata = official and official["license_name"] in (
            "Attribution License", "Attribution-ShareAlike License")
        rows.append({"image_id": image_id, "group": row["group"],
                     "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                     "source_label_sha256": row["label_sha256"],
                     "screening_status": status, "finding": finding,
                     "all_bicycle_instances_verified": False,
                     "all_motorcycle_instances_verified": False,
                     "official_annotation_compared": official is not None,
                     "official_non_crowd_vehicle_boxes_match": (
                         official["unmatched_converted_boxes"] == 0 and
                         all(box["iscrowd"] == 1 for box in official["unmatched_official"])
                         if official else None),
                     "official_missing_crowd_boxes": len(official["unmatched_official"]) if official else None,
                     "license_name": official["license_name"] if official else None,
                     "license_url": official["license_url"] if official else None,
                     "flickr_url": official["flickr_url"] if official else None,
                     "lower_restriction_license_metadata": bool(lower_restriction_metadata),
                     "priority_visual_status": (
                         "promising_requires_full_instance_and_rights_review" if image_id in PRIORITY_VISUAL
                         else "hold_visual_uncertainty" if lower_restriction_metadata else "not_prioritized_by_license_metadata"),
                     "image_license_checked": False,
                     "training_approved": False})
    assert len(rows) == len({row["image_id"] for row in rows}) == 80
    (REVIEW / "review_ledger.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "status_counts": dict(Counter(row["screening_status"] for row in rows)),
                      "official_non_crowd_matches": sum(row["official_non_crowd_vehicle_boxes_match"] is True for row in rows),
                      "priority_visual_counts": dict(Counter(row["priority_visual_status"] for row in rows)),
                      "training_approved": 0}, indent=2))


if __name__ == "__main__":
    main()

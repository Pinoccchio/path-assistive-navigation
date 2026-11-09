"""Verify 59 partially labeled review candidates and 179-image combined queue."""

import csv
import hashlib
import json

from freeze_v18_partial_person_review import DATASET, DRAFT, LEDGER, QUEUE, RUN


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert len(ledger["decisions"]) == 59
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    old = json.loads((RUN / "draft_v17_120.json").read_text(encoding="utf-8"))
    assert draft["partial_review_ledger_sha256"] == hashlib.sha256(LEDGER.read_bytes()).hexdigest()
    assert draft["rows"][:120] == old["rows"]
    assert len(draft["rows"]) == len({row["image_id"] for row in draft["rows"]}) == 179
    assert draft["proposals"] == sum(len(row["proposals"]) for row in draft["rows"])
    for row in draft["rows"]:
        image = DATASET / "images/train" / f"oi_v10_train_{row['image_id']}.jpg"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"]
        source_count = sum(p.get("origin") == "source_person_label" for p in row["proposals"])
        if row["image_id"] in ledger["decisions"]:
            info = ledger["decisions"][row["image_id"]]
            label = DATASET / "labels/train" / f"oi_v10_train_{row['image_id']}.txt"
            assert hashlib.sha256(label.read_bytes()).hexdigest() == info["label_sha256"]
            assert source_count == info["source_person_boxes"] > 0
            assert len(row["proposals"]) - source_count == info["unmatched_model_proposals"]
        for proposal in row["proposals"]:
            x1, y1, x2, y2 = proposal["xyxy_pixels"]
            assert 0 <= x1 < x2 <= row["width"] and 0 <= y1 < y2 <= row["height"]
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        queue = list(csv.DictReader(handle))
    assert len(queue) == 179
    assert {row["image_id"] for row in queue} == {row["image_id"] for row in draft["rows"]}
    report = {"total_review_images": 179, "confirmed_zero_person_images": 120,
              "partial_label_review_candidates": 59,
              "source_images_hash_verified": 179,
              "draft_boxes_geometry_checked": draft["proposals"],
              "semantic_box_approval": False, "dataset_labels_changed": False}
    (RUN / "qa_v18_partial_review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

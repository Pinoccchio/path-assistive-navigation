"""Verify frozen visual decisions and combined draft without approving boxes."""

import csv
import hashlib
import json
from collections import Counter

from freeze_v17_person_review_expansion import DATASET, DECISIONS, LEDGER_OUT, QUEUE_OUT, RUN


def main():
    ledger = json.loads(LEDGER_OUT.read_text(encoding="utf-8"))
    assert {key: row["decision"] for key, row in ledger["decisions"].items()} == DECISIONS
    assert Counter(DECISIONS.values()) == Counter(ledger["counts"])
    draft = json.loads((RUN / "draft_v17_120.json").read_text(encoding="utf-8"))
    old = json.loads((RUN / "draft.json").read_text(encoding="utf-8"))
    assert draft["review_expansion_ledger_sha256"] == hashlib.sha256(LEDGER_OUT.read_bytes()).hexdigest()
    assert draft["rows"][:109] == old["rows"]
    ids = {row["image_id"] for row in draft["rows"]}
    added = {key for key, decision in DECISIONS.items() if decision == "visible_person_without_person_box"}
    assert len(ids) == len(draft["rows"]) == 120
    assert {row["image_id"] for row in draft["rows"][109:]} == added
    assert draft["proposals"] == sum(len(row["proposals"]) for row in draft["rows"])
    for row in draft["rows"]:
        image_id = row["image_id"]
        image = DATASET / "images/train" / f"oi_v10_train_{image_id}.jpg"
        label = DATASET / "labels/train" / f"oi_v10_train_{image_id}.txt"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"]
        assert not any(line.startswith("0 ") for line in label.read_text().splitlines())
        assert row["review_status"] == "unverified_draft"
        for proposal in row["proposals"]:
            x1, y1, x2, y2 = proposal["xyxy_pixels"]
            assert 0 <= x1 < x2 <= row["width"] and 0 <= y1 < y2 <= row["height"]
    with QUEUE_OUT.open(newline="", encoding="utf-8") as handle:
        queue = list(csv.DictReader(handle))
    assert len(queue) == 120 and {row["image_id"] for row in queue} == ids
    report = {"review_images": len(ids), "newly_confirmed_images": len(added),
              "false_candidates": sum(value.startswith("false_") for value in DECISIONS.values()),
              "uncertain_candidates": sum(value.startswith("uncertain_") for value in DECISIONS.values()),
              "draft_boxes_geometry_checked": draft["proposals"],
              "source_images_hash_verified": len(ids),
              "all_review_images_have_zero_person_labels": True,
              "semantic_box_approval": False}
    (RUN / "qa_v17_review_expansion.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

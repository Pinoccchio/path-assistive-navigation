"""Report human-review progress without changing dataset labels."""

import hashlib
import json
from collections import Counter

from person_review_server import REVIEW, RUN, SOURCE, draft_rows, validate_review


def main():
    rows = draft_rows()
    statuses = Counter()
    ready = []
    issues = []
    for image_id, draft in rows.items():
        path = REVIEW / f"{image_id}.json"
        if not path.exists():
            statuses["not_started"] += 1
            continue
        try:
            review = validate_review(json.loads(path.read_text(encoding="utf-8")), draft)
            image = SOURCE / f"oi_v10_train_{image_id}.jpg"
            assert hashlib.sha256(image.read_bytes()).hexdigest() == review["image_sha256"]
            statuses[review["status"]] += 1
            if review["status"] == "second_review_complete" and review["vehicle_completeness_checked"]:
                ready.append(image_id)
        except (ValueError, AssertionError, KeyError, TypeError, json.JSONDecodeError) as error:
            statuses["invalid_review"] += 1
            issues.append({"image_id": image_id, "error": str(error)})
    extra = sorted(path.stem for path in REVIEW.glob("*.json") if path.stem not in rows) if REVIEW.exists() else []
    assert sum(statuses.values()) == len(rows) == 179
    report = {"total_images": len(rows), "statuses": dict(statuses),
              "ready_for_corrected_dataset": len(ready), "ready_ids": sorted(ready),
              "invalid_or_stale_reviews": issues, "unexpected_review_files": extra,
              "dataset_labels_changed": False,
              "policy": "Ready requires second human review and vehicle-completeness check; a future builder must still validate boxes and preserve val/test."}
    (RUN / "human_review_progress.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "ready_ids"}, indent=2))


if __name__ == "__main__":
    main()

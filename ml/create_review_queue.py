"""Prepare a human semantic-review queue without editing a frozen dataset."""

import argparse
import csv
import json

from phase1 import NAMES, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v3_screened")
    args = parser.parse_args()
    dataset = ROOT / "data" / "processed" / args.dataset_name
    rows = [json.loads(line) for line in (dataset / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    target = dataset / "semantic_review_queue.csv"
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("id", "split", "source", "group", "classes", "image_path", "priority",
                         "review_status", "decision", "correction_notes"))
        for row in rows:
            classes = set(row["class_ids"])
            if not classes & {2, 5, 6}:
                continue
            priority = "highest" if 5 in classes else "high" if 6 in classes else "normal"
            writer.writerow((row["id"], row["split"], row["source"], row["group"],
                             ";".join(NAMES[index] for index in sorted(classes)),
                             str(dataset / "images" / row["split"] / f"{row['id']}.jpg"),
                             priority, "pending", "", ""))
    print(f"{target}: {sum(bool(set(row['class_ids']) & {2, 5, 6}) for row in rows)} rows")


if __name__ == "__main__":
    main()

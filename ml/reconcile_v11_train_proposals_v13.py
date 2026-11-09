"""Reconcile the old v11 vehicle review queue against current v13 labels.

The queue is a review aid only. This script never writes training labels.
"""

import argparse
import csv
import json
from pathlib import Path

from PIL import Image

from phase1 import ROOT


QUEUE = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_label_audit_queue.json"
DATASET = ROOT / "data/processed/public_phase1_v13_four_box_pilot"
OUTPUT = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_proposals_reconciled_v13.csv"


def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection) if area_a + area_b > intersection else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    dataset = args.dataset
    output_path = args.output
    rows = json.loads(QUEUE.read_text(encoding="utf-8"))["rows"]
    output = []
    for row in rows:
        image_id = row["image_id"]
        stem = f"oi_v10_train_{image_id}"
        image = dataset / "images/train" / f"{stem}.jpg"
        label = dataset / "labels/train" / f"{stem}.txt"
        with Image.open(image) as source:
            width, height = source.size
        current = []
        for line in label.read_text(encoding="utf-8").splitlines():
            cls, xc, yc, bw, bh = map(float, line.split())
            current.append((int(cls), [(xc - bw / 2) * width, (yc - bh / 2) * height,
                                       (xc + bw / 2) * width, (yc + bh / 2) * height]))
        for proposal in row["unmatched_predictions"]:
            box = proposal["box_xyxy"]
            same = max((iou(box, b) for cls, b in current if cls == proposal["class_id"]), default=0.0)
            other = max((iou(box, b) for cls, b in current if cls in (4, 7) and cls != proposal["class_id"]), default=0.0)
            output.append({"image_id": image_id, "class_id": proposal["class_id"],
                           "confidence": round(proposal["confidence"], 4),
                           "same_class_iou_v13": round(same, 4), "other_vehicle_iou_v13": round(other, 4),
                           "review_status": "already_boxed" if same >= 0.5 else
                           "class_conflict_review" if other >= 0.5 else "visual_review_needed",
                           "box_xyxy": json.dumps([round(v, 1) for v in box])})
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)
    counts = {status: sum(row["review_status"] == status for row in output)
              for status in ("already_boxed", "class_conflict_review", "visual_review_needed")}
    print(json.dumps({"proposals": len(output), "counts": counts, "output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()

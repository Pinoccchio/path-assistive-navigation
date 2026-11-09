"""Rank current retained OI train images for possible missing person labels.

Uses the original COCO-pretrained checkpoint as a review trigger, not as truth.
"""

import csv
import json

from PIL import Image
from ultralytics import YOLO

from phase1 import ROOT


DATASET = ROOT / "data/processed/public_phase1_v15_oi_quarantine"
SELECTION = ROOT / "data/source/oi_vehicle_v10/train_selection.json"
OUTPUT = ROOT / "runs/public_phase1_v15_oi_quarantine"
WEIGHTS = ROOT / "notebooks/yolov8n.pt"


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    overlap = max(0, x2 - x1) * max(0, y2 - y1)
    a_area = (a[2] - a[0]) * (a[3] - a[1])
    b_area = (b[2] - b[0]) * (b[3] - b[1])
    return overlap / (a_area + b_area - overlap) if a_area + b_area > overlap else 0.0


def main():
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))["rows"]
    manifest = [json.loads(line) for line in (DATASET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    retained = {row["source_id"] for row in manifest if row["split"] == "train" and row["source"] == "OpenImagesV7"}
    rows = [row for row in selection if row["image_id"] in retained]
    assert len(rows) == 283
    model = YOLO(str(WEIGHTS))
    findings = []
    for item in rows:
        image_id = item["image_id"]
        stem = f"oi_v10_train_{image_id}"
        image = DATASET / "images/train" / f"{stem}.jpg"
        label = DATASET / "labels/train" / f"{stem}.txt"
        with Image.open(image) as source:
            width, height = source.size
        truth = []
        for line in label.read_text(encoding="utf-8").splitlines():
            cls, xc, yc, bw, bh = map(float, line.split())
            if int(cls) == 0:
                truth.append([(xc - bw / 2) * width, (yc - bh / 2) * height,
                              (xc + bw / 2) * width, (yc + bh / 2) * height])
        result = model.predict(str(image), imgsz=512, conf=0.5, classes=[0], verbose=False)[0]
        proposals = []
        for box in result.boxes:
            coords = list(map(float, box.xyxy[0]))
            best = max((iou(coords, existing) for existing in truth), default=0.0)
            if best < 0.1:
                proposals.append({"confidence": round(float(box.conf[0]), 4),
                                  "box_xyxy": [round(v, 1) for v in coords],
                                  "best_person_iou": round(best, 4)})
        if proposals:
            findings.append({"image_id": image_id, "group": item["group"],
                             "person_boxes": len(truth), "proposals": proposals})
    findings.sort(key=lambda row: (-len(row["proposals"]), -max(p["confidence"] for p in row["proposals"]), row["image_id"]))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"model": str(WEIGHTS), "dataset": str(DATASET), "retained_images": len(rows),
              "flagged_images": len(findings), "flagged_proposals": sum(len(row["proposals"]) for row in findings),
              "policy": "Review trigger only; do not auto-promote detections as labels.", "rows": findings}
    (OUTPUT / "person_label_audit_queue.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUTPUT / "person_label_audit_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("image_id", "group", "person_boxes", "proposals", "highest_confidence"))
        for row in findings:
            writer.writerow((row["image_id"], row["group"], row["person_boxes"],
                             len(row["proposals"]), max(p["confidence"] for p in row["proposals"])))
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()

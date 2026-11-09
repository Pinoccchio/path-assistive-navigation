"""Rank retained Open Images train images for missing vehicle-label review."""

import csv
import json

from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from phase1 import ROOT


SOURCE = ROOT / "data" / "source" / "oi_vehicle_v10"
RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"


def target_box(box, width, height):
    _, xc, yc, w, h = box
    return [(xc - w / 2) * width, (yc - h / 2) * height,
            (xc + w / 2) * width, (yc + h / 2) * height]


def main():
    rows = json.loads((SOURCE / "train_selection.json").read_text(encoding="utf-8"))["rows"]
    excluded = json.loads((SOURCE / "review_exclusions.json").read_text(encoding="utf-8"))["train"]
    excluded.update(json.loads((SOURCE / "train_review_v11.json").read_text(encoding="utf-8"))["excluded"])
    rows = [row for row in rows if row["image_id"] not in excluded]
    assert len(rows) == 290
    model = YOLO(str(RUN / "yolov8n" / "weights" / "best.pt"))
    findings = []
    for row in rows:
        image_id = row["image_id"]
        path = SOURCE / "images" / "train" / f"{image_id}.jpg"
        result = model.predict(str(path), imgsz=512, conf=0.4, verbose=False)[0]
        height, width = result.orig_shape
        truth = {cls: [target_box(box, width, height) for box in row["boxes"] if box[0] == cls]
                 for cls in (4, 7)}
        unmatched = []
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls not in (4, 7):
                continue
            coords = list(map(float, box.xyxy[0]))
            best_iou = max((iou(coords, gt) for gt in truth[cls]), default=0.0)
            if best_iou < 0.1:
                unmatched.append({"class_id": cls, "confidence": float(box.conf[0]),
                                  "box_xyxy": coords, "best_same_class_iou": best_iou})
        if unmatched:
            findings.append({"image_id": image_id, "group": row["group"],
                             "source_boxes": len(row["boxes"]),
                             "unmatched_predictions": unmatched,
                             "priority": max(pred["confidence"] for pred in unmatched)})
    findings.sort(key=lambda row: (-len(row["unmatched_predictions"]), -row["priority"], row["image_id"]))
    report = {"retained_train_images": len(rows), "flagged_images": len(findings),
              "method": "v11 inference at 512px/confidence 0.4; bicycle/motorcycle predictions with IoU <0.1 to every same-class source box",
              "warning": "Prediction is not a ground-truth annotation. Review visually; do not auto-add boxes or alter frozen test labels.",
              "rows": findings}
    (RUN / "train_vehicle_label_audit_queue.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (RUN / "train_vehicle_label_audit_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("rank", "image_id", "group", "source_boxes", "unmatched_predictions", "highest_confidence", "image_path"))
        for rank, item in enumerate(findings, 1):
            writer.writerow((rank, item["image_id"], item["group"], item["source_boxes"],
                             len(item["unmatched_predictions"]), round(item["priority"], 4),
                             SOURCE / "images" / "train" / f"{item['image_id']}.jpg"))
    print(json.dumps({"retained_train_images": len(rows), "flagged_images": len(findings),
                      "top_ten": [row["image_id"] for row in findings[:10]]}, indent=2))


if __name__ == "__main__":
    main()

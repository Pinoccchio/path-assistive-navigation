"""Measure whether small-bicycle misses are absent detections or localization misses."""

import json

from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from evaluate_v11_reviewed_640_candidate import RUN, selection
from phase1 import ROOT


def xyxy(box, width, height):
    _, xc, yc, w, h = box
    return [(xc - w / 2) * width, (yc - h / 2) * height,
            (xc + w / 2) * width, (yc + h / 2) * height]


def main():
    rows, _, _, _ = selection("small_bicycle")
    model = YOLO(str(RUN / "yolov8n" / "weights" / "best.pt"))
    details = []
    for row in rows:
        image_id = row["image_id"]
        path = ROOT / "data" / "source" / "oi_vehicle_v10" / "images" / "test" / f"{image_id}.jpg"
        result = model.predict(str(path), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        pred = [list(map(float, box.xyxy[0])) for box in result.boxes if int(box.cls[0]) == 4]
        for index, gt in enumerate(row["boxes"]):
            target = xyxy(gt, width, height)
            overlap = max((iou(target, box) for box in pred), default=0.0)
            center_hit = any(box[0] <= (target[0] + target[2]) / 2 <= box[2] and
                             box[1] <= (target[1] + target[3]) / 2 <= box[3] for box in pred)
            details.append({"image_id": image_id, "gt_index": index,
                            "approx_side_at_512": (gt[3] * gt[4]) ** 0.5 * 512,
                            "best_same_class_iou": overlap,
                            "gt_center_in_prediction": center_hit,
                            "same_class_predictions_on_image": len(pred)})
    report = {"images": len(rows), "boxes": len(details),
              "iou_ge_0_1": sum(row["best_same_class_iou"] >= 0.1 for row in details),
              "iou_ge_0_3": sum(row["best_same_class_iou"] >= 0.3 for row in details),
              "iou_ge_0_5": sum(row["best_same_class_iou"] >= 0.5 for row in details),
              "gt_center_in_prediction": sum(row["gt_center_in_prediction"] for row in details),
              "zero_overlap": sum(row["best_same_class_iou"] == 0 for row in details),
              "limitations": "Diagnostic on post-hoc public slice with incomplete Open Images boxes. Independent phone-domain performance cannot be inferred.",
              "rows": details}
    out = RUN / "small_bicycle_localization_diagnostic_512.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()

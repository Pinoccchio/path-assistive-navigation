"""Controlled v11 full-frame plus 2x2 tiled inference on existing diagnostics."""

import hashlib
import json
import time
from collections import Counter

import cv2
from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from evaluate_v10_oi_vehicle_candidate import OI, boxes
from evaluate_v11_reviewed_640_candidate import RUN, selection


OUT = RUN / "tiled_inference_512"
CLASSES = (0, 4, 7)


def suppress(detections, threshold=0.5):
    kept = []
    for candidate in sorted(detections, key=lambda row: row["confidence"], reverse=True):
        if all(candidate["class_id"] != prior["class_id"] or
               iou(candidate["xyxy"], prior["xyxy"]) < threshold for prior in kept):
            kept.append(candidate)
    return kept


def predict(model, image, tiled, source_path):
    height, width = image.shape[:2]
    regions = [(0, 0, width, height)]
    if tiled:
        tile_w, tile_h = round(width * 0.6), round(height * 0.6)
        regions += [(x, y, x + tile_w, y + tile_h)
                    for y in (0, height - tile_h) for x in (0, width - tile_w)]
    detections = []
    start = time.perf_counter()
    for left, top, right, bottom in regions:
        source = (str(source_path) if left == 0 and top == 0 and right == width and bottom == height
                  else image[top:bottom, left:right].copy())
        result = model.predict(source, imgsz=512, conf=0.25,
                               device=0, verbose=False)[0]
        for box in result.boxes:
            category = int(box.cls[0])
            if category not in CLASSES:
                continue
            x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
            detections.append({"class_id": category,
                               "confidence": float(box.conf[0]),
                               "xyxy": [max(0, x1 + left), max(0, y1 + top),
                                        min(width, x2 + left), min(height, y2 + top)]})
    elapsed = time.perf_counter() - start
    return (suppress(detections) if tiled else detections), elapsed


def assess_case(row, predictions, width, height):
    counts = Counter()
    for category, name in ((4, "bicycle"), (7, "motorcycle")):
        pred = [item["xyxy"] for item in predictions if item["class_id"] == category]
        truth = boxes(row, category, width, height)
        pairs = sorted(((iou(p, g), pi, gi) for pi, p in enumerate(pred)
                        for gi, g in enumerate(truth)), reverse=True)
        used_pred, used_truth = set(), set()
        for score, pi, gi in pairs:
            if score < 0.5:
                break
            if pi not in used_pred and gi not in used_truth:
                used_pred.add(pi)
                used_truth.add(gi)
        counts[f"{name}_gt"] = len(truth)
        counts[f"{name}_matched"] = len(used_truth)
        counts[f"{name}_pred"] = len(pred)
    counts["person_pred"] = sum(item["class_id"] == 0 for item in predictions)
    if row["group"] == "motorcycle" and counts["bicycle_pred"]:
        counts["moto_only_images_with_bicycle_prediction"] = 1
    if row["group"] == "small_bicycle" and counts["motorcycle_pred"]:
        counts["bike_only_images_with_motorcycle_prediction"] = 1
    return counts


def main():
    weights = RUN / "yolov8n" / "weights" / "best.pt"
    model = YOLO(str(weights))
    OUT.mkdir(exist_ok=True)
    report = {"model": "v11", "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
              "input_size": 512, "confidence": 0.25, "matching_iou": 0.5,
              "tile_fraction": 0.6, "windows": "full frame plus four overlapping corner crops",
              "nms_iou": 0.5,
              "limitations": "Post-hoc public development diagnostics with incomplete source labels; desktop GPU timing does not establish phone latency or safety.",
              "diagnostics": {}}
    for kind in ("small_bicycle", "vehicle"):
        rows, checksums, _, _ = selection(kind)
        totals = {name: Counter() for name in ("full", "full_plus_tiles")}
        seconds = {name: 0.0 for name in totals}
        details = []
        for index, row in enumerate(rows, 1):
            image_id = row["image_id"]
            path = OI / "images" / "test" / f"{image_id}.jpg"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == checksums[image_id]
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            assert image is not None, path
            outcome = {"image_id": image_id, "group": row["group"]}
            for name, tiled in (("full", False), ("full_plus_tiles", True)):
                predictions, elapsed = predict(model, image, tiled, path)
                metrics = assess_case(row, predictions, image.shape[1], image.shape[0])
                totals[name].update(metrics)
                seconds[name] += elapsed
                outcome[name] = {**metrics, "seconds": elapsed}
            details.append(outcome)
            if index % 10 == 0:
                print(f"{kind} {index}/{len(rows)}", flush=True)
        report["diagnostics"][kind] = {
            name: {"counts": dict(totals[name]), "total_seconds": seconds[name],
                   "mean_seconds_per_image": seconds[name] / len(rows)} for name in totals}
        report["diagnostics"][kind]["images"] = len(rows)
        report["diagnostics"][kind]["rows"] = details
        (OUT / f"{kind}.json").write_text(json.dumps(report["diagnostics"][kind], indent=2), encoding="utf-8")
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({kind: {name: report["diagnostics"][kind][name] for name in ("full", "full_plus_tiles")}
                      for kind in report["diagnostics"]}, indent=2))


if __name__ == "__main__":
    main()

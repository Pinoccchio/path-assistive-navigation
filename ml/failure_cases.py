"""List public-test false negatives and false positives at IoU >= 0.5.

This is descriptive error analysis after the frozen public-test evaluation, not
a parameter-tuning command. Predictions use confidence >= 0.25.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from ultralytics import YOLO

from phase1 import NAMES, OUTPUT, ROOT


def iou(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    return intersection / (area_a + area_b - intersection) if area_a + area_b > intersection else 0.0


def ground_truth(path: Path, width: int, height: int) -> list[tuple[int, tuple[float, ...]]]:
    boxes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        class_id, x, y, w, h = (float(value) for value in line.split())
        boxes.append((int(class_id), ((x - w / 2) * width, (y - h / 2) * height,
                                      (x + w / 2) * width, (y + h / 2) * height)))
    return boxes


def main() -> None:
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v1")
    parser.add_argument("--weights", default=None)
    parser.add_argument("--device", default="0")
    args = parser.parse_args()
    OUTPUT = ROOT / "data" / "processed" / args.dataset_name
    weights = args.weights or str(ROOT / "runs" / args.dataset_name / "yolov8n" / "weights" / "best.pt")
    manifest = [json.loads(line) for line in (OUTPUT / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    images = [OUTPUT / "images" / "test" / f"{row['id']}.jpg" for row in manifest if row["split"] == "test"]
    model = YOLO(weights)
    cases = []
    for result in model.predict(source=[str(path) for path in images], imgsz=512, batch=16,
                                conf=0.25, device=args.device, stream=True, verbose=False):
        path = Path(result.path)
        height, width = result.orig_shape
        truth = ground_truth(OUTPUT / "labels" / "test" / f"{path.stem}.txt", width, height)
        predictions = [(int(box.cls.item()), tuple(float(v) for v in box.xyxy[0].tolist()),
                        float(box.conf.item())) for box in result.boxes]
        matched_truth = set()
        matched_predictions = set()
        for prediction_index in sorted(range(len(predictions)), key=lambda i: -predictions[i][2]):
            class_id, box, _ = predictions[prediction_index]
            candidates = [(iou(box, target), truth_index) for truth_index, (target_class, target) in enumerate(truth)
                          if target_class == class_id and truth_index not in matched_truth]
            if candidates:
                overlap, truth_index = max(candidates)
                if overlap >= 0.5:
                    matched_truth.add(truth_index)
                    matched_predictions.add(prediction_index)
        for truth_index, (class_id, _) in enumerate(truth):
            if truth_index not in matched_truth:
                cases.append((path.name, NAMES[class_id], "missed", ""))
        for prediction_index, (class_id, _, confidence) in enumerate(predictions):
            if prediction_index not in matched_predictions:
                cases.append((path.name, NAMES[class_id], "unmatched_prediction", f"{confidence:.4f}"))
    out = ROOT / "runs" / args.dataset_name / "failure_cases.csv"
    with out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("image", "class", "kind", "confidence"))
        writer.writerows(cases)
    summary = {kind: dict(Counter(class_name for _, class_name, row_kind, _ in cases if row_kind == kind))
               for kind in ("missed", "unmatched_prediction")}
    (out.parent / "failure_cases_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

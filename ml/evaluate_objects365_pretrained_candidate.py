"""Research-only paired diagnostic for the official YOLO26n Objects365 checkpoint.

Uses an isolated Ultralytics 8.4.0 package in ml/pretrained/.runtime, leaving the
project's pinned 8.3.0 installation and all prior experiment outputs untouched.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml/pretrained/.runtime"))

from ultralytics import YOLO  # noqa: E402

from coco_vehicle_external_qa import iou  # noqa: E402
from evaluate_v11_reviewed_640_candidate import selection  # noqa: E402


DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
RUN = ROOT / "runs/public_phase1_v11_reviewed_640_candidate"
WEIGHTS = ROOT / "ml/pretrained/yolo26n-objv1-150.pt"
OUT = RUN / "objects365_pretrained_comparison_512.json"
CLASSES = {
    0: ("Person", "person"),
    1: ("Chair", "chair"),
    3: ("Car", "car"),
    4: ("Bicycle", "bicycle"),
    7: ("Motorcycle", "motorcycle"),
}


def match(predictions, truth):
    pairs = sorted(
        ((iou(pred, gt), pi, gi) for pi, pred in enumerate(predictions)
         for gi, gt in enumerate(truth)),
        reverse=True,
    )
    used_pred, used_truth = set(), set()
    for score, pi, gi in pairs:
        if score < 0.5:
            break
        if pi not in used_pred and gi not in used_truth:
            used_pred.add(pi)
            used_truth.add(gi)
    return len(used_truth)


def boxes_for(result, class_id):
    return [list(map(float, box.xyxy[0].tolist())) for box in result.boxes
            if int(box.cls[0]) == class_id]


def evaluate_public(model, class_ids, rows):
    counts = Counter()
    detected = Counter()
    details = []
    for index, row in enumerate(rows, 1):
        image = DATA / "images/test" / f'{row["id"]}.jpg'
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["sha256"]
        result = model.predict(str(image), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        labels = [line.split() for line in (DATA / "labels/test" / f'{row["id"]}.txt')
                  .read_text(encoding="utf-8").splitlines() if line.strip()]
        item = {"id": row["id"]}
        for cls, (_, name) in CLASSES.items():
            pred = boxes_for(result, class_ids[cls])
            truth = []
            for label in labels:
                if int(label[0]) == cls:
                    xc, yc, w, h = map(float, label[1:5])
                    truth.append([(xc - w / 2) * width, (yc - h / 2) * height,
                                  (xc + w / 2) * width, (yc + h / 2) * height])
            for suffix, number in (("gt", len(truth)), ("pred", len(pred)),
                                   ("matched", match(pred, truth))):
                counts[f"{name}_{suffix}"] += number
                item[f"{name}_{suffix}"] = number
        for box in result.boxes:
            detected[model.names[int(box.cls[0])]] += 1
        details.append(item)
        if index % 100 == 0:
            print(f"Objects365 {index}/{len(rows)}", flush=True)
    return {"counts": dict(counts), "detected_class_counts": dict(detected),
            "rows": details}


def evaluate_small_bicycle(model, class_id):
    rows, checksums, _, _ = selection("small_bicycle")
    counts = Counter()
    for row in rows:
        image_id = row["image_id"]
        image = ROOT / "data/source/oi_vehicle_v10/images/test" / f"{image_id}.jpg"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == checksums[image_id]
        result = model.predict(str(image), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        pred = boxes_for(result, class_id)
        truth = [[(xc - w / 2) * width, (yc - h / 2) * height,
                  (xc + w / 2) * width, (yc + h / 2) * height]
                 for category, xc, yc, w, h in row["boxes"] if category == 4]
        counts["bicycle_gt"] += len(truth)
        counts["bicycle_pred"] += len(pred)
        counts["bicycle_matched"] += match(pred, truth)
    return dict(counts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Smoke-test image limit; 0 runs all")
    args = parser.parse_args()
    assert WEIGHTS.exists(), WEIGHTS
    model = YOLO(str(WEIGHTS))
    class_ids = {}
    for cls, (source_name, _) in CLASSES.items():
        ids = [index for index, name in model.names.items()
               if name.casefold() == source_name.casefold()]
        assert len(ids) == 1, (source_name, ids, list(model.names.items())[:8])
        class_ids[cls] = ids[0]
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row["split"] == "test"]
    assert len(rows) == 620
    if args.limit:
        rows = rows[:args.limit]
    report = {
        "model": "yolo26n-objv1-150.pt",
        "weights_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
        "ultralytics_version": "8.4.0",
        "images": len(rows),
        "imgsz": 512,
        "conf": 0.25,
        "iou": 0.5,
        "class_mapping": {CLASSES[cls][1]: model.names[model_id]
                          for cls, model_id in class_ids.items()},
        "unmapped_project_classes": ["stairs", "electrical_pole", "plant_pot"],
        "limitations": "Reused public development set with incomplete source labels; extra-class counts are predictions, not validated detections. No phone or campus test.",
        "public_test": evaluate_public(model, class_ids, rows),
    }
    if not args.limit:
        report["small_bicycle"] = evaluate_small_bicycle(model, class_ids[4])
        OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"images": len(rows), "counts": report["public_test"]["counts"],
                      "small_bicycle": report.get("small_bicycle"),
                      "output": str(OUT) if not args.limit else None}, indent=2))


if __name__ == "__main__":
    main()

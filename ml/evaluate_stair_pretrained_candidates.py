"""Paired research diagnostic for project stairs versus prompt-free YOLOE stairs.

The reused public test labels are imperfect, so matched boxes and predictions on
zero-stair-label images are triage signals, not field recall or false-positive rates.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml/pretrained/.runtime"))

from ultralytics import YOLO, YOLOE  # noqa: E402

from coco_vehicle_external_qa import iou  # noqa: E402


DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
RUN = ROOT / "runs/public_phase1_v11_reviewed_640_candidate"
WEIGHTS = {
    "v11": RUN / "yolov8n/weights/best.pt",
    "yoloe26n_prompt_free": ROOT / "ml/pretrained/yoloe-26n-seg-pf.pt",
}
OUT = RUN / "stair_pretrained_comparison_512.json"


def match(predictions, truth):
    pairs = sorted(((iou(pred, gt), pi, gi)
                    for pi, pred in enumerate(predictions)
                    for gi, gt in enumerate(truth)), reverse=True)
    used_pred, used_truth = set(), set()
    for score, pi, gi in pairs:
        if score < 0.5:
            break
        if pi not in used_pred and gi not in used_truth:
            used_pred.add(pi)
            used_truth.add(gi)
    return len(used_truth)


def stair_truth(image_id, width, height):
    labels = (DATA / "labels/test" / f"{image_id}.txt").read_text(encoding="utf-8")
    truth = []
    for line in labels.splitlines():
        cls, xc, yc, w, h = map(float, line.split()[:5])
        if int(cls) == 2:
            truth.append([(xc - w / 2) * width, (yc - h / 2) * height,
                          (xc + w / 2) * width, (yc + h / 2) * height])
    return truth


def evaluate(model, name, rows, class_ids):
    counts = Counter()
    details = []
    for index, row in enumerate(rows, 1):
        image = DATA / "images/test" / f'{row["id"]}.jpg'
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["sha256"]
        result = model.predict(str(image), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        truth = stair_truth(row["id"], width, height)
        pred = [list(map(float, box.xyxy[0].tolist())) for box in result.boxes
                if int(box.cls[0]) in class_ids]
        matched = match(pred, truth)
        counts["gt_boxes"] += len(truth)
        counts["pred_boxes"] += len(pred)
        counts["matched_boxes"] += matched
        counts["positive_images"] += bool(truth)
        counts["positive_images_with_prediction"] += bool(truth) and bool(pred)
        counts["zero_label_images"] += not truth
        counts["zero_label_images_with_prediction"] += not truth and bool(pred)
        details.append({"id": row["id"], "gt": len(truth), "pred": len(pred),
                        "matched": matched})
        if index % 100 == 0:
            print(f"{name} {index}/{len(rows)}", flush=True)
    return {"counts": dict(counts), "rows": details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Smoke-test image limit; 0 runs all")
    args = parser.parse_args()
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row["split"] == "test"]
    assert len(rows) == 620
    if args.limit:
        rows = rows[:args.limit]
    report = {"images": len(rows), "imgsz": 512, "conf": 0.25,
              "matching_iou": 0.5, "models": {},
              "limitations": "Reused public development images and potentially incomplete/inconsistent staircase labels; no independent or phone validation."}
    for name, weights in WEIGHTS.items():
        assert weights.exists(), weights
        model = YOLOE(str(weights)) if name.startswith("yoloe") else YOLO(str(weights))
        class_names = {"stairs", "stair", "stairwell"} if name.startswith("yoloe") else {"stairs"}
        class_ids = {index for index, value in model.names.items()
                     if value.casefold() in class_names}
        assert class_ids, (name, class_ids)
        report["models"][name] = {
            "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
            "selected_class_names": {str(index): model.names[index] for index in class_ids},
            **evaluate(model, name, rows, class_ids),
        }
    if not args.limit:
        OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({name: item["counts"] for name, item in report["models"].items()}, indent=2))


if __name__ == "__main__":
    main()

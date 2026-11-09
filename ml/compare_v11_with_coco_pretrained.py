"""Paired shared-class diagnostic for v11 versus its original COCO weights."""

import hashlib
import json
from collections import Counter

from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from evaluate_v11_reviewed_640_candidate import RUN, selection
from phase1 import ROOT


DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
OUT = RUN / "coco_pretrained_comparison_512.json"
CLASSES = {0: (0, "person"), 1: (56, "chair"), 3: (2, "car"),
           4: (1, "bicycle"), 7: (3, "motorcycle")}
WEIGHTS = {"v11": RUN / "yolov8n/weights/best.pt", "coco_pretrained": ROOT / "notebooks/yolov8n.pt"}


def match(pred, truth):
    pairs = sorted(((iou(p, g), pi, gi) for pi, p in enumerate(pred)
                    for gi, g in enumerate(truth)), reverse=True)
    used_pred, used_truth = set(), set()
    for score, pi, gi in pairs:
        if score < 0.5:
            break
        if pi not in used_pred and gi not in used_truth:
            used_pred.add(pi)
            used_truth.add(gi)
    return len(used_truth)


def evaluate(model, variant, rows):
    counts = Counter()
    details = []
    for index, row in enumerate(rows, 1):
        path = DATA / "images/test" / f'{row["id"]}.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        result = model.predict(str(path), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        label_path = DATA / "labels/test" / f'{row["id"]}.txt'
        labels = [line.split() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        item = {"id": row["id"]}
        for cls, (coco_cls, name) in CLASSES.items():
            model_cls = cls if variant == "v11" else coco_cls
            pred = [list(map(float, box.xyxy[0].tolist())) for box in result.boxes if int(box.cls[0]) == model_cls]
            truth = []
            for label in labels:
                if int(label[0]) != cls:
                    continue
                xc, yc, w, h = map(float, label[1:5])
                truth.append([(xc - w / 2) * width, (yc - h / 2) * height,
                              (xc + w / 2) * width, (yc + h / 2) * height])
            matched = match(pred, truth)
            for suffix, number in (("gt", len(truth)), ("pred", len(pred)), ("matched", matched)):
                counts[f"{name}_{suffix}"] += number
                item[f"{name}_{suffix}"] = number
        details.append(item)
        if index % 100 == 0:
            print(f"{variant} {index}/{len(rows)}", flush=True)
    return {"counts": dict(counts), "rows": details}


def evaluate_small(model, variant):
    rows, checksums, _, _ = selection("small_bicycle")
    counts = Counter()
    for row in rows:
        image_id = row["image_id"]
        path = ROOT / "data/source/oi_vehicle_v10/images/test" / f"{image_id}.jpg"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == checksums[image_id]
        result = model.predict(str(path), imgsz=512, conf=0.25, verbose=False)[0]
        height, width = result.orig_shape
        model_cls = 4 if variant == "v11" else 1
        pred = [list(map(float, box.xyxy[0].tolist())) for box in result.boxes if int(box.cls[0]) == model_cls]
        truth = [[(xc - w / 2) * width, (yc - h / 2) * height,
                  (xc + w / 2) * width, (yc + h / 2) * height]
                 for category, xc, yc, w, h in row["boxes"] if category == 4]
        counts["bicycle_gt"] += len(truth)
        counts["bicycle_matched"] += match(pred, truth)
        counts["bicycle_pred"] += len(pred)
    return dict(counts)


def main():
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row["split"] == "test"]
    assert len(rows) == 620
    report = {"images": len(rows), "imgsz": 512, "conf": 0.25, "iou": 0.5,
              "class_mapping": {name: {"v11": cls, "coco_pretrained": coco_cls}
                                for cls, (coco_cls, name) in CLASSES.items()},
              "limitations": "Paired public development diagnostic; source labels may omit objects and this does not establish independent, campus, or phone performance.",
              "models": {}}
    for name, path in WEIGHTS.items():
        assert path.exists(), path
        model = YOLO(str(path))
        report["models"][name] = {"weights_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                  "public_test": evaluate(model, name, rows),
                                  "small_bicycle": evaluate_small(model, name)}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({name: {"public_test_counts": item["public_test"]["counts"],
                             "small_bicycle": item["small_bicycle"]}
                      for name, item in report["models"].items()}, indent=2))


if __name__ == "__main__":
    main()

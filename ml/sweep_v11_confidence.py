"""Post-hoc class threshold sweep for v11 on the public development test."""

import hashlib
import json
from collections import Counter

from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from compare_v11_with_coco_pretrained import DATA, RUN, match


THRESHOLDS = (0.01, 0.05, 0.10, 0.15, 0.25, 0.40)
CLASSES = {0: "person", 4: "bicycle", 7: "motorcycle"}
OUT = RUN / "v11_confidence_sweep_512.json"


def main():
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row["split"] == "test"]
    assert len(rows) == 620
    model = YOLO(str(RUN / "yolov8n/weights/best.pt"))
    totals = {threshold: Counter() for threshold in THRESHOLDS}
    for index, row in enumerate(rows, 1):
        path = DATA / "images/test" / f'{row["id"]}.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        result = model.predict(str(path), imgsz=512, conf=min(THRESHOLDS), verbose=False)[0]
        height, width = result.orig_shape
        labels = [line.split() for line in (DATA / "labels/test" / f'{row["id"]}.txt').read_text(encoding="utf-8").splitlines() if line.strip()]
        for cls, name in CLASSES.items():
            truth = []
            for label in labels:
                if int(label[0]) != cls:
                    continue
                xc, yc, w, h = map(float, label[1:5])
                truth.append([(xc - w / 2) * width, (yc - h / 2) * height,
                              (xc + w / 2) * width, (yc + h / 2) * height])
            candidates = [(float(box.conf[0]), list(map(float, box.xyxy[0].tolist())))
                          for box in result.boxes if int(box.cls[0]) == cls]
            for threshold in THRESHOLDS:
                pred = [xyxy for confidence, xyxy in candidates if confidence >= threshold]
                matched = match(pred, truth)
                totals[threshold][f"{name}_gt"] += len(truth)
                totals[threshold][f"{name}_pred"] += len(pred)
                totals[threshold][f"{name}_matched"] += matched
                totals[threshold][f"{name}_unmatched_pred"] += len(pred) - matched
        if index % 100 == 0:
            print(f"{index}/{len(rows)}", flush=True)
    report = {"scope": "post-hoc public development test; source labels may omit objects",
              "imgsz": 512, "matching_iou": 0.5, "images": len(rows),
              "weights_sha256": hashlib.sha256((RUN / "yolov8n/weights/best.pt").read_bytes()).hexdigest(),
              "thresholds": {str(threshold): dict(totals[threshold]) for threshold in THRESHOLDS}}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["thresholds"], indent=2))


if __name__ == "__main__":
    main()

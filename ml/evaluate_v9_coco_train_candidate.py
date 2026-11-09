"""Evaluate v9 against unchanged v8 public-test labels after training."""

import json

from ultralytics import YOLO

from phase1 import ROOT


def main():
    run_root = ROOT / "runs" / "public_phase1_v9_coco_train_candidate"
    dataset = ROOT / "data" / "processed" / "public_phase1_v9_coco_train_candidate" / "dataset.yaml"
    weights = run_root / "yolov8n" / "weights" / "best.pt"
    result = YOLO(str(weights)).val(data=str(dataset), split="test", imgsz=512,
                                     batch=4, device=0, workers=0,
                                     project=str(run_root), name="public_test", exist_ok=True)
    per_class = {}
    for position, class_id in enumerate(result.box.ap_class_index):
        per_class[result.names[int(class_id)]] = {
            "precision": float(result.box.p[position]), "recall": float(result.box.r[position]),
            "mAP50": float(result.box.ap50[position]), "mAP50_95": float(result.box.ap[position])}
    summary = {"weights": str(weights), "dataset": str(dataset), "split": "test",
               "warning": "public test reused in prior design; not independent",
               "overall": {"precision": float(result.box.mp), "recall": float(result.box.mr),
                           "mAP50": float(result.box.map50), "mAP50_95": float(result.box.map)},
               "per_class": per_class}
    (run_root / "public_test_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

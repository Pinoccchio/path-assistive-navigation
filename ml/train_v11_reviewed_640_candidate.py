"""Train reviewed v11 data at 640px from the same initial YOLOv8n weights."""

import hashlib
import json
import platform

import torch
import ultralytics
from ultralytics import YOLO

from phase1 import ROOT


def main():
    dataset = ROOT / "data" / "processed" / "public_phase1_v11_reviewed_640_candidate"
    run_root = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"
    run_root.mkdir(parents=True, exist_ok=True)
    weights = ROOT / "notebooks" / "yolov8n.pt"
    env = {"python": platform.python_version(), "torch": torch.__version__,
           "ultralytics": ultralytics.__version__, "cuda_available": torch.cuda.is_available(),
           "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
           "seed": 42, "epochs": 12, "batch": 4, "imgsz": 640,
           "initial_weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
           "dataset_manifest_sha256": hashlib.sha256((dataset / "dataset_manifest.jsonl").read_bytes()).hexdigest(),
           "changes_from_v10": "seven quarantined train images and 640px training instead of 512px; validation/test unchanged"}
    (run_root / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    YOLO(str(weights)).train(data=str(dataset / "dataset.yaml"), epochs=12, imgsz=640,
                             batch=4, seed=42, deterministic=True,
                             device=0 if torch.cuda.is_available() else "cpu", workers=0,
                             project=str(run_root), name="yolov8n", exist_ok=True)


if __name__ == "__main__":
    main()

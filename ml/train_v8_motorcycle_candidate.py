"""Train the audited eight-class candidate with v7's 12-epoch settings."""

import hashlib
import json
import platform

import torch
import ultralytics
from ultralytics import YOLO

from phase1 import ROOT


def main():
    dataset = ROOT / "data" / "processed" / "public_phase1_v8_motorcycle_candidate"
    run_root = ROOT / "runs" / "public_phase1_v8_motorcycle_candidate"
    run_root.mkdir(parents=True, exist_ok=True)
    weights = ROOT / "notebooks" / "yolov8n.pt"
    env = {"python": platform.python_version(), "torch": torch.__version__,
           "ultralytics": ultralytics.__version__, "cuda_available": torch.cuda.is_available(),
           "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
           "seed": 42, "epochs": 12, "batch": 4, "imgsz": 512,
           "initial_weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
           "dataset_manifest_sha256": hashlib.sha256((dataset / "dataset_manifest.jsonl").read_bytes()).hexdigest()}
    (run_root / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    YOLO(str(weights)).train(data=str(dataset / "dataset.yaml"), epochs=12, imgsz=512,
                             batch=4, seed=42, deterministic=True,
                             device=0 if torch.cuda.is_available() else "cpu", workers=0,
                             project=str(run_root), name="yolov8n", exist_ok=True)


if __name__ == "__main__":
    main()

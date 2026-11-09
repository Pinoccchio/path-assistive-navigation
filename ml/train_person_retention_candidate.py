"""Controlled YOLOv8n retrain after excluding unreviewed new OI training images."""

import hashlib
import json
import platform

import torch
import ultralytics
from ultralytics import YOLO
from ultralytics.utils import SETTINGS

from phase1 import ROOT


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dataset = ROOT / "data/processed/public_phase1_person_retention_candidate"
    run_root = ROOT / "runs/public_phase1_person_retention_candidate"
    weights = ROOT / "notebooks/yolov8n.pt"
    assert dataset.joinpath("build_report.json").exists()
    assert weights.exists()
    if run_root.joinpath("yolov8n_local/weights/best.pt").exists():
        raise SystemExit("Candidate checkpoint already exists; refusing to overwrite")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA unavailable; refusing an accidental multi-hour CPU run")
    run_root.mkdir(parents=True, exist_ok=True)
    environment = {
        "purpose": "Controlled public-data person-retention diagnostic; no app promotion",
        "python": platform.python_version(), "torch": torch.__version__,
        "ultralytics": ultralytics.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "seed": 42, "epochs": 12, "batch": 4, "imgsz": 640,
        "initial_weights_sha256": sha256(weights),
        "dataset_manifest_sha256": sha256(dataset / "dataset_manifest.jsonl"),
        "dataset_build_report_sha256": sha256(dataset / "build_report.json"),
        "comparison": "Same initial weights and training recipe as v11; removes the 290 new OI images, quarantines four ambiguous stair images, and applies four stair-label corrections. Effects cannot be attributed to one factor.",
        "optional_external_loggers": "disabled in this process only; no global Ultralytics settings persisted",
    }
    (run_root / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    # SettingsManager persists ordinary assignments outside this workspace.
    # Bypass only its disk-writing wrapper for this process's integration flags.
    for key in ("wandb", "comet", "dvc", "mlflow", "neptune", "raytune", "hub"):
        dict.__setitem__(SETTINGS, key, False)
    YOLO(str(weights)).train(data=str(dataset / "dataset.yaml"), epochs=12, imgsz=640,
                             batch=4, seed=42, deterministic=True, device=0,
                             workers=0, project=str(run_root), name="yolov8n_local",
                             exist_ok=False)


if __name__ == "__main__":
    main()

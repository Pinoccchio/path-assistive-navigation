"""Train and evaluate a provisional scene-screened public dataset."""

import argparse
import json
import platform
from pathlib import Path

import torch
from ultralytics import YOLO, __version__ as ultralytics_version

from phase1 import ROOT, sha256


DATA = ROOT / "data" / "processed" / "public_phase1_v2_screened"
RUN = ROOT / "runs" / "public_phase1_v2_screened"


def train():
    RUN.mkdir(parents=True, exist_ok=True)
    manifest = DATA / "dataset_manifest.jsonl"
    environment = {"python": platform.python_version(), "torch": torch.__version__,
                   "cuda_available": torch.cuda.is_available(), "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                   "ultralytics": ultralytics_version, "seed": 42, "epochs": 12, "batch": 4, "imgsz": 512,
                   "dataset_manifest_sha256": sha256(manifest.read_bytes()),
                   "initial_weights_sha256": sha256((ROOT / "notebooks" / "yolov8n.pt").read_bytes())}
    (RUN / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    model = YOLO(str(ROOT / "notebooks" / "yolov8n.pt"))
    model.train(data=str(DATA / "dataset.yaml"), epochs=12, imgsz=512, batch=4,
                seed=42, deterministic=True, device=0, workers=2,
                project=str(RUN), name="yolov8n", exist_ok=True)


def evaluate(weights_override=None, report_tag=""):
    weights = Path(weights_override) if weights_override else RUN / "yolov8n" / "weights" / "best.pt"
    model = YOLO(str(weights))
    result = model.val(data=str(DATA / "dataset.yaml"), split="test", imgsz=512,
                       batch=4, device=0, project=str(RUN),
                       name="public_test" + (f"_{report_tag}" if report_tag else ""), exist_ok=False)
    by_index = {}
    for position, class_id in enumerate(result.box.ap_class_index):
        by_index[int(class_id)] = {"precision": float(result.box.p[position]),
                                   "recall": float(result.box.r[position]),
                                   "map50": float(result.box.ap50[position]),
                                   "map50_95": float(result.box.ap[position])}
    report = {"model": DATA.name, "weights": str(weights),
              "test_split": str(DATA / "images" / "test"),
              "warning": "Provisional public split; known v1 exposure and incomplete manual semantic review prevent independent accuracy claims",
              "overall": {key: float(value) for key, value in result.results_dict.items()},
              "per_class": {name: by_index.get(index) for index, name in result.names.items()}}
    out = RUN / ("public_test_summary" + (f"_{report_tag}" if report_tag else "") + ".json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("train", "evaluate"))
    parser.add_argument("--dataset-name", default="public_phase1_v2_screened")
    parser.add_argument("--weights", default=None, help="Evaluate a specified checkpoint on this dataset")
    parser.add_argument("--report-tag", default="", help="Suffix for evaluation artifacts")
    args = parser.parse_args()
    DATA = ROOT / "data" / "processed" / args.dataset_name
    RUN = ROOT / "runs" / args.dataset_name
    if args.command == "train":
        if args.weights or args.report_tag:
            parser.error("--weights and --report-tag apply only to evaluate")
        train()
    else:
        evaluate(args.weights, args.report_tag)

"""Windows fallback export without the unavailable tflite-support wheel.

Converts YOLOv8n -> ONNX -> TFLite with onnx2tf. Model metadata is stored in
an adjacent JSON file because the legacy Ultralytics exporter cannot embed
TFLite metadata on this Windows environment.
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path

import numpy as np
import onnx  # Load its Windows DLL before pyarrow/TensorFlow initialize.
from PIL import Image

from phase1 import ROOT, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v1")
    parser.add_argument("--weights", default=None)
    parser.add_argument("--run-name", default=None,
                        help="Run directory under runs/; defaults to dataset name")
    args = parser.parse_args()
    dataset = ROOT / "data" / "processed" / args.dataset_name
    weights = Path(args.weights) if args.weights else ROOT / "runs" / args.dataset_name / "yolov8n" / "weights" / "best.pt"

    import onnx2tf
    from ultralytics import YOLO

    # onnx2tf downloads a fixed sample array even for FP32 conversion. Supply
    # local public-training images so export remains reproducible offline.
    train_images = sorted((dataset / "images" / "train").glob("*"))[:20]
    if not train_images:
        raise SystemExit("No training images available for local export samples")
    samples = []
    for path in train_images:
        with Image.open(path) as source:
            samples.append(np.asarray(source.convert("RGB").resize((128, 128)), dtype=np.float32) / 255.0)
    sample_batch = np.stack(samples)
    importlib.import_module("onnx2tf.onnx2tf").download_test_image_data = lambda: sample_batch

    model = YOLO(str(weights))
    onnx_path = Path(model.export(format="onnx", imgsz=512, batch=1, simplify=True, opset=13))
    output_dir = ROOT / "runs" / (args.run_name or args.dataset_name) / "tflite_fp32"
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"Export directory already contains files: {output_dir}")
    onnx2tf.convert(input_onnx_file_path=str(onnx_path), output_folder_path=str(output_dir),
                    not_use_onnxsim=True, verbosity="error", disable_group_convolution=True,
                    enable_batchmatmul_unfold=True)
    files = sorted(output_dir.rglob("*float32*.tflite"))
    if not files:
        files = sorted(output_dir.rglob("*.tflite"))
    if not files:
        raise SystemExit(f"No TFLite file generated in {output_dir}")
    chosen = files[0]
    metadata = {"format": "tflite_fp32", "file": str(chosen), "sha256": sha256(chosen.read_bytes()),
                "source_weights": str(weights), "source_weights_sha256": sha256(weights.read_bytes()),
                "source_onnx": str(onnx_path),
                "class_names": [model.names[index] for index in range(len(model.names))],
                "input_size": 512,
                "test_dataset": str(dataset / "dataset.yaml"),
                "status": "desktop_export_only_prediction_parity_and_phone_testing_pending"}
    record = output_dir / "model_metadata.json"
    record.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(record)


if __name__ == "__main__":
    main()

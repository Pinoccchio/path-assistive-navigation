"""Compare the FP32 TFLite export with its ONNX source on held-out images."""

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import tensorflow as tf
from PIL import Image

from phase1 import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v1")
    parser.add_argument("--weights-run-name", default="yolov8n")
    args = parser.parse_args()
    base = ROOT / "runs" / args.dataset_name
    dataset = ROOT / "data" / "processed" / args.dataset_name
    onnx = ort.InferenceSession(str(base / args.weights_run_name / "weights" / "best.onnx"), providers=["CPUExecutionProvider"])
    tflite = tf.lite.Interpreter(model_path=str(base / "tflite_fp32" / "best_float32.tflite"))
    tflite.allocate_tensors()
    input_index = tflite.get_input_details()[0]["index"]
    output_index = tflite.get_output_details()[0]["index"]
    images = sorted((dataset / "images" / "test").glob("*"))[:10]
    if len(images) < 10:
        raise SystemExit("Need ten held-out test images")
    results = []
    for path in images:
        with Image.open(path) as source:
            array = np.asarray(source.convert("RGB").resize((512, 512)), dtype=np.float32) / 255.0
        nchw = np.transpose(array, (2, 0, 1))[None]
        expected = onnx.run(None, {onnx.get_inputs()[0].name: nchw})[0]
        tflite.set_tensor(input_index, array[None])
        tflite.invoke()
        actual = tflite.get_tensor(output_index)
        difference = np.abs(expected - actual)
        results.append({"image": path.name, "max_abs_error": float(difference.max()),
                        "mean_abs_error": float(difference.mean()),
                        "all_finite": bool(np.isfinite(actual).all())})
    summary = {"images": len(results), "max_abs_error": max(x["max_abs_error"] for x in results),
               "mean_abs_error": float(np.mean([x["mean_abs_error"] for x in results])),
               "all_finite": all(x["all_finite"] for x in results), "samples": results}
    target = base / "tflite_fp32" / "parity.json"
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    metadata_path = base / "tflite_fp32" / "model_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "desktop_raw_output_parity_checked_phone_testing_pending"
    metadata["parity_report"] = str(target)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "samples"}, indent=2))


if __name__ == "__main__":
    main()

# Thesis formula validation

These are proposed mathematical contracts for the formulas review dated 2026-11-10. They are separate from Flutter and do not establish field accuracy or validate every method mentioned in the source document.

Run the standard-library numerical checks from the thesis root:

```powershell
.venv/Scripts/python.exe -m unittest discover -s qa/formulas -p test_*.py -v
```

The tests cover boundary conditions, invalid values, quantization arithmetic, relative-depth normalization, score bounds, hysteresis state, approximate approach time, agreement and SUS scoring. Two counterexamples show why scene-relative percentiles cannot establish metric distance and why direction must use unletterboxed coordinates. These tests validate the review reference functions, not the current Dart implementation.

Optional bounded model integrity check, using the existing TensorFlow, ONNX Runtime, NumPy and Pillow environment:

```powershell
.venv/Scripts/python.exe qa/formulas/check_model_artifacts.py
```

This hashes existing artifacts and compares ten raw ONNX/TFLite outputs on reused development images. It saves `model_validation_2026-11-10.json`, without changing models or historical reports. Direct square resizing intentionally matches the old export-parity procedure; it does not test camera YUV conversion, letterboxing, postprocessing, detection quality or phone latency. The chosen raw-output tolerance is a smoke-check criterion.

Before integration, port the accepted contracts into production Dart and execute the same cases against that code. Add recorded-scene tests for calibration and ranking, and device tests for capture-to-feedback latency, cancellation, accessibility and stability. No new model training or phone sessions were performed by this review.

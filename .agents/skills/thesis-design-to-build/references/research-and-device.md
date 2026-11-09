# Research, model, and device checks

## Evidence and code map

- `apps/mobile/lib/main.dart`: current UI and session lifecycle.
- `apps/mobile/lib/detector.dart`: preprocessing, inference, decoding and transforms.
- `apps/mobile/lib/detection_overlay.dart`: overlay placement.
- `apps/mobile/test/`: existing transform/widget checks and visual baseline.
- `apps/mobile/assets/model/model_metadata.json`: bundled checkpoint provenance, class order, checksum, preprocessing/export details; read actual contents before changing anything.
- `ml/README.md`, relevant `ml/PHASE1_*_STATUS.md`, `ml/PUBLIC_LABEL_POLICY.md`: experiment lineage and current label conventions.
- `ml/CAMPUS_CAPTURE_GUIDE.md`: independent campus data collection.
- `runs/` and `data/processed/`: recorded results, dataset manifests, parity and audit reports.

At skill creation, the guides describe an eight-class FP32 TFLite detection-only prototype: person, chair, stairs, car, bicycle, electrical pole, plant pot, motorcycle. Recheck metadata rather than hardcoding this map elsewhere. The current implementation uses Flutter camera and a TFLite inference isolate, samples at most once per 500ms, and skips overlapping work. Speech, vibration, distance, GPS, and route navigation are not implied by existing boxes or by the Figma design.

## App and model correctness

When changing camera/model behavior, verify image rotation, channel ordering, normalization, input shape, letterbox offsets, inverse coordinate transforms, clipping, class mapping, confidence filtering, and NMS where affected. Preserve one-frame backpressure and release resources on Stop, app pause, or failure. Do not let delayed inference revive a stopped session.

Model replacements require explicit provenance and checksum, matching class metadata, reproducible export, and parity evidence. Raw-output parity on desktop is distinct from detection-level parity and live-phone camera correctness. Keep FP32 and INT8 evidence separate; calibration must use appropriate training/validation samples rather than test data.

## Experiments and claims

Inspect saved reports without rerunning notebook acquisition/training cells. For requested retraining/builds, use new versioned output names, preserve source annotations and historical runs, and record dataset/model/config/seed/environment lineage. Audit duplicates, split leakage, class completeness and label policy before interpreting metrics. Do not overwrite an evaluated dataset or silently repair its test annotations.

Compare candidate and baseline on the same disclosed evaluation set. Reused public-test results are development evidence, not independent generalization, campus performance, phone accuracy, or safety percentages. Report per-class failures and known tradeoffs; overall mAP cannot conceal weak critical classes. Treat unresolved image/model redistribution rights as a release concern; do not broaden an internal experiment into public publication by default.

Distance/proximity, feedback priority, and participant study work follow the relevant PRD phase gates. Read exact current criteria; do not copy a target into achieved results. Relative depth does not establish metric distance, no detection means unknown, and mockup SAFE text does not establish a clear route. Stop must cancel pending feedback when feedback is introduced. Preserve the supervised research scope and approved study/ethics boundaries.

## Verification appropriate to the change

From `apps/mobile`, use focused `dart format` checks, `flutter analyze`, and relevant `flutter test` targets. Use deterministic fixtures for transform/state logic; inspect visual output rather than accepting file names or a changed golden as proof. Routine typography edits do not require retraining a model or replaying every historical experiment.

For phone QA, agree the requested scope and keep physical results distinct: device/build, mount geometry, permission outcomes, Start/Stop, lifecycle, offline behavior, camera alignment, performance/thermal behavior, text scaling and TalkBack. Processing time in the overlay excludes other stages unless explicitly instrumented; a 500ms sampling interval is not measured 500ms end-to-end feedback latency. Record actual p50/p95 with stage definitions when latency is in scope.

The user normally runs `flutter run`. Do not automatically launch it or install/debug on their phone. When device work has not been delegated, provide precise steps and record pending checks. Do not claim speaker, haptic, battery, thermal, or mobility behavior from desktop tests.

# Phase 1A public-data status

**Date:** 2026-09-28  
**Stage:** Public-data acquisition and detector training. Campus capture and independent campus testing remain pending.

**QA update:** The [full Phase 1 QA report](PHASE1_QA_REPORT.md) confirmed train/test same-scene leakage and class-label errors. The 0.702 public-test mAP50 below is retained as a historical debugging result, **not an independent accuracy estimate** or readiness claim. See the screened v3 follow-up below; manual correction and independent campus testing remain required.

**Follow-up:** The [v3 screened research run](PHASE1_V3_STATUS.md) is complete. It removed known bad examples and screened dHash/pHash train/test overlaps, then retrained and exported FP32 TFLite. Its own remaining annotation and campus-test gaps are documented there.

## Dataset v1

The [processed dataset](../data/processed/public_phase1_v1/dataset.yaml) contains 3,075 training, 290 validation, and 588 public-test images after the generated pilot copies with invalid boxes were removed. The [build report](../data/processed/public_phase1_v1/build_report.json) and [manifest](../data/processed/public_phase1_v1/dataset_manifest.jsonl) record counts, sources, checksums, and duplicate filtering. Source manifests are under `data/source/rod_public_phase1/` and `data/source/oi_public_phase1/`.

The source set combines ROD seven-class images with an Open Images V7 supplement for person, chair, stairs, car, and bicycle. The Open Images manifest retains the listed CC BY 2.0 image license, author, and original landing page for each selected image. Original-image license verification and ROD underlying-source rights review are still pending; keep image and model artifacts internal to the thesis team.

The [Ultralytics model license](https://www.ultralytics.com/license) also requires a release decision before the model is bundled in a public app.

| Class | Train images | Validation images | Public-test images | Public-test capture groups |
| --- | ---: | ---: | ---: | ---: |
| person | 731 | 70 | 124 | 89 |
| chair | 521 | 51 | 112 | 67 |
| stairs | 442 | 54 | 128 | 61 |
| car | 779 | 64 | 132 | 67 |
| bicycle | 324 | 54 | 60 | 45 |
| electrical pole | 165 | 17 | 33 | 12 |
| plant pot | 197 | 9 | 24 | 9 |

The build rejected 894 duplicate or near-duplicate candidates. A post-build audit removed 57 generated pilot copies with no valid boxes and removed invalid boxes from three retained copies; the historical pilot remains untouched. The current `audit` command reports zero invalid labels. The [stairs and poles review queue](../data/processed/public_phase1_v1/stairs_and_poles_review.csv) contains 839 images pending manual semantic review. The low number of independent pole and plant-pot scenes prevents strong per-class reliability claims, even when box-level metrics are reported.

## Model and remaining gates

A 12-epoch YOLOv8n candidate is trained at [`runs/public_phase1_v1/yolov8n/`](../runs/public_phase1_v1/yolov8n/). On the untouched 588-image public test split, its mAP50 is **0.702** (historical pilot: **0.652**) and mAP50-95 is **0.490** (pilot: **0.446**). Candidate per-class mAP50: person 0.666, chair 0.726, stairs 0.673, car 0.770, bicycle 0.700, electrical pole 0.574, plant pot 0.803. See the [candidate summary](../runs/public_phase1_v1/public_test_candidate_summary.json), [pilot summary](../runs/public_phase1_v1/public_test_pilot_summary.json), and [failure-case summary](../runs/public_phase1_v1/failure_cases_summary.json). The candidate missed 114 annotated people and 67 staircases at the recorded failure-case threshold; these counts need review alongside incomplete-label checks.

FP32 TFLite export succeeded at [`runs/public_phase1_v1/tflite_fp32/best_float32.tflite`](../runs/public_phase1_v1/tflite_fp32/best_float32.tflite). A raw-output comparison with ONNX across ten held-out public-test images found mean absolute error 0.0000105 and maximum absolute error 0.00133; [parity details](../runs/public_phase1_v1/tflite_fp32/parity.json) are recorded. This compares model tensors on a desktop and does not establish detection-level parity, phone latency, or field safety. INT8 export and calibration remain pending.

Campus capture, consent/permission, annotation, independent campus test, on-device latency, and supervised walking evidence are still outside this public-data stage.

## Visual QA spot check

On 2026-09-28, inference was run on 14 held-out public-test examples (two selected by manifest order per class). The [contact sheet](../runs/public_phase1_v1/visual_qa_sheet.jpg) overlays green ground-truth boxes and red model predictions. The model visibly produced detections for several cars, bicycles, chairs, people, and pots. This spot check also exposed label-definition problems: one `stairs` example shows an escalator; two `electrical_pole` examples show pedestrian-crossing posts rather than clear utility poles; one `plant_pot` example is a bare pot. These examples conflict with the frozen annotation guide above. Do not treat this spot check as a pass for the safety use case. Review and correct source labels with an auditable new dataset version before reporting final class performance; leave the frozen public test split unchanged for this run.

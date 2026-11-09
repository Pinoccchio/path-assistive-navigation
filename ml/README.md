# Phase 1 public-data workflow

The latest trained experiment is the [person-retention candidate](PHASE1_PERSON_RETENTION_CANDIDATE_STATUS.md), which is bundled in the Flutter app for **technical detection testing only**. It improves person matches against the [v11 research baseline](PHASE1_V11_STATUS.md) on the reused public test, but bicycle and motorcycle matches fall; it is not cleared for navigation alerts. The [v18 person-label review backlog](PHASE1_V18_PARTIAL_PERSON_AUDIT_STATUS.md), built from the [v16 quarantine](PHASE1_V16_PERSON_LABEL_STATUS.md) and [v17 expanded audit](PHASE1_V17_PERSON_AUDIT_STATUS.md), remains open. For a short account of the full journey, see the [team guide](../TEAM_START_HERE.md).

The earlier public-label cleanup checkpoint [v7](PHASE1_V7_STATUS.md), derived from [v6](PHASE1_V6_STATUS.md), applies the [label policy](PUBLIC_LABEL_POLICY.md) and records box removals and quarantines in its build reports. The commands below reproduce that **historical v6/v7 workflow**, not the current person-retention candidate:

```powershell
.\.venv\Scripts\python.exe ml/build_v4_curated.py --name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/audit_curated_diff.py --name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/qa_inventory.py --dataset data/processed/public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/qa_phash.py --dataset-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/build_v7_curated.py --name public_phase1_v7_vehicle_labels_candidate
.\.venv\Scripts\python.exe ml/audit_curated_diff.py --name public_phase1_v7_vehicle_labels_candidate --source-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/qa_inventory.py --dataset data/processed/public_phase1_v7_vehicle_labels_candidate
.\.venv\Scripts\python.exe ml/qa_phash.py --dataset-name public_phase1_v7_vehicle_labels_candidate
```

The builder refuses to overwrite an existing output. v3 stays frozen as the source. The intervening v4 and v5 candidates were superseded after additional validation and pole-label errors were found during their early training epochs; neither has a final evaluation.

The v6 model, public-test results, visual review sheets, and remaining label issues are recorded in the [v6 status](PHASE1_V6_STATUS.md). To repeat training and the desktop export checks for a newly named curated dataset, substitute its name in these commands:

For v7, run `train_v2_screened.py` with `--dataset-name public_phase1_v7_vehicle_labels_candidate`; use `evaluate --weights runs/public_phase1_v6_curated_candidate/yolov8n/weights/best.pt --report-tag v6_on_v7` to reproduce the frozen v6 baseline on the same corrected test labels. Do not interpret a v6-versus-v7 raw public-test score difference as independent deployment accuracy.

The [v7 status](PHASE1_V7_STATUS.md) records the final same-test comparison and hard-negative check. To repeat the latter with a checkpoint, run `ml/qa_vehicle_negatives.py --weights <checkpoint> --model-tag <tag> --dataset-name public_phase1_v7_vehicle_labels_candidate`.

```powershell
.\.venv\Scripts\python.exe ml/train_v2_screened.py train --dataset-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/train_v2_screened.py evaluate --dataset-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/failure_cases.py --dataset-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/qa_review_sheets.py --dataset-name public_phase1_v6_curated_candidate --weights runs/public_phase1_v6_curated_candidate/yolov8n/weights/best.pt --model-tag v6model
.\.venv\Scripts\python.exe ml/export_tflite_direct.py --dataset-name public_phase1_v6_curated_candidate
.\.venv\Scripts\python.exe ml/verify_tflite.py --dataset-name public_phase1_v6_curated_candidate
```

The [QA report](PHASE1_QA_REPORT.md) found train/test scene leakage and semantic-label errors in public v1. The [v3 screened experiment](PHASE1_V3_STATUS.md) is a separate, provisional public-data copy; its build and training commands are:

```powershell
.\.venv\Scripts\python.exe ml/build_v2_screened.py --name public_phase1_v3_screened --phash-distance 10
.\.venv\Scripts\python.exe ml/qa_inventory.py --dataset data/processed/public_phase1_v3_screened
.\.venv\Scripts\python.exe ml/qa_phash.py --dataset-name public_phase1_v3_screened
.\.venv\Scripts\python.exe ml/train_v2_screened.py train --dataset-name public_phase1_v3_screened
.\.venv\Scripts\python.exe ml/train_v2_screened.py evaluate --dataset-name public_phase1_v3_screened
```

The v3 builder is one-shot and refuses to overwrite an existing dataset. Only rebuild under a new version name. Read the [campus capture guide](CAMPUS_CAPTURE_GUIDE.md) before collecting the independent phone-view dataset.

The existing notebook and `runs/yolov8n_pilot/` are historical evidence. `phase1.py` creates a separate public-data experiment. Use the workspace `.venv` with `requirements-phase1.txt`; record the installed PyTorch/CUDA build separately because its wheel depends on the GPU environment.

```powershell
.\.venv\Scripts\python.exe ml/phase1.py acquire --train 3000 --val 400 --test 400
.\.venv\Scripts\python.exe ml/openimages.py --train-per-class 80 --val-per-class 20 --test-per-class 20
.\.venv\Scripts\python.exe ml/phase1.py build --include-pilot
.\.venv\Scripts\python.exe ml/phase1.py audit
.\.venv\Scripts\python.exe ml/phase1.py train --epochs 30 --batch 4 --device 0
.\.venv\Scripts\python.exe ml/phase1.py evaluate --batch 4 --device 0
.\.venv\Scripts\python.exe ml/phase1.py export
.\.venv\Scripts\python.exe ml/export_tflite_direct.py
.\.venv\Scripts\python.exe ml/verify_tflite.py
```

On this Windows environment, `phase1.py export` may fail because the legacy Ultralytics exporter requires the unavailable `tflite-support` wheel. The direct exporter uses ONNX and onnx2tf with local training-image samples, writes FP32 TFLite plus sidecar metadata, and can then be checked against ONNX with `verify_tflite.py`. Keep the FP32 and INT8 workflows separate; the direct exporter currently produces FP32 only.

Both acquisition commands are resumable and record source URLs and SHA-256 hashes. The Open Images adapter records the listed per-image license, author, and original landing page; verify the original listing before redistribution. `build` is intentionally one-shot: use a new dataset version instead of silently replacing an evaluated test set. It writes rejected-image reasons and a build report. `--include-pilot` copies the old pilot into **training only** after cross-source duplicate and invalid-box checks. Run `audit` before training; `audit --fix` may remove invalid generated copies but never changes the source or historical pilot. Hold the public test set untouched until the training choices are fixed. Its results are **public-data results**, never campus results.

The source ledger currently marks ROD's underlying source-image rights as pending. The Hugging Face card lists MIT, but the collection combines third-party datasets. Keep images and derived model internal to the thesis team until the per-source rights review is finished. Do not commit raw images or weights to a public repository by default.

The [Ultralytics YOLOv8 license](https://www.ultralytics.com/license) is another release gate: its code and trained models are offered under AGPL-3.0 or an Enterprise license. Decide the app's distribution and source-code terms before bundling the checkpoint in a public or proprietary release.

## Historical seven-class annotation guide

This section documents the original seven-class dataset. The current research checkpoint has an eighth, auxiliary `motorcycle` class; use its [model metadata](../apps/mobile/assets/model/model_metadata.json) and the [versioned label policy](PUBLIC_LABEL_POLICY.md) for the current class map and conventions.

| ID | Label | Positive box | Exclude or review |
| ---: | --- | --- | --- |
| 0 | person | Visible human body, including partial body | Poster, photo, mannequin |
| 1 | chair | Movable seat with back or chair-like seat | Bench, sofa, stool unless the source's intended class is explicitly chair |
| 2 | stairs | Visible stepped walking surface; one box around the contiguous staircase | Ramp, escalator, decorative stepped object; review upward vs downward views |
| 3 | car | Passenger car | Bus, truck, toy car |
| 4 | bicycle | Pedal bicycle | Motorcycle, scooter |
| 5 | electrical_pole | Utility pole carrying electrical/communication wires or hardware | Generic light pole, signpost, tree trunk; review every retained example |
| 6 | plant_pot | Pot/container with a plant that presents a physical obstacle | Bare pot or general vegetation unless the source definition includes it |

Use a tight box around the visible object or staircase extent, normalized YOLO `class x_center y_center width height` coordinates in `[0,1]`. A box must have positive width and height and stay inside the image. Keep multiple objects on one image. Review every stair and pole annotation manually before interpreting per-class metrics. Missing target objects in otherwise labeled scenes can create false negatives; sample multi-object images for a completeness audit. Keep original annotations and corrections traceable in the manifest.

## Public source ledger and decisions

| Source | Seven-class contribution | Rights and handling | Decision |
| --- | --- | --- | --- |
| [ROD](https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO) | Direct labels for all seven | Dataset card says MIT but combines third-party sources; underlying rights require tracing | Curated internal research set; no public redistribution yet |
| [Open Images V7](https://storage.googleapis.com/openimages/web/download_v7.html) | Boxed person, chair, stairs, car, and bicycle; no direct electrical-pole or plant-pot box class | Annotations CC BY 4.0; per-image license, author, URL, and attribution must be retained | Included as a curated five-class supplement with original-image rights still to verify |
| [COCO 2017](https://cocodataset.org/dataset/detection-2017.htm) | Person, chair, car, bicycle, potted plant | COCO does not cover stairs or electrical poles; verify individual image terms | Candidate common-class supplement, not a seven-class test by itself |
| [Mapillary Object Dataset](https://www.mapillary.com/dataset/assets/mapillary-object-dataset-research-use-license-2019.pdf) | Some street objects and poles | Research-only license restricts derivatives and public products | Excluded from app-training set pending rights review |

The intent is to survey public sources broadly, then add only data whose labels, permissions, and context suit the app. More images from one near-duplicate source do not substitute for independent campus evidence.

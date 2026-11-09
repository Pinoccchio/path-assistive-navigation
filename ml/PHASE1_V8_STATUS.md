# Public-data v8 motorcycle candidate — 2026-09-29

**Status:** Built, audited, trained for 12 epochs, and evaluated. **Do not use as an app-ready walking-assistance detector.**

The [v8 dataset](../data/processed/public_phase1_v8_motorcycle_candidate/dataset.yaml) derives from immutable v7. It adds an auxiliary `motorcycle` class from 100 visually reclassified boxes across 98 images (76 train, 8 validation, 16 test) and quarantines one training image whose stair box covers most of a person and landing. The [build report](../data/processed/public_phase1_v8_motorcycle_candidate/build_report.json) records the change; [diff audit](audit_v8_motorcycle_candidate.py) checked all 3,520 source images and found zero unexpected changes. Existing app alert taxonomy has not been changed; class 7 is only a model candidate.

The [training script](train_v8_motorcycle_candidate.py) uses the same initial YOLOv8n weights, 512-pixel input, batch 4, seed 42, and 12 epochs as v7. The [environment record](../runs/public_phase1_v8_motorcycle_candidate/environment.json) and [best checkpoint](../runs/public_phase1_v8_motorcycle_candidate/yolov8n/weights/best.pt) are saved. On the corrected but **previously exposed public test**, [v8 evaluation](../runs/public_phase1_v8_motorcycle_candidate/public_test_summary.json) gives overall precision 0.794, recall 0.713, mAP50 0.771, and mAP50-95 0.568 across eight classes. Bicycle precision 0.813, recall 0.669, mAP50 0.740; motorcycle precision 0.626, recall 0.625, mAP50 0.461. Overall metrics are not directly comparable with v7's seven-class average, and this test was used in earlier development.

An **80-image COCO val2017 holdout** was selected and downloaded before v8 training finished. It is disjoint from the first 80-image development slice by image ID, and none of its images matched the v7 project images byte-for-byte. The [frozen selection](../data/source/coco_external/selection_holdout.json) records seed `20260930`, image IDs, annotation boxes, and image SHA-256. Evaluation used confidence 0.25, image size 512, and one-to-one IoU ≥ 0.5 matching for bicycle boxes.

| Detector | Bicycle matches / 89 boxes | Bicycle precision | Motorcycle-only images with any bicycle prediction |
| --- | ---: | ---: | ---: |
| [v6](../data/source/coco_external/v6_holdout_vehicle_qa.json) | 15/89 (0.169 recall) | 0.341 | 18/40 |
| [v7](../data/source/coco_external/v7_holdout_vehicle_qa.json) | 15/89 (0.169 recall) | 0.268 | 15/40 |
| [v8](../data/source/coco_external/v8_holdout_vehicle_qa.json) | 16/89 (0.180 recall) | 0.356 | 13/40 |

Explicit motorcycle labels improved v8 slightly against v7 on this slice, but bicycle recall remains very low and 13/40 motorcycle-only images still trigger a bicycle prediction. Of 89 holdout bicycle boxes, 19 are below 32×32 pixels and 47 below 64×64 pixels at source resolution; this suggests a small-object problem as well as class confusion. The 80-image holdout is small, public, and from one source. It is a diagnostic comparison, not a safety or campus-domain assessment.

Next work should collect and visually audit a source-diverse **training** set with both bicycle and motorcycle boxes, including near-field, small, occluded, scooter, and trike cases, then retrain. Keep a newly frozen test from a different source before selecting models or thresholds; do not train on either COCO val slice in this folder. Also complete the stair geometry ledger and per-class error review. Only after those checks improve should the candidate be exported and tested end-to-end on the Infinix X6853 for detection output, latency, and alerts. Campus collection stays deferred until requested.

Dataset provenance: [COCO API](https://github.com/cocodataset/cocoapi); [annotation mirror and checksum](https://huggingface.co/datasets/LibreYOLO/coco2017). Image licenses vary by original COCO image.

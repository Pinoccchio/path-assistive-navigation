# Public-data v11 reviewed 640px candidate

## Decision

**Do not promote v11 to the Flutter app.** It is a completed, reproducible research candidate. Broad bicycle detection improved at 512px, but the main small-bicycle failure remains: only 10 of 48 boxes matched. Motorcycle detection is also weak. The public tests have already informed experiment design and cannot support an independent accuracy or safety claim. Campus capture remains deferred.

The later [paired remediation diagnostics](PHASE1_V11_REMEDIATION_STATUS.md) identify a substantial person-detection regression against the original COCO checkpoint, reject confidence lowering and crop inference as alert fixes, and reconcile the stale v11 label queue against v13.

## What changed

The [review ledger](../data/source/oi_vehicle_v10/train_review_v11.json) quarantines seven clearly out-of-policy Open Images training images: object fragments, a toy, an ATV, a newspaper depiction, and a video-game scene. The [v11 build report](../data/processed/public_phase1_v11_reviewed_640_candidate/build_report.json) records 3,302 training, 251 validation, and 620 test images; validation and test are unchanged from v10. The builder preserves the v10 source and weights. The 12-epoch run trained YOLOv8n from the same initial weights with 640px input, batch 4, and seed 42 on the RTX 3050 Laptop GPU. See [environment](../runs/public_phase1_v11_reviewed_640_candidate/environment.json) and [best checkpoint](../runs/public_phase1_v11_reviewed_640_candidate/yolov8n/weights/best.pt).

The experiment changes **both** seven training exclusions and training resolution, so any difference cannot be attributed to one factor. No extra data was downloaded for v11. The remaining Open Images training boxes have not been fully adjudicated instance by instance.

## Paired diagnostics

All counts below use confidence 0.25 and one-to-one IoU 0.5 matching. The [64-image vehicle report at 512px](../runs/public_phase1_v11_reviewed_640_candidate/oi_vehicle_comparison_512.json) and [31-image small-bicycle report at 512px](../runs/public_phase1_v11_reviewed_640_candidate/oi_small_bicycle_comparison_512.json) compare the same images with each checkpoint.

| 512px diagnostic | v9 | v10 | v11 |
| --- | ---: | ---: | ---: |
| Broad-test bicycle boxes matched | 29/43 | 30/43 | **34/43** |
| Broad-test motorcycle boxes matched | 40/74 | 37/74 | 38/74 |
| Motorcycle-only images with any bicycle prediction | 3/35 | 5/35 | 5/35 |
| Small-bicycle boxes matched | 11/48 | 11/48 | **10/48** |
| Small-bicycle images with any motorcycle prediction | 10/31 | 8/31 | 3/31 |

At 640px inference, [the vehicle report](../runs/public_phase1_v11_reviewed_640_candidate/oi_vehicle_comparison_640.json) shows v9/v10/v11 bicycle matches of 28/43, 33/43, and 32/43; motorcycle matches of 43/74, 35/74, and 34/74. [The small-bicycle report](../runs/public_phase1_v11_reviewed_640_candidate/oi_small_bicycle_comparison_640.json) shows 12/48, 10/48, and 10/48. Raising inference resolution is not a sufficient fix. The small-bicycle slice deliberately filters ground truth by size, so its prediction count cannot be used as precision; larger visible bicycles and incomplete source boxes remain in some images.

On the unchanged 620-image public test at 512px, the [v10 paired report](../runs/public_phase1_v11_reviewed_640_candidate/public_test_summary_v10_on_v11_512.json) and [v11 paired report](../runs/public_phase1_v11_reviewed_640_candidate/public_test_summary_v11_512.json) give overall mAP50 of 0.770 versus 0.772. Bicycle recall is 0.632 versus 0.705; motorcycle recall is 0.402 versus 0.435. Person recall is 0.243 versus 0.345, while chair recall is 0.726 versus 0.702 and plant-pot recall is 0.896 versus 0.875. Electrical-pole test has only six instances, so its high score is unstable. These public-data metrics are descriptive and have been repeatedly used during model development.

## Next data work

The [targeted visual and label audit](PHASE1_V11_LABEL_AUDIT.md) found 28/48 small-bicycle boxes with zero same-class prediction overlap and flagged 40 of 290 new training images for human annotation review. It includes concrete image IDs and review sheets. No source or test labels were changed by that audit.

The [51-image review queue](../runs/public_phase1_v11_reviewed_640_candidate/review_queue_512.csv) prioritizes 25 images with missed small bicycles and 12 with missed motorcycles, plus class-confusion examples. Review every bicycle and motorcycle instance and box on these images and the 290 retained new Open Images training images before another training run. Record whether each case is an incomplete annotation, wrong class, tiny object, occlusion, or true model miss. Do not edit the frozen public test labels merely to improve a score; record corrections separately and evaluate the effect transparently.

After that audit, collect **targeted** small/distant bicycle and motorcycle examples from an independently sourced, rights-reviewed dataset only for training. Lock a separate independent-source test before tuning, then measure box recall, class confusion, false alerts per scene, and latency on the Infinix X6853. Bulk Open Images downloads or blind retraining would not address the current evidence. No source files or prior checkpoints were deleted.

Reproduce the v11 dataset and diagnostics:

```powershell
.\.venv\Scripts\python.exe ml/build_v11_reviewed_640_candidate.py
.\.venv\Scripts\python.exe ml/train_v11_reviewed_640_candidate.py
.\.venv\Scripts\python.exe ml/evaluate_v11_reviewed_640_candidate.py --imgsz 512
.\.venv\Scripts\python.exe ml/evaluate_v11_reviewed_640_candidate.py --imgsz 640
.\.venv\Scripts\python.exe ml/make_v11_review_queue.py
```

The dataset builder refuses to overwrite an existing v11 build; use a new version name if rebuilding after edits.

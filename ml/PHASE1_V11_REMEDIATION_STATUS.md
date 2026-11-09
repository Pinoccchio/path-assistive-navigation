# V11 detection remediation, 2026-10-04

**Decision:** v11 is still a research checkpoint. Do not use it for navigation alerts or claim that eight labels are reliable. This round did not change model weights, public-test labels, or any app code. Campus collection remains deferred.

## What the paired diagnostics show

All box matches here use one-to-one IoU 0.5 on previously used public test data at 512px and confidence 0.25. The [same-image comparison](../runs/public_phase1_v11_reviewed_640_candidate/coco_pretrained_comparison_512.json) shows that the original COCO-pretrained YOLOv8n matches **372/510 person** boxes versus **246/510 for v11**. The person drop occurs in both Open Images (130/194 versus 58/194) and ROD (242/316 versus 188/316). V11 improves chair (125/168 versus 85/168) and broad bicycle (75/95 versus 67/95), so simply replacing v11 with the original COCO checkpoint would sacrifice other target classes and lose the three non-COCO labels.

V13 training labels contain **4,206 person boxes**, **755 motorcycle boxes**, and **1,355 bicycle boxes**. Only about **344 bicycle boxes** have an approximate short side under 40px. These counts rule out a simple total-person-count shortage, but they do not establish label completeness or domain coverage. The [balance audit](audit_v13_training_balance.py) contains source and size breakdowns.

The [confidence sweep](../runs/public_phase1_v11_reviewed_640_candidate/v11_confidence_sweep_512.json) raises person matches from 246/510 at 0.25 confidence to 314/510 at 0.10, while unmatched person predictions rise from 85 to 244. At 0.05 the figures are 350/510 and 506. Lowering confidence globally is not an acceptable navigation-alert fix.

The [crop experiment](../runs/public_phase1_v11_reviewed_640_candidate/tiled_inference_512/report.json) raises small-bicycle matches from 10/48 to 15/48, but motorcycle-only scenes with at least one bicycle prediction rise from 5/35 to 14/35. Do not enable that path in Flutter. These diagnostics are on a reused development test and cannot independently establish precision, field accuracy, or safety.

## Label-audit correction

The v11 proposal queue is **stale relative to v13**. A full-resolution review initially appeared to find an unboxed motorcycle in `b8de9ce8cb2f4d94`; the v13 label already contains the exact motorcycle box from the v12 pilot. No duplicate was added. The [reconciliation script](reconcile_v11_train_proposals_v13.py) compares all 93 old proposals against current v13 train labels. Its [CSV](../runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_proposals_reconciled_v13.csv) finds 5 already boxed, 16 overlapping another vehicle class, and 72 still requiring visual review. A `visual_review_needed` row is **not** an approved missing label: examples include a stroller, a hot-rod car, partial object boxes, and prior rejected predictions. The script writes no labels and can be rerun after each pilot version.

## Next corrective run

1. Review every visible person, bicycle, and motorcycle instance in the flagged retained Open Images training images, starting with the 72 reconciled proposals. Also inspect the remaining retained images because proposal-only review misses objects that v11 never predicts. Record accepted/rejected boxes with image hashes; compare against the latest labels before building a new dataset version.
2. Assemble a rights-reviewed, distant-bike and motorcycle training supplement only after the instance audit. Keep the 80-image COCO review batch separate until image-level rights and annotation review are completed. Do not convert predictions into labels automatically.
3. Lock an independent-source holdout before selecting a training recipe. Then run controlled training candidates that isolate data corrections and person-retention changes, comparing person recall, small-bike box recall, motorcycle/bicycle confusion, and false alerts per scene at the same threshold. The public test remains a development diagnostic only.
4. Measure latency and alert behavior on the Infinix X6853 before any Flutter integration decision. A detection box score alone does not establish safe assistive navigation.

No old dataset, checkpoint, or review artifact was deleted.

The subsequent [v14 annotation pilot](PHASE1_V14_LABEL_PILOT_STATUS.md) adds two verified motorcycle boxes and prepares whole-image review sheets for all 290 retained new Open Images training images. It does not retrain the model.

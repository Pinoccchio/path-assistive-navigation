# V11 targeted bicycle and motorcycle label audit

The v11 checkpoint remains a research candidate. This audit inspected all 13 visual sheets from the 51-image public-test failure queue and all 10 sheets from the 40 flagged retained Open Images training images. It did **not** modify frozen test labels, add model predictions as labels, or retrain.

## What the small-bicycle failure contains

The [localization diagnostic](../runs/public_phase1_v11_reviewed_640_candidate/small_bicycle_localization_diagnostic_512.json) re-ran v11 at 512px/confidence 0.25 on the 31-image, 48-box post-hoc public slice. Only 10/48 boxes reached IoU 0.5. Another five reached IoU 0.1 but not 0.5; 28 had zero same-class overlap. A same-class prediction covered the ground-truth center for 18/48 boxes, which can include a much larger bicycle box and is not a correct localization. By approximate box side at 512px, matches were **0/9 at 12–24px**, **1/15 at 24–40px**, and **9/24 at 40–64px**. This supports a real tiny-object detection gap, with additional localization and annotation-completeness issues.

The [test review sheets](../runs/public_phase1_v11_reviewed_640_candidate/review_sheets_512) show examples that need annotation adjudication before treating the scores as accuracy: `0d1902a8a0ccab84` and `4b76b35cd4d63ce3` contain crowded bicycle scenes with visibly sparse/partial source boxes; `07a23b4ca59c2c26` contains a large bicycle prediction but source boxes around separated visible parts; `97948408f6a3a476` is a cropped close-up rather than a clear full-bicycle obstacle; `10644516604217c` contains small amusement-ride motorcycles; `81ac34eb158bcc18` contains stationary exercise bicycles. The last two are candidates for out-of-policy exclusion, **not** approved test-set edits. Keep the original paired reports intact and record any later adjudicated evaluation separately.

## Training-label audit

The [automated training queue](../runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_label_audit_queue.csv) checks all **290 retained new Open Images training images** at confidence 0.4. Forty have at least one bicycle/motorcycle prediction with IoU below 0.1 against every same-class source box. This is a review trigger, not proof that all 40 have missing annotations. The [full JSON](../runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_label_audit_queue.json) records prediction boxes and confidence; the [visual sheets](../runs/public_phase1_v11_reviewed_640_candidate/train_label_audit_sheets) preserve the image context.

Visual review found several clear **candidates** for missing target-instance annotation: `29e6d25056a05f4d`, `dfc7fb40f5632b45`, `b96a89e8d5b34184`, and `b8de9ce8cb2f4d94` show cyclists in groups with only a fraction of visible bicycles boxed. `1f0413949f0d0e90`, `2097b2c1aaf55688`, and `ceff3e6b06f665a5` have bike-rack scenes with incomplete target boxing and occasional bicycle-to-motorcycle confusion. `e8a75d8f8fdd85fa`, `d5c75161e020ce88`, and `6d048a3c49d0eaaf` have crowded motorcycle scenes requiring instance-by-instance box review. `66da6f93d78d1a49` shows a scooter predicted as a motorcycle but absent from the visible source boxes. Other flags, including `8dfe66be8e71bdd6` and `5d9a76c617be9980`, need box-level adjudication before assigning a cause.

## Next controlled change

1. For the 40 flagged training images, inspect full resolution and create a separate correction ledger with exact instance boxes and class decisions. Review the other 250 retained Open Images images for missed objects too; an inference-based queue cannot find objects the model never predicts.
2. Freeze a new v12 dataset copy with only human-confirmed training corrections or exclusions. Preserve v11 images, labels, reports, and weights. Do not alter the public test during training.
3. If corrected training labels still leave 12–40px bicycles weak, acquire **targeted**, rights-reviewed distant bicycle and motorcycle training images from another source. Lock a new independent-source test before model selection. Campus collection remains deferred.
4. Compare v11 and v12 at the same inference size and confidence, including small-object box recall, bicycle/motorcycle confusion, false alerts per scene, and on-device latency on the Infinix X6853. No Flutter integration decision follows from these public tests alone.

Recreate these audit artifacts with `ml/diagnose_v11_small_boxes.py`, `ml/render_v11_review_queue.py`, `ml/audit_v11_train_vehicle_labels.py`, and `ml/render_v11_train_label_audit.py`.

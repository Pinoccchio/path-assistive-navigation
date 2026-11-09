# Phase 1 model and dataset QA — 2026-09-28

## Verdict

The seven-class detector is a **working research prototype**, but the current public-test score is **not a valid independent performance estimate**. Visual review confirmed train/test scene leakage and incorrect or inconsistent labels. Do not use the current model or its 0.702 mAP50 as evidence of safe navigation performance.

## Scope and evidence

- The [full inventory](../runs/public_phase1_v1/qa_inventory.json) checked all **3,953** processed images and labels for presence, decodability, manifest SHA-256, and class consistency. These checks found **zero file/format issues** and **zero exact-image hashes shared across splits**. The prior label-coordinate audit also found zero invalid boxes.
- The inventory found one declared capture group (`ROD:4163`) spanning validation and test. A broader dHash screen found **458 train/test candidate pairs** at distance <=13 with a shared class. That number is a *review queue*, not a count of true duplicates. The [first 40 candidate pairs](../runs/public_phase1_v1/qa_sheets/near_pairs_1.jpg) were visually reviewed across four sheets (`near_pairs_1.jpg` through `near_pairs_4.jpg`), and multiple same-scene pairs were confirmed.
- Prediction overlays were reviewed for **nine test selections per class** and **nine training selections each** for stairs, electrical pole, and plant pot: 90 class-selection tiles total. Green boxes are source annotations; red boxes are model predictions at confidence >=0.25. See the [per-class sheets](../runs/public_phase1_v1/qa_sheets/) and the earlier [14-selection sheet](../runs/public_phase1_v1/visual_qa_sheet.jpg). This is a stratified spot check, **not manual review of every image**.
- The candidate's published public-test metrics were mAP50 **0.702**, precision **0.785**, and recall **0.590** across 588 images. These numbers describe the compromised split and should not be used for deployment decisions. The [evaluation summary](../runs/public_phase1_v1/public_test_candidate_summary.json) and [failure-case summary](../runs/public_phase1_v1/failure_cases_summary.json) remain useful for debugging.
- FP32 TFLite loaded successfully; ten-image raw-output comparison with ONNX yielded mean absolute error **0.0000105** and maximum **0.00133**. This verifies desktop conversion only. Detection-level TFLite parity, camera testing, and Infinix X6853 latency were not tested.

## Confirmed high-priority defects

1. **Train/test scene leakage.** Training `pilot_train_IMG_00346` and test `rod_test_IMG_19204` are neighboring frames of the same two-person street video. Training `rod_train_IMG_07763` and test `rod_test_IMG_19874` show the same staircase. Training `pilot_train_IMG_19176` and test `rod_test_IMG_20814` show the same social-video car scene. Training `rod_train_IMG_10621` and test `rod_test_IMG_20090` show the same crossing post. The current dHash rejection threshold of four missed these. Scene-level grouping must happen before splitting and before training.
2. **Electrical-pole labels are unreliable.** Test `rod_test_IMG_20088` and training `rod_train_IMG_10612` show pedestrian-crossing button posts labeled electrical pole. Several test pole images with genuine utility poles have boxes across the road/low foreground instead of the pole itself. The test sheet makes this visible. Only **12 public-test capture groups** contain this class.
3. **Class-definition mismatches.** Test `openimagesv7_test_14fe08f87965e8a0` labels an escalator as stairs; test `rod_test_IMG_19835` labels a motorcycle as bicycle; test `rod_test_IMG_19193` labels a bare pot as plant pot. Test `rod_test_IMG_19614` labels a backless stool as chair. These conflict with the current annotation guide.
4. **Inconsistent or incomplete boxes.** Stair scenes use both one box for a staircase and multiple boxes for individual steps. Several crowded chair scenes have predictions on plausible chairs that are absent from the source annotations. The existing unmatched-prediction counts therefore mix true false alerts with missing labels.

## Per-class assessment

| Class | What visibly works | What needs improvement | Current disposition |
| --- | --- | --- | --- |
| Person | Detects clear, larger people in several street and indoor scenes. | Low reported recall (**0.411**); **114** unmatched ground-truth boxes at the failure-case threshold; video-frame leakage and crowded scenes. | Prototype only; collect walking-view people and review misses. |
| Chair | Detects isolated chairs and some crowded scenes. | **303** unmatched predictions; stool definition and incomplete crowded-scene labels need review. | Prototype only; normalize labels and audit crowded scenes. |
| Stairs | Detects many ordinary staircases. | Escalator mislabeled; step-by-step versus whole-staircase boxes; same staircase in train/test; **67** missed boxes. | Priority cleanup before any navigation claim. |
| Car | Detects many cars. | Same-scene video leakage; bus false alert seen; **56** missed boxes. | Prototype only; rebuild split and add campus traffic views. |
| Bicycle | Detects several pedal bicycles. | Motorcycle mislabeled; **24** missed boxes; riders and partial bicycles need review. | Prototype only; clean class boundary. |
| Electrical pole | Some posts are detected. | Crossing posts mislabeled; several boxes miss the pole; only **12** test groups; near-identical scenes cross splits. | **Unreliable**; rebuild this class and its test set. |
| Plant pot | Detects several close-up pots. | Bare pot mislabeled; only **9** test groups; mostly isolated close-ups, unlike walking scenes. | **Unproven in context**; collect campus scenes and clean labels. |

## Required next pass

1. Freeze v1 artifacts as historical evidence. Do not silently edit this test split or treat its score as a release gate.
2. Trace source images back to capture/video/product series and assign a durable **scene ID**. Split entire scenes, then verify no cross-split same-scene pairs with image-similarity screening plus manual review.
3. Resolve the annotation policy for stairs, chairs, poles, and pots; manually review every electrical-pole and plant-pot image and the full stairs queue. Audit a sample of all other classes for missing boxes and class mismatch. Record corrections in a v2 ledger.
4. Collect consented campus scenes using the intended phone/camera viewpoint. Keep an independent campus test set from locations, sessions, and scenes excluded from training and tuning.
5. Rebuild v2, retrain, evaluate per class and by setting, then test detection-level parity and latency on the Infinix X6853. Conduct supervised walking tests only after those gates.

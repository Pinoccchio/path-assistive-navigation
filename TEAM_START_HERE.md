# Start here: Group 8 assistive-navigation thesis

**A short team guide · Updated 2026-10-04**

We are building an **offline Android research prototype** that shows selected objects seen by a phone's rear camera. The intended use is a *supervised* assistive-navigation study. It is **not a navigation aid**: no detection means “unknown,” not “the path is clear.” Keep using the usual mobility aid during tests. The [product roadmap](docs/05_Product/Assistive_Navigation_PRD.md) describes the longer-term vision; some of its “current state” text predates the Flutter app.

## What exists today

The [Flutter app](apps/mobile/README.md) runs on the **Infinix Note 40 (X6853)**. Its camera view is contained within screen margins so the whole image and bounding boxes remain visible. It shows a detected object's label, confidence, approximate left/ahead/right direction, a live frame count, and processing time. Start and Stop control the camera session. Camera frames are sampled at most once every 500 ms; another frame is skipped while one is being processed.

The app bundles one **eight-class YOLOv8n-derived FP32 TFLite checkpoint** for technical testing. It does **not** speak warnings, vibrate, estimate distance, navigate routes, record video, use location, or send frames to a backend. The team has informally seen the app open, show the camera, and recognize objects from the [local image gallery](qa/phone_test_gallery/index.html) on the X6853. That spot check is not a scored phone evaluation or proof of correct box alignment in every scene.

## How we reached this point

| Stage | What happened | Evidence |
| --- | --- | --- |
| Initial pilot | A five-epoch, seven-class YOLOv8n training run proved the desktop pipeline could train and save results. | [Pilot notebook](notebooks/01_yolov8n_training_pilot.ipynb) |
| Public-data preparation | ROD and Open Images were assembled, then later versions screened duplicates and corrected suspect labels. COCO supplied common-object examples; source rights remain under review. | [Phase 1 history](ml/PHASE1_STATUS.md), [source ledger](ml/README.md) |
| Eight-class experiments | Motorcycle was added. The v11 YOLOv8n run became a useful comparison checkpoint, but person and small-bicycle detection remained weak. | [v11 report](ml/PHASE1_V11_STATUS.md) |
| Other pretrained models | COCO YOLOv8n, YOLO26n Objects365, and prompt-free YOLOE-26n were compared. More labels did not automatically improve our target classes; Objects365 lacks our stairs/pole definitions, and prompt-free YOLOE performed poorly on our stair test. | [Pretrained-model report](ml/PHASE1_PRETRAINED_MODEL_CANDIDATE_STATUS.md) |
| Latest retrain | The **person-retention candidate** excluded 290 incompletely reviewed Open Images training images and four ambiguous stair images; four other stair labels received a versioned correction. It trained for 12 epochs on an RTX 3050 Laptop GPU. | [Retrain report](ml/PHASE1_PERSON_RETENTION_CANDIDATE_STATUS.md), [dataset build report](data/processed/public_phase1_person_retention_candidate/build_report.json) |
| Phone prototype | The candidate was exported through ONNX to TFLite and bundled in the Flutter app. Ten desktop images passed a raw-output parity check; the app now displays live boxes on sampled camera frames. | [Export metadata](apps/mobile/assets/model/model_metadata.json), [parity report](runs/public_phase1_person_retention_candidate/tflite_fp32/parity.json), [app guide](apps/mobile/README.md) |

## Data, labels, and model results

The current candidate dataset has **3,008 training, 251 validation, and 620 public test images**. Its eight labels, in model order, are **person, chair, stairs, car, bicycle, electrical pole, plant pot, motorcycle**. Older seven-class documents predate the motorcycle addition. Motorcycle is an auxiliary class for distinguishing it from bicycle; showing its box for research QA does not make it a validated alert. Dataset images and weights should stay within the thesis team until source-image rights and Ultralytics model licensing are resolved.

The table below counts boxes matched on the **same reused 620-image public development test**, using 512-pixel input, confidence 0.25, and box-overlap threshold 0.5. These are not independent accuracy, phone accuracy, or safety percentages; some source images have incomplete labels.

| Label | Labeled boxes | v11 matched | Current candidate matched |
| --- | ---: | ---: | ---: |
| Person | 510 | 246 | **317** |
| Chair | 168 | 125 | **138** |
| Stairs | 122 | 98 | **101** |
| Car | 253 | 189 | **192** |
| Bicycle | 95 | **75** | 70 |
| Motorcycle | 90 | **48** | 42 |

Small bicycles remain especially difficult: **9 of 48** labeled boxes matched for the current candidate. The original COCO-pretrained YOLOv8n matched **372 of 510** labeled person boxes on this test, more than the current custom checkpoint. The [full paired report](runs/public_phase1_person_retention_candidate/paired_public_diagnostic_512.json) and [stair report](runs/public_phase1_person_retention_candidate/stair_public_diagnostic_512.json) contain image-level results. The app's bundled checkpoint is therefore a **research test model**, not a selected model for navigation alerts.

## Tools and how the app works

| Part | Tools used |
| --- | --- |
| Dataset and experiments | Python, Jupyter notebooks, Ultralytics YOLOv8n, PyTorch; training requirements are pinned in [requirements-training.txt](requirements-training.txt). |
| Model export | ONNX, onnx2tf, and TensorFlow Lite; [export script](ml/export_tflite_direct.py) and [desktop comparison](ml/verify_tflite.py). |
| Android prototype | Flutter/Dart, the `camera` plugin, `tflite_flutter`, Android SDK/Gradle, and the X6853 test phone. |

The live path is: **rear-camera frame → rotate/resize/color-convert → TFLite inference → remove overlapping predictions → draw boxes and labels**. The box is the rectangle around a predicted object; *confidence* is the model's score, not a guarantee that the object is present. The app reports processing time for a sampled frame, **not** measured capture-to-warning latency.

To open the current build from the workspace root:

```powershell
cd apps/mobile
flutter pub get
flutter run
```

The [eight-image gallery](qa/phone_test_gallery/index.html) can be displayed on a laptop and viewed through the phone camera for a quick visual check. These images come from the public test split, which has already influenced development; do not use a gallery demonstration as a new accuracy result. The app has also passed local Flutter analysis, widget tests, and a debug APK build. Those checks do not replace physical-device performance testing.

## What remains unverified

- **Labels and independent evidence:** A 179-image person-review queue has **five AI drafts in progress and zero human-complete reviews**. Bicycle, motorcycle, stairs, and source-label completeness still need review. No genuinely independent-source test has been reported. Campus data collection is deferred.
- **Phone performance:** No recorded p50/p95 latency, 20-minute stability, battery/thermal result, or systematic box-alignment result exists for the X6853. Informal camera/gallery observations are encouraging but limited.
- **User-facing warnings:** Speech, vibration, proximity zones, priority rules, TalkBack acceptance, and supervised participant testing have not been validated or enabled. The [PRD](docs/05_Product/Assistive_Navigation_PRD.md) describes these as later phases.
- **Distribution:** Source-image rights and Ultralytics licensing need review before any public dataset, model, or app release.

For details beyond this guide, start with the [app README](apps/mobile/README.md), [current retrain report](ml/PHASE1_PERSON_RETENTION_CANDIDATE_STATUS.md), [data/label policy](ml/PUBLIC_LABEL_POLICY.md), and [product roadmap](docs/05_Product/Assistive_Navigation_PRD.md). Historical reports under `ml/` explain earlier experiments; the current app and model metadata are the source of truth for what is installed today. This local workspace is not currently a Git checkout, so its versioned datasets and reports—not a commit log—record the experiment history.

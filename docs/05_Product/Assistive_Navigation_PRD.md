# Assistive Navigation: Product Requirements and Research Roadmap

**Status:** Build specification for a supervised thesis prototype  
**Date:** 2026-09-28  
**First device:** Infinix Note 40 (X6853), rear camera in a chest mount  
**Platform and language:** Android, English spoken alerts  
**Owners:** Group 8 thesis development team

## 1. Product decision

Build an offline-first Android app that recognizes selected obstacles in front of a user and communicates the most relevant warning through short speech and phone vibration. The first release is a **supervised research prototype**. It supplements a white cane or other established mobility aid; it is not a route-navigation system or a sole means of avoiding hazards. Researchers must remain present during movement tests. The first app has no account or cloud backend.

The thesis [manuscript](../04_Manuscript/Assistive_Navigation_Thesis_Ch1_Ch3.md) defines obstacle detection, approximate distance zones, priority alerts, multimodal feedback, and optional location context. This PRD turns those ideas into build order and measurable gates. The team selected a chest mount, one Note 40 test phone, English speech first, and location features after core alerts. Confirm the phone's installed Android version, available memory, camera modes, and mount geometry on the physical unit before implementation; model number alone does not establish its current software state. Infinix identifies X6853 as Note 40 and lists a Helio G99 Ultimate chipset ([model document](https://d1wd32b69guoqm.cloudfront.net/infinixmobility_com/NOTE-40-X6853-V1.0.pdf), [device page](https://wap.infinixmobility.com/note-40)).

### Users and primary task

- **Primary research user:** a person with visual impairment, recruited only after required ethics approval, who can start a supervised session, hear or feel selected obstacle cues, and stop immediately.
- **Researcher/operator:** installs the prototype, fixes the mount, checks permissions and calibration, supervises a controlled route, and reviews technical logs.
- **First task:** start a session, point the rear camera forward, receive a concise cue such as “Chair ahead” or, only after validated proximity testing, “Chair ahead, caution,” and stop the session.

Out of scope for this prototype: autonomous route instructions, crossing decisions, claims that no alert means a path is clear, exact meter estimates from a monocular depth map, iOS, background camera monitoring, public unsupervised release, and collision-reduction claims against an unassisted baseline.

## 2. Current evidence and gaps

The repository contains two notebooks, source metadata, prepared ROD pilot images and labels, and saved YOLOv8n results. It contains no Flutter app, mobile model export, camera integration, depth model, calibrated zones, priority engine, or phone benchmarks. Preserve the recorded pilot and its five-epoch settings as a baseline rather than rewriting them.

| Recorded pilot fact | Value | Interpretation |
| --- | ---: | --- |
| Training / validation images | 2,000 / 400 | Existing seven-class ROD subset; not a campus test set |
| Precision / recall | 0.775 / 0.627 | Detector still misses labeled objects |
| mAP@0.5 / mAP@0.5:0.95 | 0.719 / 0.506 | Preliminary desktop validation only |
| Electrical-pole mAP@0.5 | 0.181 | Critical weakness for a narrow hazard |

Source: [pilot summary](../../runs/yolov8n_pilot/pilot_summary.json), [overall metrics](../../runs/yolov8n_pilot/final_overall_metrics.csv), [per-class metrics](../../runs/yolov8n_pilot/final_per_class_metrics.csv). None of these numbers predicts performance on the Note 40 or on an independent campus walk.

The [proposal](../01_Proposal/Topic_6_Assistive_Navigation.md) contains illustrative targets and an example that speaks exact meters. Those are planning examples, not achieved results. MiDaS produces **relative depth**, so this PRD requires observed zone performance before any proximity wording; it does not use meter-level mean absolute error as a release criterion ([MiDaS documentation](https://github.com/isl-org/MiDaS)).

## 3. Technology and system design

| Layer | Choice | Reason and boundary |
| --- | --- | --- |
| App screens | Flutter stable channel, Android target | Matches thesis framework; owns Start/Stop, settings, accessible status, and later history |
| Live camera and inference | Kotlin module with CameraX `ImageAnalysis` and LiteRT `CompiledModel` | Keeps camera frames and model buffers native; `STRATEGY_KEEP_ONLY_LATEST` drops stale frames rather than building a queue ([CameraX](https://developer.android.com/media/camera/camerax/analyze), [LiteRT](https://developers.google.com/edge/litert/android)) |
| Detector | Existing YOLOv8n pilot checkpoint, then a revised seven-class checkpoint | Gives a reproducible baseline before model changes; export FP32 first, then compare calibrated INT8 on the device ([Ultralytics export](https://docs.ultralytics.com/modes/export)) |
| Depth candidate | MiDaS v2.1 Small mobile model | Has a documented mobile path; must pass phone-speed and zone tests before use in alerts ([MiDaS mobile notes](https://github.com/isl-org/MiDaS/blob/master/mobile/README.md)) |
| Feedback | Android text-to-speech and vibration, controlled by the native alert coordinator | Avoids sending every frame through Dart; Flutter displays the same current alert and status |
| Research storage | Local structured log with explicit consent and export action | No camera-frame recording by default; GPS and place names are Phase 5 only |

Use LiteRT CPU as the correctness baseline, then profile GPU on the physical phone. Do not assume an NPU delegate exists for its chipset. Bundle model files for offline use. Keep the Python training environment separate from the Android runtime; pin versions and record model hashes in each experiment. The current notebook's `ultralytics==8.3.0` is a pilot dependency, not an instruction to silently upgrade or retrain it.

Native-to-Flutter interface: `startSession(config)` and `stopSession()` commands, plus a stream of `status`, `alert`, and `telemetry` events. `config` contains enabled classes and audio/vibration choices; `alert` contains class, direction, optional validated zone, confidence, and frame timestamp; `telemetry` contains capture, preprocessing, inference, decision, and feedback times. Camera image bytes never cross this interface. Stop, permission loss, app pause, model failure, or an old frame must close the active warning and report an understandable status.

For detection, use the seven pilot labels: person, chair, stairs, car, bicycle, electrical pole, and plant pot. More proposed categories, especially doors, tables, and curbs, require labeled data and a new class-map/version; do not relabel COCO or the existing checkpoint as if they already recognize them. A detection box maps to left/center/right using its horizontal center in the corrected camera frame. No-detection means **unknown**, never “safe.”

If proximity passes validation, derive a per-object depth statistic from the same timestamped frame, reject invalid pixels and unstable readings, apply calibration from the fixed mount, and classify danger/caution/farther zones. Rank candidates by zone first, then whether they intersect the central walking region, then class hazard weight and confidence. Apply persistence across frames, hysteresis at zone boundaries, and a cooldown so speech does not repeat continuously. Give vehicles and stairs higher hazard weight than low-risk background objects; tune weights only on validation data. If the depth gate fails, use class-and-direction alerts with no zone terms.

## 4. Phased requirements and exit gates

### Phase 1 — Collect datasets, annotate, train, and evaluate

**Goal:** produce a documented public-data detector candidate first, then obtain independent campus evidence before making campus-performance claims. The team has chosen to defer campus capture while public dataset collection and training proceed.

**Stage 1A — Public data and model (in progress):** use the frozen seven-class guide and source ledger in [`ml/README.md`](../../ml/README.md). Acquire curated, class-balanced public images with source IDs, image rights, checksums, and original split recorded; audit exact and perceptual duplicates and annotations; train a reproducible candidate; evaluate on an untouched public test set; export a desktop-checked mobile model. Public-test scores are explicitly not campus scores. The existing pilot remains historical evidence.

**Stage 1B — Campus validation (pending):** complete the following campus capture, annotation, and test steps when permission and capture logistics are ready. Do not mark the full Phase 1 gate passed merely because Stage 1A completed.

1. Freeze the seven-class definition, positive/negative examples, box conventions, and source-license ledger. Treat the existing ROD pilot as training evidence, not independent test data. ROD is listed as MIT on its [dataset page](https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO); check the underlying image provenance before redistribution. COCO may supply common classes; Open Images may supplement underrepresented classes, with per-image license and annotation provenance recorded ([Open Images V7](https://storage.googleapis.com/openimages/web/factsfigures_v7.html)).
2. Capture a target of **1,000–1,500 distinct campus images** across corridors, entrances, stairs, walkways, parked vehicles, lighting changes, occlusion, and motion. Record the camera mount height/angle, scene, date, and capture session. Extract video frames sparsely enough to avoid nearly identical examples. Obtain permissions and avoid identifiable people when consent is absent.
3. Annotate with CVAT or an equivalent tool using the frozen guide; review every pole and stair label plus a random sample of other classes. Track disagreements and corrections ([CVAT quality tools](https://opencv.github.io/cvat/docs/)). Split by walk/session and location into training, validation, and an **untouched test set of at least 200 images**. Target at least 30 test instances for each critical class; report any shortfall rather than inventing class performance.
4. Run duplicate/leakage and missing-label checks; train a new YOLOv8n candidate with fixed seed, configuration, dataset manifest, source versions, and checkpoints. Compare the old pilot, pretrained baseline, and new candidate on the same campus test set. Report per-class precision, recall, mAP, confusion matrix, and failure examples. The 0.719 pilot mAP must not be reused as the campus result.
5. Export the selected checkpoint to LiteRT/TFLite, first FP32 and then INT8 using representative training/validation images for calibration. Compare exported predictions against the desktop model on fixed images; keep the higher-fidelity model if quantization substantially weakens critical classes.

**Gate to Phase 2 technical app work:** Stage 1A has a versioned dataset manifest, annotation guide, license ledger, class counts, leakage report, frozen public test set, reproducible training command/config, exported model, and explicit per-class error analysis. Stage 1B remains mandatory before any campus-performance or supervised-walking claim. The team may proceed with a detection-only technical app if pole detection remains weak, but the PRD and UI must disclose that weakness; a poor class result cannot be hidden behind overall mAP.

### Phase 2 — Offline detection on the Infinix Note 40

Build the Flutter shell and Kotlin CameraX/LiteRT module. Verify frame rotation, aspect ratio, color conversion, normalization, postprocessing, and class-map parity against Phase 1 fixtures. Use one-frame analysis backpressure; timestamp every stage. Provide an offline session with accessible Start/Stop, camera and model status, English class-and-direction speech, and vibration. Keep a debug overlay for researchers; users need not read the preview.

**Gate:** a 20-minute chest-mounted session completes without crash or growing frame backlog; airplane-mode warnings still operate; all seven class outputs map correctly; Start, Stop, permission denial, and model failure work with TalkBack. Record p50/p95 capture-to-feedback latency, processed frames per second, battery change, and thermal behavior on the actual phone. A **p95 alert time over 500 ms**, repeated stale alerts, or thermal shutdown blocks movement testing and triggers profiling/resolution or model changes. This is an engineering gate for supervised study, not a declaration of independent-walking safety.

### Phase 3 — Validate proximity zones

Benchmark MiDaS Small alone and alongside detection on the phone. Collect synchronized controlled scenes with obstacles at measured reference positions and varying lighting and object types. Fix and document mount geometry. Derive danger/caution/farther thresholds from a calibration subset and evaluate on separate walks/scenes. Use zone accuracy, confusion matrix, near-obstacle false-negative rate, and combined p95 latency; do not turn relative depth directly into spoken meters.

**Gate:** target at least **80% macro zone recall** and **90% recall for the nearest danger-zone examples** on the held-out controlled set, while still meeting the Phase 2 latency/stability gate. These are proposed study thresholds, not observed results. If either gate fails, leave zones disabled and continue with detection-only cues; document the failed experiment and do not substitute unvalidated box-size distance claims.

### Phase 4 — Priority, feedback, and accessible usability

Add priority ranking, temporal smoothing, stale-frame rejection, speech cooldown, and distinct vibration patterns for validated urgency levels. Give speech precedence to the highest-priority current obstacle; allow immediate replacement when a higher-risk candidate appears. A single Stop action must silence pending speech and vibration. Test whether vibration is perceptible through the chest mount; if it is not, retain speech as the primary channel and record the limitation. Test settings and the full session flow with TalkBack and manual accessibility review ([Android accessibility testing](https://developer.android.com/guide/topics/ui/accessibility/testing)).

**Gate:** scripted multi-object cases choose the expected alert; repeated static objects do not flood speech; changing hazard priority updates the cue; inaccessible controls or ambiguous failure states block participant testing. Measure false and missed alerts per controlled scenario, not just aggregate detection mAP.

### Phase 5 — Optional location and supervised study

Add opt-in location only while a session is active. Store approximate coordinates and selected warning events locally. Resolve place names only when network access exists; denied location or failed geocoding must have no effect on camera warnings. Provide a local history view and an explicit, consent-based research export. Do not record raw video or continuous location by default.

Prepare an ethics submission and supervised protocol before recruiting visually impaired participants. A researcher accompanies each participant; the existing mobility aid remains available. Evaluate alert comprehension, workload, TalkBack usability, session control, and perceived usefulness through observation, interviews, and SUS if approved. If recruitment is not approved or feasible, finish with a clearly labeled technical/controlled evaluation. Sighted simulation is not a substitute for participant evidence. Do not compare collisions against an unassisted walking baseline.

## 5. Acceptance record and decisions that must remain visible

Every phase ends with a short evidence report: model/data version, device build, test scenes, pass/fail against its gate, failures, and the exact app capabilities enabled. Publish descriptive statistics and confidence intervals where sample sizes allow; show per-class and per-scene breakdowns. Freeze thresholds before evaluating the test set. A threshold miss narrows prototype claims and blocks the dependent feature or study; it does not erase the result.

The first app implementation should live under `apps/mobile/`; training and export scripts should live under `ml/` while the existing notebooks and recorded `runs/` remain historical evidence. Keep app model assets versioned with checksum and class-map metadata. Use local tests for preprocessing/postprocessing, coordinate transforms, alert ranking, cooldown, and error states; use the phone for performance and TalkBack acceptance. There is no public API or backend contract in this version.

**Open measurements, not open product choices:** installed Android build, actual accelerators, mount vibration perceptibility, campus class counts, and phone inference speed are unknown until measured. The chosen response to each failed gate is specified above. Any later public release requires a new PRD and broader device, accessibility, field, and safety evaluation.

## 6. Source and tool notes

- Product scope and research questions: [current manuscript](../04_Manuscript/Assistive_Navigation_Thesis_Ch1_Ch3.md).
- Recorded pilot: [training notebook](../../notebooks/01_yolov8n_training_pilot.ipynb), [metrics](../../runs/yolov8n_pilot/final_overall_metrics.csv).
- Runtime, camera, export, and depth: [Google LiteRT](https://developers.google.com/edge/litert/android), [Android CameraX](https://developer.android.com/media/camera/camerax/analyze), [Ultralytics export](https://docs.ultralytics.com/modes/export), [MiDaS mobile](https://github.com/isl-org/MiDaS/blob/master/mobile/README.md).
- Optional skills found for later execution: [PRD workflow](https://skills.sh/github/awesome-copilot/prd), [Flutter accessibility](https://skills.sh/flutter/agent-plugins/flutter-improving-accessibility), and [dataset curation](https://skills.sh/voxel51/fiftyone-skills/fiftyone-dataset-curation). They were identified for future use; none is installed by this document.

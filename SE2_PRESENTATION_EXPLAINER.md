# SE2 thesis presentation: slide-by-slide explainer

Source deck: `SE2_Thesis_Progress_Presentation.pptx` (10 slides). This guide was checked against `TEAM_START_HERE.md`, `apps/mobile/README.md`, and `docs/05_Product/Assistive_Navigation_PRD.md`.

## Read this before presenting

The slides mix the intended system with the current prototype. **The current phone app is a detection-only technical test build.** It uses an **eight-class FP32 TFLite model** and displays camera frames, bounding boxes, labels, confidence, approximate left/ahead/right direction, frame count, and processing time. It does **not** speak or vibrate, estimate distance, provide navigation alerts, use GPS, or run an Int8 model. A missing detection does not mean the path is clear. The app is not a navigation aid.

Suggested introduction:

> Our thesis explores whether an offline Android phone can detect selected objects and eventually provide useful, timely cues for supervised assistive-navigation research. We have built a detection-only technical prototype and compared model candidates. Distance, alerts, and mobility testing still require separate validation.

## Slide 1 — Title

- **Edge AI:** AI runs on the phone, close to where camera data is captured.
- **Spatial perception:** Understanding where objects appear. The current app estimates left/ahead/right from image position; it does not identify a safe walking route or reliable distance.
- **On-device:** Processing happens locally, without a remote inference server.
- **Assistive navigation prototype:** A research concept intended to supplement established mobility aids. The current app is not a proven navigation aid.

**Say:** “We are testing local object recognition as a first step toward supervised assistive-navigation research.”

## Slide 2 — Project overview

- **Problem statement:** The need for useful additional information about obstacles and surroundings.
- **BLV:** Blind and Low-Vision, the intended participants in a future supervised study.
- **White cane and guide dog:** Established mobility aids. This prototype must supplement, never replace, them.
- **Offline-first:** Core detection works without internet.
- **Cloud AI:** Remote processing that can introduce network delay and camera-data privacy concerns.
- **Latency:** Delay between input and response. The slide’s `<500 ms` value is a target, not a demonstrated capture-to-warning result.
- **Privacy-preserving:** Keeping frames on the device avoids cloud video transmission; it does not eliminate every privacy risk.
- **Multimodal feedback:** More than one output mode, such as speech and vibration. Planned, not active.
- **TTS (Text-to-Speech):** Software that speaks a phrase such as “Chair ahead.” Not enabled in the current app.
- **Haptics:** Phone vibration patterns. Not enabled.
- **O&M specialist:** Orientation and Mobility specialist, trained in safe travel for BLV people.
- **IRB/ethics committee:** Reviews the ethics, consent, and safety of research involving participants.

**Check before presenting:** Find a proper source for the slide’s “2.2 billion” statistic. Do not present the latency target as a measured result.

## Slide 3 — Software requirements

- **Functional requirement:** An action the system is supposed to perform.
- **Camera ingestion:** Receiving live rear-camera images.
- **Frame:** One image from the camera stream.
- **Tensor:** An array of numbers passed into or returned by an AI model.
- **Preprocessing / normalization:** Rotating, resizing, color-converting, and formatting camera pixels as model input. The slide mentions 640×640; verify the precise live app stages before claiming that every stage runs at that size.
- **Object detection:** Predicting object types and their image locations.
- **YOLOv8n:** A compact YOLO (“You Only Look Once”) object detector; `n` means nano.
- **FP32:** 32-bit floating-point model values. **This is the format bundled in the current app.**
- **Quantization:** Converting model values to a lower-precision representation, often to reduce size or improve speed. Accuracy must be rechecked.
- **Int8:** Signed 8-bit integer values used in quantized models. **Int8 is not the current phone model.** Its speed and accuracy on target hardware remain to be compared.
- **TFLite / LiteRT:** Google's on-device machine-learning runtime/model ecosystem. The app currently uses `tflite_flutter` to run an FP32 `.tflite` model.
- **Bounding box (BBox):** Rectangle around a predicted object.
- **Centroid:** The box's center point. Its horizontal position gives an approximate left/ahead/right direction.
- **Three-region direction:** Dividing the camera image into left, center, and right. It does not recommend a safe avoidance route.
- **MiDaS:** Proposed single-camera relative-depth model. It cannot directly establish trustworthy real-world meters. Not integrated into the current app.
- **Danger/Caution/Safe zones:** Proposed proximity or urgency categories that need calibration and held-out testing. “Safe” is risky wording: no detection does not prove safety.
- **Priority engine:** Planned rules to select the most relevant current hazard for an alert.
- **GPS:** Approximate geographic location.
- **Reverse geocoding:** Turning coordinates into a place/address name; may require internet. Not in the current app.
- **Requirement traceability:** Connecting each thesis objective to a feature and test.

**Correction:** Move Int8, TTS, depth zones, priority alerts, preferences, and location into planned requirements.

## Slide 4 — Design and architecture

The deck's eight layers are a **proposed architecture**:

1. **Input:** Camera and optional future GPS.
2. **Preprocessing:** Prepare images for inference.
3. **Inference:** Run YOLO and, if validated later, MiDaS.
4. **Post-processing:** Interpret outputs, filter overlapping predictions, and map locations.
5. **Priority:** Choose one hazard to alert on. Planned.
6. **Feedback:** Speech and vibration. Planned.
7. **Location:** Optional place context. Planned.
8. **Session/preferences:** Local logs and settings. Planned.

Other terms:

- **Inference:** Running a trained model on a new image; different from training it.
- **Post-processing:** Cleaning and interpreting raw outputs, such as removing overlapping boxes.
- **Asynchronous processing:** Doing heavier work without blocking every UI operation.
- **Dart isolate:** A separate Dart execution context. The current app uses a `tflite_flutter` inference isolate, but this does not guarantee zero lag or 60 FPS.
- **60 FPS:** Sixty displayed frames per second. It needs measurement, not an architectural promise.
- **State machine:** Defined states and transitions, such as Idle → Capture → Process → Alert → Cooldown. The full alert flow is not implemented.
- **Cooldown:** Waiting before repeating speech so warnings do not flood the user. Planned.
- **SQLite:** Local device database. The slide's tables are a design, not current app storage.
- **UUID:** A unique record identifier.
- **Schema:** Fields and types used to structure stored records.
- **Flutter/Dart:** UI framework and programming language used by the phone app.
- **Camera2/CameraX:** Android camera technologies. The current app uses Flutter's camera plugin; the roadmap considers a more native CameraX/LiteRT route if needed.
- **ARM:** Common phone processor architecture.
- **LiDAR:** Distance-sensing hardware. A regular-camera depth model avoids requiring it but needs careful calibration.

## Slide 5 — Current prototype progress

**Demonstrable now:** Start/Stop, rear-camera preview, eight-class FP32 local detection, boxes, labels, confidence, approximate direction, frame count, and sampled-frame processing time. The app samples at most one frame every 500 ms and skips a frame when processing is busy.

- **Interpreter:** Component that loads and runs the `.tflite` model.
- **Confidence:** The model's prediction score, not proof that the object is present.
- **Frame sampling:** Processing selected frames rather than every camera frame.
- **Processing time:** Time reported for a sampled frame. It is not measured camera-to-spoken-warning latency.
- **Code modularity:** Separating camera, inference, overlay, and other responsibilities.
- **Version control/branches:** Tools for recording code changes and isolating work. Verify the deck's specific GitHub branch workflow with the team; this local workspace is not currently a Git checkout.

**Do not claim:** A working “Chair, Center” voice prompt, Int8 phone inference, a completed audio pipeline, or verified safe alerts.

## Slide 6 — Software engineering practice

- **Spiral model:** Repeat planning → risk analysis → engineering → evaluation. Appropriate because data quality, model errors, latency, depth, and safety need repeated checks.
- **Risk analysis:** Identify possible failures and design tests before relying on the feature.
- **Re-quantization:** Try another lower-precision export or calibration when optimizing; then compare accuracy and speed.
- **Heuristic:** A practical rule, such as giving central objects higher priority.
- **Kanban:** Task board with states such as To Do, In Progress, and Done. Verify that GitHub Projects was actually used before claiming it.
- **Unit test:** Checks one function, such as coordinate conversion.
- **Integration test:** Checks components working together.
- **Usability test:** Studies whether people can understand and use the system.
- **SUS:** System Usability Scale questionnaire. Planned, not completed.
- **meCUE 2.0:** User-experience questionnaire framework. Planned, not completed.
- **Configuration management:** Tracking model assets, settings, dependencies, and versions so work is reproducible.
- **`pubspec.yaml`:** Flutter package and asset configuration.
- **Dependency locking:** Recording exact package versions, typically in `pubspec.lock`.

## Slide 7 — Challenges and risks

- **Thermal throttling:** Phone slows processing when it becomes hot.
- **Battery drain:** Camera and AI processing consume power during long sessions.
- **Monocular:** Using one camera.
- **Scale ambiguity:** A single image usually cannot provide exact physical distance without assumptions or calibration.
- **Occlusion:** An object is partly hidden.
- **Motion blur:** Movement blurs an image and can reduce detection quality.
- **Latency budget:** Maximum acceptable delay set as an engineering target.
- **Cognitive overload:** Too much information to process while moving.
- **Alert fatigue:** Repeated low-value alerts cause warnings to be ignored.
- **PTQ (post-training quantization):** Converting a trained model to lower precision after training; it must be measured and validated.
- **FLOPs:** Approximate number of arithmetic operations. Fewer operations can help, but phone performance still needs testing.
- **False negative:** An object is present but missed; especially serious for safety.
- **False positive:** An object is reported when it is absent; can create distracting alerts.

**Say:** “Missed and misleading warnings are why this remains a supervised technical test build until separate safety-related checks pass.”

## Slide 8 — Next steps

- **Model fusion:** Combining detector and depth outputs from corresponding frames. Adds processing cost.
- **Haptic pattern:** Vibration rhythm intended to represent direction or urgency; must be tested on the actual mount and with users.
- **RAM:** Working memory while the app runs.
- **FPS:** Frames per second; specify whether discussing camera preview, processed frames, or UI rendering.
- **mAP50:** Mean Average Precision at an Intersection-over-Union (IoU) threshold of 0.50. A detection metric, **not “50% accuracy”** or proof of navigation safety.
- **IoU:** Overlap between a predicted box and the labeled box.
- **Zone correctness:** Whether a proposed distance-zone prediction agrees with measured reference scenes. Not yet validated.
- **APK:** Android installation package.
- **Sideloading:** Installing an APK directly on a test phone.
- **Telemetry:** Data sent from an app for analytics or diagnostics. The current app has no backend.
- **Supervised field trial:** Study with observers and safety controls. Future work.

**Sequence to explain:** Review labels and models → obtain independent evaluation → measure sustained phone performance → validate depth zones → implement and test priority/feedback → supervised participant study. If a gate fails, leave the dependent warning disabled.

## Slide 9 — Timeline

- **Milestone:** A meaningful completed stage, such as a trained candidate or a working camera test build.
- **Pilot:** Early experiment showing that an approach can run; not final validation.
- **Technical release:** Build for controlled engineering testing; not necessarily public or safe for mobility use.
- **Thesis defense:** Presenting the problem, method, evidence, limitations, and conclusions to evaluators.

**Correction needed:** The slide claims September–November 2026 work is on schedule for an October v1.0 release. As of **October 27, 2026**, that wording is stale. Update milestones from actual team evidence. The public-data and phone work do not complete independent or campus validation.

## Slide 10 — Conclusion

- **Technical feasibility:** The team has shown local phone detection with a visual overlay. Full assistive navigation and safety are not proven.
- **Operational baseline:** The minimum working app: camera, detector, and visible results.
- **Human factors:** How users understand warnings, manage workload, and develop trust.
- **Supplementary aid:** Additional information used alongside established mobility tools.

Suggested closing:

> Our current result is an offline detection-only Android research build. Next we need stronger independent evaluation, phone performance measurements, and validation of depth and alerts. Until those pass, we will not claim reliable distance warnings or safe independent navigation.

## Five distinctions to memorize

| Question | Answer |
| --- | --- |
| FP32 or Int8? | **FP32 is installed now.** Int8 is a planned lower-precision comparison. |
| Detection or distance? | Detection says what and roughly where in the image. It does not establish physical distance. |
| Processing time or alert latency? | The app shows sampled-frame processing time. It has no audio alert, so capture-to-warning latency is not measured. |
| Public test or independent test? | The reused public development test diagnoses models; it is not an independent campus or safety result. |
| Prototype or navigation aid? | The current app is a supervised technical research prototype, not an independent-walking aid. |

If you forget a term during the defense:

> That is part of our proposed architecture. The current verified build is detection-only. We will enable that feature after its performance and safety checks pass.

## Likely panel questions

**What works today?** A Flutter Android app runs an eight-class FP32 TFLite detector on sampled rear-camera frames and displays boxes, labels, confidence, approximate direction, frame count, and processing time.

**Why not use it for independent walking?** Missed objects and inaccurate cues could cause harm. Independent-scene detection, proximity zones, capture-to-alert latency, and user outcomes have not been validated.

**Does it measure distance?** No. MiDaS is only a proposed relative-depth approach. Any distance zones need calibration and testing against measured scenes.

**What is the accuracy?** Desktop experiments have per-class results on a reused 620-image public development test, but that is not independent campus accuracy or phone safety accuracy. Person and small-bicycle performance remain concerns.

**Why not use a pretrained detector?** Alternatives were compared; more classes do not necessarily match the target obstacle definitions. The selected model still needs independent comparison and error analysis.

**Why does the slide say Int8?** It describes an intended optimization. The model installed in the current phone app is FP32.

**Are warnings fast enough?** Unknown. Capture-to-feedback latency, sustained phone speed, heat, and battery still need measurement after feedback is implemented.

**Why speech and vibration?** They are proposed complementary cues, but their timing, clarity, and perceptibility need actual user and device testing.

**What does offline mean?** Current camera inference runs locally without a backend. Optional future place lookup may use a network but must not block core local processing.

# Navigation Research Android prototype

The app includes the THESIS Figma PATH HUD, Settings & Accessibility, and Hazard Log UI, with licensed local Inter fonts and source-exported artwork. Open the top-right HUD menu to navigate. Detection speech summarizes multiple enabled objects, for example "2 people, ahead. bicycle, left." Mute/Unmute and Repeat last alert are functional. Settings save locally and control delivery mode, speech rate, cooldown, spoken direction format and spoken category filtering. Neutral haptic detection-update cues are connected. Depth, GPS and live history remain in development. See the [source and QA inventory](../../docs/05_Product/PATH_MAIN_SCREEN_INVENTORY.md). The raw Figma reference pack stays local at `qa/figma-source/index.html` and can be regenerated with `scripts/export_thesis_figma.py` using private credentials. A full restart registers the speech plugin when upgrading from the earlier UI-only build.

The Hazard Log menu currently opens a clearly labeled PREVIEW using Figma's sample location and hazard events. Its address, distances, severities and timestamps are example content. Clear/Undo affects the preview only; live GPS/history, shake gestures, and alert cancellation are not connected.

The HUD now follows the user-approved camera-first concept in `qa/design-concepts/path-camera-first-approved.png`. A large proportional preview replaces the small camera panel and separate oversized message card. Each bounding box shows its class and direction, such as PERSON · AHEAD; the fixed LEFT/CENTER/RIGHT headings are removed. The compact Last spoken overlay opens the full message when tapped. The bottom dock contains Mute/Unmute, Repeat and Stop. The yellow primary action starts the camera when idle, then offers Describe scene while live and switches to More details while description pages remain. The menu retains Settings, Hazard Log, a Describe scene restart, and a saved Haptics on/off control with device status. Enlarged text and short screens use a scrollable layout so controls remain reachable.

Flutter live-detection test build for the Group 8 assistive-navigation thesis. The camera sits in a large contained viewport, so the full image and labeled bounding boxes stay visible inside the screen margins. It starts and stops the rear camera, runs the eight-class person-retention TFLite checkpoint on sampled frames, releases the camera when the app leaves the foreground, and shows permission/model/voice errors. The earlier [full-screen mockup](../../docs/05_Product/mockups/navigation_fullscreen_proposal.png) was superseded after phone review showed boxes reaching the screen edge. Speech describes detections; it **does not estimate distance, classify danger or provide route guidance**. Do not use it as a navigation aid.

Run on a connected Android device:

```powershell
cd apps/mobile
flutter pub get
flutter run
```

This research build uses Flutter's `camera` plugin and `tflite_flutter` inference isolate. It samples at most one frame per 500 ms and drops frames while processing. The FP32 model was exported from the person-retention `.pt` checkpoint; its [metadata](assets/model/model_metadata.json) fixes the class order and SHA-256. Desktop raw-output parity against ONNX passed on ten public test images, but camera rotation/color/letterboxing, detection-level parity, and Infinix X6853 latency need physical-device QA. The [product requirements](../../docs/05_Product/Assistive_Navigation_PRD.md) specify a later native CameraX/LiteRT path if this Dart prototype does not meet the latency gate. No account, backend, recording or location permission is included. Android vibration uses the normal VIBRATE permission.

## Detection speech verification

The speech adapter uses [flutter_tts 4.2.5](https://pub.dev/packages/flutter_tts). Android must have an installed English voice whose engine reports that it does not require a network connection. A missing voice produces a visible setup message and leaves camera detection available. The Android TTS service query is declared in the manifest; no microphone permission is needed.

Automatic speech announces up to two changed class/direction/count groups, such as "2 people, ahead. bicycle, left." An unchanged scene stays quiet even after the cooldown. Confidence fluctuations and box order alone do not trigger speech. This remains confidence-ordered detection reporting, not calibrated hazard priority.

Describe scene reads the current stable groups in pages of three. If there are more groups, the app announces the additional object count and the same yellow primary button becomes More details. That button reads the next page, then returns to Describe scene when complete. Describe scene is also available from the menu to restart the description. Paging order is independent of confidence fluctuations. If the scene changes, the next page restarts with "Scene changed" rather than reading old data. Repeat explicitly says "Last announcement" and replays the historical message; it does not claim the old scene remains current.

Temporal association matches same-class boxes one to one by IoU, requires two consecutive observations before confirmation, tolerates one missed processed frame, and requires two observations to change direction. Tracks expire after two misses or a 1.5 second observation gap. These are research parameters, not validated safety thresholds. At the current 500 ms sampling interval, confirmation adds at least one observation interval and can take longer when processing is slow. This basic matcher does not recognize people, guarantee identity through crossings, estimate approach rate, or implement the Kalman/Hungarian pipeline in [SORT](https://arxiv.org/abs/1602.00763). Counts are model-derived estimates.

Perception continues updating while speech is busy, muted or cooling down; old utterances are never queued. Freshness uses a monotonic clock and the camera callback time before inference, not the sensor exposure timestamp. Results older than two seconds and out-of-order results are rejected for speech; manual descriptions explain when fresh information is unavailable. A fresh empty scene is described on request as unknown, never clear. Pending scene utterances are checked again after asynchronous rate configuration. These bounds need target-phone timing evaluation.

The saved cooldown begins at speech completion. Manual Describe/More/Repeat bypass cooldown and are disabled during playback. Stop, backgrounding, leaving the HUD, mute and disposal cancel speech and invalidate pending utterances. New sessions reset tracking, paging and message history. Clock mode uses coarse 10/12/2 o'clock image labels, not measured angles. Category switches affect speech while boxes remain visible. Haptic Only suppresses voice and uses neutral detection-update pulses when haptics is enabled and supported.

Automated checks cover tracking/occlusion/direction stabilization, change-only speech, mixed-object counts, complete detail paging, settings, stale/out-of-order data, initialization/configuration cancellation, voice selection and accessible controls. The user reported initial speech working on the phone; the new temporal policy, offline operation, intelligibility, cancellation latency and mobility effectiveness still need physical verification. Depth, near/far zones and danger prioritization remain pending calibration and evaluation.

After a full `flutter run` restart, check on the phone:

1. Start the camera and hold one object in view for at least two processed observations. Listen for its class and direction. Keep the scene unchanged beyond cooldown and confirm it stays quiet.
2. Move the object across the image thirds and add/remove another object. Brief flicker should be suppressed; sustained changes should be announced after confirmation and cooldown. Compare two-person counts with the boxes.
3. Tap Describe scene for the current grouped scene. If More details appears, read the remaining groups. Change the scene between pages and confirm it restarts explicitly. Repeat should say "Last announcement" before replaying the message.
4. Tap Mute audio during playback. Current speech should stop and later frames remain silent. Unmute, then Describe scene to verify it uses the refreshed scene.
5. Stop the session during playback. Confirm speech stops and Describe/Repeat/More become unavailable. Restart and confirm old counts/pages do not reappear.
6. In Settings, change rate/cooldown and category toggles, then restart the session. Confirm both outputs follow the selected delivery mode; Haptic Only should vibrate without speech.
7. Background the app during speech and return. Confirm the camera stays stopped and no delayed announcement plays. Check TalkBack traversal and enlarged text separately.
8. Once an offline English voice is installed, disable connectivity and repeat. Record the phone, voice engine and observed timing. Do not infer offline success, count accuracy or navigation readiness from desktop tests.

After the camera-first update, check full image framing and box alignment on the phone as well: portrait image content should fit in proportion with possible letterboxing, never zoom-to-fill or stretch. Text overlays are painted at display size independently of camera image scaling. Desktop tests verify the fit geometry, not sensor orientation and physical camera correctness on every device.


## Haptic detection cues

The app uses an app-owned Android `path/haptics` method channel, without a new Flutter plugin or SDK upgrade. It probes the device vibrator and requests one 120 ms pulse at default amplitude for a meaningful stabilized scene change. The native code uses [VibrationEffect.createOneShot](https://developer.android.com/reference/android/os/VibrationEffect) on Android 26 and newer, with the legacy one-shot call on supported older Android versions. This is a neutral update cue: it encodes no object class, direction, distance or severity. There are no repeating patterns or timers.

Detection pulses explicitly use [accessibility vibration usage](https://developer.android.com/reference/android/os/VibrationAttributes#USAGE_ACCESSIBILITY) on Android 33+, with accessibility audio attributes on older supported versions. Read-only diagnostics on the Infinix X6853 showed that the original unclassified one-shot was treated as TOUCH and rejected as ignored_for_settings: touch feedback was OFF while accessibility vibration was MEDIUM. This classification fix does not change global settings or use interruption-bypass flags. Respect the accessibility vibration settings; a native success response alone does not prove Android played a pulse.

Voice + Haptic enables both outputs. Voice Only suppresses vibration and disables its quick toggle. Haptic Only does not initialize TTS and can vibrate without an installed English voice. The saved menu switch independently enables/disables haptics in modes that permit it. If that switch is off, Haptic Only intentionally produces no output until reenabled. Missing hardware or playback failure is reported in the feedback status/menu while camera detection and available voice output continue.

Haptics consumes the same confirmed scene as speech, shares its monotonic clock and freshness contract, and filters the enabled categories. An unchanged scene, empty scene, stale result or disabled category does not pulse. One scene update produces one pulse, not one per object. Haptic cooldown is measured from pulse dispatch and uses the saved cooldown setting independently of speech completion. Muting audio does not mute haptics. Manual Describe/More/Repeat remain spoken operations; the neutral pulse is for automatic detection changes.

Stop, navigation away, backgrounding and disposal cancel native vibration and invalidate pending state. Android additionally cancels from activity pause/destruction. [MethodChannel FIFO ordering](https://api.flutter.dev/flutter/services/MethodChannel-class.html) keeps a cancellation sent after a pulse ordered after that pulse request. Pending capability checks cannot restart a stopped session. The hardware permission, successful compilation and capability response do not prove that a physical pulse is perceptible.

This update changes native Android code: fully stop the existing `flutter run` process and run `flutter run` again. Hot reload or Dart hot restart alone does not install the native channel.

On the phone, select Voice + Haptic, start the camera and hold an object steady until confirmed. Verify one short vibration alongside the first update, and silence for an unchanged scene. Introduce another object after cooldown. Then check Voice Only, Haptic Only, menu off/on, audio mute with haptics still enabled, Stop and background cancellation. Verify the saved toggle after restarting the app. Record the actual Infinix behavior, vibration strength and timing; these remain pending until observed.

# Navigation Research Android prototype

The app now includes the THESIS Figma PATH HUD, Settings & Accessibility, and Hazard Log UI, with licensed local Inter fonts and source-exported artwork. Open the top-right HUD menu to navigate. Settings selections save locally; speech/haptics, GPS, and live history recording remain marked In development. Detection-only behavior remains unchanged. See the [source and QA inventory](../../docs/05_Product/PATH_MAIN_SCREEN_INVENTORY.md). The raw Figma reference pack stays local at `qa/figma-source/index.html` and can be regenerated with `scripts/export_thesis_figma.py` using private credentials. Stop the existing Flutter run and start it again after this update to register the new preferences plugin.

The Hazard Log menu currently opens a clearly labeled PREVIEW using Figma's sample location and hazard events. Its address, distances, severities and timestamps are example content. Clear/Undo affects the preview only; live GPS/history, shake gestures, and alert cancellation are not connected.

Flutter live-detection test build for the Group 8 assistive-navigation thesis. The camera sits in a large contained viewport, so the full image and labeled bounding boxes stay visible inside the screen margins. Compact live metrics and a large Stop control remain below it. It starts and stops the rear camera, runs the eight-class person-retention TFLite checkpoint on sampled frames, releases the camera when the app leaves the foreground, and shows permission/model errors. The earlier [full-screen mockup](../../docs/05_Product/mockups/navigation_fullscreen_proposal.png) was superseded after phone review showed boxes reaching the screen edge. It **does not estimate distance or issue obstacle alerts**. Do not use it as a navigation aid.

Run on a connected Android device:

```powershell
cd apps/mobile
flutter pub get
flutter run
```

This research build uses Flutter's `camera` plugin and `tflite_flutter` inference isolate. It samples at most one frame per 500 ms and drops frames while processing. The FP32 model was exported from the person-retention `.pt` checkpoint; its [metadata](assets/model/model_metadata.json) fixes the class order and SHA-256. Desktop raw-output parity against ONNX passed on ten public test images, but camera rotation/color/letterboxing, detection-level parity, and Infinix X6853 latency need physical-device QA. The [product requirements](../../docs/05_Product/Assistive_Navigation_PRD.md) specify a later native CameraX/LiteRT path if this Dart prototype does not meet the latency gate. No account, backend, recording, location permission, spoken warnings, or vibration is included.

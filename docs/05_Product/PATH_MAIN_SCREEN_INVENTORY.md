# PATH main camera screen

Implementation and desktop verification: 2026-11-10. This is a detection-only research UI, not the full Figma feature set.

## Source and exports

THESIS Figma file `aFXQm7eAu32gXNeWt7WJVe`, version `2419075896925554276`, source last modified `2026-11-09T15:44:59Z`. The refreshed comments endpoint returned zero comments.

| Source node | Reference | Result |
| --- | --- | --- |
| `2:1624` | Navigation HUD, 390 x 844 | Main camera screen implemented with research-specific adaptations |
| `2:1669` | Settings and accessibility, 390 x 844 | Implemented with local preference storage; alert output remains in development |
| `2:1734` | Hazard log and GPS context, 390 x 844 | Implemented empty/populated UI, clear/undo; live event/GPS pipeline remains in development |
| `2:1787` | PATH design/accessibility board, 1440 x 3748 | Source tokens and accessibility intent |
| `2:1977` | CPU icon | Original 2x PNG used at `apps/mobile/assets/figma/cpu.png` |
| `2:1986` | Volume icon | Original 2x PNG used at `apps/mobile/assets/figma/volume.png` for Repeat last alert |
| `2:1980` | Audio waveform | Source PNG used in the bordered alert card |
| `2:1983` | Warning artwork | Exported for reference; not bundled in the app |

Open `qa/figma-source/index.html` for the reference pack. `manifest.json` records version, source node IDs, layout/render bounds, dimensions, and SHA-256 hashes. Four frame renders, four artwork nodes, and one original image fill decoded successfully. The sample camera image is reference-only. Refresh with `python scripts/export_thesis_figma.py`; it reads the existing private token without copying it into outputs. The script requires Pillow.

## Implemented behavior and deliberate differences

- Black canvas, #121212 panels, #FFD700 actions, bundled licensed Inter Regular/Bold, 64dp-minimum primary control, 16dp spacing, and scrollable large-text layout.
- Compact source-style offline header and PATH / IDLE or PATH / LIVE row. GPS is explicitly marked In development. Idle, starting, live, stopping, and camera/model error presentation. Errors remain readable and the primary action remains reachable.
- Real camera stays contained within screen margins using the existing preview/box transform. Yellow detection outlines and opaque black labels; grouped class/direction/confidence semantics. No per-frame screen-reader live announcements. Extra visible processing counters and researcher readout cards were removed to preserve the Figma HUD composition.
- Existing detector, eight-class map, model weights, frame sampling, and Start/Stop callbacks are retained. The view is presentation-only; SessionScreen continues to own camera resources.
- All three source feedback controls are present: MUTE AUDIO, HAPTICS ON, and REPEAT LAST ALERT. Each displays In development and opens an informational dialog; HAPTICS ON is a source-design label, not a live on-state. Audio/haptics remain side by side at normal text size even on 320dp screens. They stack only for enlarged accessibility text. Repeat is a solid yellow button with a horizontal source-volume icon and label.
- Corrected the earlier source mismatch at the user's direction: removed the oversized idle heading/subheading and research-mode header, restored the pink-bordered source alert card with waveform and explicit Alerts in development copy, and restored LEFT/CENTER/RIGHT camera labels. Start/Stop is an accessible 64dp action inside the camera panel. The notice card remains removed. The camera stays contained; no fake chair, severity, distance, GPS lock, battery percentage, or log values are shown. No new permissions or backend.
- Exported CPU artwork is exact source artwork. Idle/loading and play/stop icons are native Flutter controls added for the research session. The result follows the source palette and accessibility guidance while preserving the accepted research layout; it is not a literal copy of the future alert HUD.

## Verification

Flutter analyzer and 13 tests passed, covering existing detector transforms, idle/compact layout, 390x844 and 320x700 at 100%/200% text, live fixture summaries, empty detections, disabled transition actions, Start/Stop callbacks, error presentation, grouped non-live detection semantics, and all three development-control dialogs and close paths. The live Figma HUD source version was rechecked and remained unchanged. Tests use synthetic preview/detection fixtures; they do not open the phone camera. Desktop screenshots are in `qa/path-ui/`; existing goldens were preserved.

Refresh screenshots with `flutter test --dart-define=CAPTURE_PATH_UI=true --concurrency=1` from `apps/mobile`. The regular suite does not write screenshots unless that flag is present.

## Phone verification pending

The user runs `flutter run` from `apps/mobile`. Verify camera permission denial/recovery, Start, real objects/box alignment, Stop, app background/return, repeated sessions, TalkBack traversal, 200% text with scroll-reachable controls, and system safe areas on the Infinix. No phone install, debug session, latency benchmark, or physical accessibility acceptance was performed in this pass. Processing time is not end-to-end alert latency. Source accessibility intent is not certification.

## Settings, accessibility and hazard log UI completion — 2026-11-10

HUD menu (top right) opens Settings & Accessibility or Hazard Log & GPS. Each screen has the Figma back control; Android Back also returns to the HUD. Navigating away stops an active camera session; returning does not silently restart it. The menu is an intentional native navigation addition because the supplied three frames do not specify entry controls.

Settings implements the source-selected delivery/direction pills, speech-rate 1.0–2.0 in 0.1 steps, cooldown 0.5–3.0 in 0.5 steps, and Stairs/Vehicles/Pedestrians switches. Selections save locally under the versioned `path.accessibility.v1` preference key using the Flutter-compatible pinned shared_preferences 2.5.3 dependency. Writes are serialized. These selections configure the UI for future alert integration; they do not enable speech, haptics, distance, category filtering, or direction-format conversion in the detector. The Settings page itself follows source copy without an added development subtitle.

Hazard Log implements the Figma location panel, event counter, severity/icon card layout, Clear log with Undo, and Cancel alert control. The production route has no recorded events. Its three source-shaped placeholder cards are explicitly titled In development and announced as layout placeholders; no real object, distance, time, or location values are fabricated. Sample populated event cards exist only in test fixtures and their screenshots. Clear/Undo operates on supplied UI entries; real history capture/storage is not connected.

The refreshed source pack contains four full-frame references, eight artwork nodes, and one original fill. Back (`2:1989`), map pin (`2:2004`), warning (`2:1983`), caution (`2:2010`), and safe (`2:2013`) use actual exported PNG artwork. Settings, log, and navigation screenshots are under `qa/path-ui/`. Full normal/compact and 200% text checks include scrolling, settings persistence, selection/switch/slider interactions, load-error recovery, log clear/undo, development dialogs, source button placement, Back navigation, and semantics. Physical-device TalkBack, actual app restart persistence, and camera-to-navigation behavior remain phone checks.

Because a native preferences plugin was added, stop the existing Flutter run and start `flutter run` again to register it; hot reload alone may not register the new plugin. Do not reset phone app data as part of this UI check.

## Settings contrast and failure-state correction — 2026-11-10

The supplied phone screenshots showed failed storage loading disabling the entire Settings page, causing gray controls and poor selected-text contrast. Storage failure now leaves session preferences interactive. A temporary SnackBar reports that changes apply only to this session and offers Retry saving; permanent load-error, Retry/Reset rows, and the extra In development subtitle were removed from the page. This does not prove native persistence is functioning on the phone; the plugin must be registered by a fresh Flutter run.

Live source version remained `2419075896925554276`. Source fidelity corrections include 12px top padding, source section gaps, 18px section labels with 22px line height, 20px slider labels with 24px line height, 64px delivery pills, 72px direction pills, 24px yellow thumbs, #B3B3B3 inactive tracks without extra tick marks, black-on-yellow selections, white category labels, and source-sized ON badges. The checkmark comes from exact nodes `2:1992` / `2:1993` stroke geometry, saved as SVG and compiled to a native Flutter path using `scripts/prepare_figma_check.py`. This bypasses the Figma image-export quota without substituting artwork; raw geometry and SVG are in `qa/figma-source/`.

Regression checks include unavailable storage and corrupt stored settings, continued selection/slider/switch interaction, selected and unselected label contrast of at least 7:1, normal and compact rendering, and 200% text. Phone persistence and TalkBack verification remain pending.

## Settings fit on the Note 40 viewport — 2026-11-10

Read-only device queries returned 1080x2436 at 480dpi and font scale 0.85, corresponding to a 360x812 logical test viewport. Settings now uses compact spacing when its safe-area height is below 800dp at ordinary text sizes: smaller header/section/label gaps, 64dp direction choices, and reduced outer vertical padding. All controls remain at least 64dp tall; adjacent hazard rows and choices keep 16dp separation. The 390x844 source-size layout retains its original spacing, and enlarged accessibility text retains scrolling instead of forced shrinking.

New tests verify that the complete Pedestrians control is visible without scrolling at 360x812 with 28dp top and 24dp bottom system-bar allowances, at both 85% and 100% text scaling. These allowances are test fixtures, not an on-device inset measurement. Rendered checks are `qa/path-ui/settings-phone-85.png` and `settings-phone-100.png`. No app install, launch, phone setting change, or live phone interaction was performed.

## Hazard Log source-fidelity correction — 2026-11-10

Rechecked live Figma node `2:1734`; source version remained `2419075896925554276`. Replaced the oversized empty panel with three source-style DANGER, CAUTION, SAFE card placeholders using the exported icons. Each reads In development with unavailable distance/direction and time; the event counter remains 0. Screen-reader labels explicitly identify layout placeholders, not live hazards. Actual supplied events replace the placeholders and retain clear/undo behavior.

Matched source geometry and type: 12px outer top padding, 100px location panel, 18px/22px feed heading, 8px feed gap, 124px cards with 36px icon wells and 28px artwork, 5px detail gaps, 14px severity/time, 24px object title, 20px detail, and two equal 64px action buttons. The phone compact mode uses 92px location and 112px cards while preserving readable content and touch targets. Clear log is full-contrast and explains that no detections are saved when tapped on the placeholder state. Cancel alert opens its development explanation; extra button subtitles were removed. The source-positioned shake hint remains marked In development because gestures are not implemented.

Verified source-size, compact, and 200% text layouts, actual action/dialog clicks, placeholder semantics/data honesty, clear/undo with supplied fixture entries, and control fit at 360x812 with system-bar allowances and 85% text. Preview: `qa/path-ui/hazard-phone-85.png`. Runtime GPS/history recording, shake gestures, alert cancellation, and physical-phone acceptance remain pending.

## Hazard Log Figma sample preview — 2026-11-10

At the user's request to remove the remaining design differences, the HUD Hazard Log route now explicitly opens `HazardLogScreen(previewMode: true)`. This mode uses the exact Figma sample address, ±5m context, Chair/Pedestrian/Vehicle events, 1.2m/2.4m/4.8m details, source timestamps, and source gesture-hint copy. A visible PREVIEW badge and screen-reader descriptions identify the data as examples. These values are never read from or written to live GPS/history. At enlarged text sizes the preview label moves before the header so it remains visible before sample location data.

Preview mode preserves the original 100dp location panel, 124dp cards, and source gaps instead of compacting them; short viewports scroll naturally. Clear/Undo changes only the in-memory sample list. Alert cancellation and shake detection remain unconnected despite the reference hint shown in this design preview. The non-preview empty-data UI remains available for future live history integration. The latest full-screen reference is `qa/path-ui/hazard-log-route.png`.

Verification includes source sample values, explicit preview labeling at 390x844, 360x812 and 320x700/200% text, original card dimensions, source hint, and preview-only Clear/Undo. Phone acceptance is pending.

## Detection speech integration 2026-11-10

This supersedes the earlier development-only audio entries. The HUD now displays speech state or the last detection announcement, and Mute/Unmute and Repeat last alert invoke actual speech behavior. Their development subtitles were removed; haptics retains its development explanation. The source palette, paired feedback controls, camera containment and large-text reflow are preserved.

`DetectionSpeech` announces one highest-confidence enabled object and its image direction, without distance or danger claims. Delivery mode, speech rate, cooldown, coarse clock/three-zone direction and category settings affect speech. Busy frames are dropped with no speech queue; cooldown starts at utterance completion. Repeat is disabled while muted, stopped, busy or without a previous message. Stop, backgrounding, HUD navigation and disposal cancel playback; pending initialization/configuration cannot revive an old utterance. The adapter selects an English voice explicitly reported as not requiring a network connection, and exposes unavailable/playback errors. Offline engine playback still needs physical verification.

Direction now uses the inverse-letterboxed preview box, after class-wise NMS in model space. Portrait side padding no longer shifts left/right objects into the center zone; the right third includes the exact two-thirds boundary. Detector weights and confidence/NMS settings are unchanged. Camera initialization also checks cancellation before publishing a live session.

Verification: 53 Flutter tests passed, analyzer reported no issues, and a local Android debug APK compiled successfully. Tests cover direction regression cases, speech selection/settings, cooldown, no queue, mute/repeat, offline-voice metadata, error reporting and cancellation. The functional audio screenshot is `qa/path-ui/audio-live-controls.png`; existing goldens were preserved. The APK was not installed or launched. Infinix speaker output, offline playback, intelligibility, Stop/background cancellation timing and TalkBack coexistence remain pending. Manual phone steps are in `apps/mobile/README.md`.

## Multiple object speech summaries 2026-11-10

The user reported the first audio feature working and requested multiple-object announcements. This supersedes the single-object selection above. Enabled detections are grouped by class and image direction within one frame, with counts such as "2 people, ahead. bicycle, left." Groups are ordered by highest confidence with deterministic ties. Up to three groups are named; any remaining detections are disclosed as "N more objects." This bound keeps one utterance short rather than queuing every frame. Counts refer to post-NMS detections, not tracked identities; person-plus-bicycle detections do not establish a riding relationship. Repeat replays the entire summary, and settings, cooldown and cancellation still apply.

Verification: 62 Flutter tests passed and the analyzer reported no issues. New cases cover multiple people, separate directions, mixed classes, plural forms, frame-local counts, remaining-object counts, full-summary repeat, clock labels, category filtering and invalid inputs. The summary fits normal text and reflows at 200 percent with reachable controls. Screenshot: `qa/path-ui/audio-multiple-controls.png`. Multi-object physical playback remains pending; no phone session or installation was started by the agent.

## Temporal scene announcements and on demand details 2026-11-10

This supersedes the continuously repeated per-frame summary above. Basic same-class IoU association confirms a detection after two consecutive observations, tolerates one missed frame, stabilizes direction over two observations, and expires tracks after two misses or a 1.5 second gap. It does not guarantee identity through crossings. Automatic speech reports at most two changed class/direction/count groups and stays quiet for an unchanged scene. Confidence ordering remains a baseline rather than validated hazard priority.

The authorized additions to the source HUD are Describe scene and conditional More details controls, using the existing native button style and minimum 64 dp touch targets. Details read up to three groups per page; remaining groups can all be requested. Paging ignores confidence reordering and restarts explicitly when scene content changes. Repeat identifies its output as a historical announcement. The HUD labels message text Last spoken, so an earlier utterance is not presented as current detection data.

Tracking refreshes during playback, mute and cooldown without queueing utterances. Freshness uses the monotonic callback timestamp before inference; stale results older than two seconds and out-of-order results are rejected. Scene content/freshness is checked again after rate configuration. Stop, backgrounding, navigation and disposal invalidate pending work and reset scene state. Storage-only settings notifications do not restart scene announcements or discard paging. Confirmation and freshness bounds are research parameters and add latency; they do not establish the 500 ms alert target.

Verification: 89 Flutter tests passed, analyzer reported no issues, and the final Android debug APK compiled. Cases include occlusion/count/direction, meaningful changes, complete paging, stale inference/configuration, settings notifications, cancellation and normal/200 percent control reflow. Visual captures: `qa/path-ui/scene-details-1x.png` and `scene-details-2x.png`. The APK was not installed or launched. Phone verification of the new policy remains pending. The previous user confirmation covers initial audio only. Haptics, metric/near-far depth calibration and hazard-priority effectiveness remain separate pending features.

## Approved camera first HUD 2026-11-10

The user explicitly approved a new generated camera-first concept, replacing the earlier HUD composition while retaining PATH branding, Inter typography and the Figma palette. Approved reference: `qa/design-concepts/path-camera-first-approved.png`. Settings and Hazard Log keep their existing layout. The new HUD removes the pink standalone message card and fixed LEFT/CENTER/RIGHT headings, provides a large camera area, and places direction on each object label such as PERSON · AHEAD. Confidence remains in grouped detection semantics instead of the visible box label.

The complete oriented camera image is fitted proportionally using contain geometry. Native camera content and the detection overlay share the exact fitted plane; text is drawn in display logical pixels rather than scaled down with sensor pixels. Black object labels wrap up to two lines at enlarged text sizes, stay inside the fitted plane and try alternate positions to reduce collisions. The compact message overlay is tappable for full text and moves into document flow at enlarged text sizes. It makes no danger or distance claims.

The dock contains a yellow primary action and Mute/Repeat/Stop controls. Idle primary action starts the camera; live primary action describes the scene, then becomes More details while paging remains. The menu can restart Describe scene and retains Settings, Hazard Log and the unfinished Haptics explanation. Speech/tracking, model weights, sampling, cancellation and existing navigation behavior are preserved. Normal-size controls fit without scrolling at 390x844 and 320x700; enlarged text and short screens reflow into a scrollable layout. Camera-panel height exceeds 60 percent of those normal test viewports; actual image extent depends on the camera aspect ratio and letterboxing.

Verification: 94 Flutter tests passed, analyzer reported no issues and the Android debug APK compiled. Checks include proportional portrait/landscape fit, aligned overlay dimensions, class-and-direction labels, normal-view control reachability and 64 dp targets, 200 percent reflow, full-message dialog, menu navigation, primary-action paging and the entire existing speech suite. Existing golden images were preserved. Desktop fixture captures: `qa/path-ui/camera-first-live-390.png` and `camera-first-live-320.png`; these contain synthetic detections, not phone inference evidence. Real-phone camera framing, sensor rotation, label placement and TalkBack acceptance remain pending. No installation or phone run was started.

## Native haptic detection feedback 2026-11-10

This supersedes the unfinished haptics entries above. The camera-first menu now contains a checked Haptics on/off item with capability/status text. The preference persists with the existing settings data; older stored data defaults to enabled. Voice Only suppresses vibration and disables the quick toggle. Haptic Only skips voice-engine initialization and delivers vibration without speech, provided its saved haptics toggle is enabled. Voice + Haptic uses both outputs. Muting audio leaves haptics available, while the menu toggle affects vibration only.

`DetectionHaptics` consumes the same confirmed scene as speech through a stable-scene observer, with a shared monotonic time domain. It sends one neutral 120 ms default-amplitude pulse for a changed scene rather than one pulse per object. It suppresses unchanged/empty scenes, stale/out-of-order observations, disabled categories and updates inside the saved cooldown. Its cooldown starts at pulse dispatch independently from spoken completion. No class, direction, distance or danger pattern is encoded. Describe/More/Repeat remain spoken controls.

The Android activity implements app-owned `path/haptics` capability/pulse/cancel methods using the platform vibrator, with the normal VIBRATE permission. No new plugin, SDK upgrade, repeating effect or vibration timer was added. Stop, menu navigation, lifecycle pause and disposal cancel output; native activity pause/destruction adds a second cancellation path. Capability checks cannot revive a stopped session. Voice and haptic errors are independent, so an unavailable voice engine or vibrator does not disable the other channel. Device capability is separate from a perceptible physical pulse.

Verification: 117 Flutter tests passed, analyzer reported no issues and the native Android debug APK compiled. New cases cover all three delivery modes, meaningful changes/cooldown, category and freshness filters, independent audio mute, saved on/off, legacy settings, unavailable hardware, voice/haptic failure independence, initialization cancellation, native channel request order and menu behavior. Popup fixture: `qa/path-ui/haptics-menu-on.png`. Existing golden images were preserved. The native change requires fully stopping and rerunning flutter run; hot reload or Dart restart alone is insufficient. Actual vibration strength, timing, phone settings, background cancellation and usability remain pending physical verification. No APK installation or phone session was started.

## Vibration usage correction after phone report 2026-11-10

The user reported no physical vibration. Read-only ADB inspection on the connected Infinix X6853 (Android API 36) confirmed the newly installed package, granted VIBRATE permission and actual PATH one-shot requests. Android's vibrator service recorded these 120 ms requests as TOUCH with ignored_for_settings and no playback. Its intensity settings showed TOUCH OFF and ACCESSIBILITY MEDIUM. This establishes that the initial request reached Android but was suppressed, rather than a missing native build or absent detection callback.

The native pulse now supplies VibrationAttributes.USAGE_ACCESSIBILITY on API 33+, and AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY on older supported versions. The neutral duration, default amplitude, app toggles and cancellation remain unchanged. No phone settings, DND policy, global vibration values or bypass flags were changed. Compilation verifies API compatibility; installation of this corrected build and a new observed ACCESSIBILITY vibration-service record are still required before calling physical vibration fixed. Phone installation/launch remains user-controlled.

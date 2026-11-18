# PATH quick guide

Group 8 Android research prototype | Progress as of November 19, 2026

**Choose Test to try alerts right away. Choose Live to study how well measured distance zones work.** Both modes use the phone camera. Only the researcher collecting calibration samples needs a tape measure.

## Start the app

1. Connect the Android phone by USB or paired wireless debugging.
2. From the repository root, run the commands below. If Flutter asks for a device, choose the Infinix.
3. Open **⋮ → Accessibility & Alerts → Mode**. Choose **Test** or **Live**, tap **Back**, then **Start camera session**. Choose **Voice & Haptic** to hear speech and feel vibration.

```powershell
cd apps/mobile
flutter run
```

## Test or Live?

| Question | Test | Live |
| --- | --- | --- |
| What am I checking? | Do the warning, vibration, and priority controls work? | Does the depth estimate match the object's physical distance zone? |
| What triggers Danger? | An object labeled both **AHEAD** and **CLOSER**. | Its depth score falls in the measured Danger range for its object class. |
| What triggers Caution? | An object ahead, or a closer object on the left or right, when no Danger takes priority. | Its score falls in the measured Caution range. |
| What about Farther? | Open **⋮ → Zone test → Farther → Start test** to try the quiet result. An unmatched camera rule shows **No test alert**. | A Farther estimate gives no urgent alert. Without usable references, the zone is **Unknown**. |
| Do I enter centimeters? | No. | Only during calibration. Using the camera afterward requires no typing. |

**Example.** One chair straight ahead triggers Test Caution. In Live, you can still hear “chair, ahead” without calibration. Its direction alone cannot establish a measured zone.

**Top alert** is the first alert PATH acts on. Danger interrupts Caution. With Voice & Haptic enabled, Danger gives urgent speech and three pulses. Caution gives caution speech and one pulse. **Stop** ends the session. A frame older than two seconds cannot issue a new priority warning.

**CLOSER** compares objects within the same frame. A higher relative depth score means the object appears closer. The score has no centimeter unit.

## Collect a measured sample

1. Position a real object according to the team's study protocol. Measure from the camera to the selected object in centimeters.
2. Start the camera. Tap the **ruler** in the Relative depth panel. Use the frozen color image and yellow box to check the selected object.
3. Enter the measured distance. Open **Physical zone reference**, choose **Danger**, **Caution**, or **Farther**, and tap **Save sample**.
4. Collect references for all three zones for the same object class. Start a new session and evaluate a separate scene. Overlapping, incomplete, or out-of-range readings cannot support a confident estimate.

The first 100 cm monitor entry was a practice sample. Leave practice entries untagged. Physical validation needs multiple measured scenes and a separate evaluation set.

## Review or export alerts

Open **⋮ → Hazard Log** to see the newest alert first. Each entry shows Test or Live, severity, object, direction, and local time. **Clear log** offers **Undo**.

Tap **Export CSV**, choose a folder in Android's file picker, then tap **Save**. The CSV has one row per alert and uses UTC timestamps. Exporting keeps the saved history. After an Android native-code update, stop the old Flutter session and run `flutter run` again to install the updated build.

## What is done?

| Feature | Current evidence | Still pending |
| --- | --- | --- |
| Camera, detection, directions, Start/Stop | Confirmed on the Infinix with chair and person scenes. | Broader accuracy testing, including missed and duplicate boxes. |
| Depth preview and CLOSER | Relative depth, object labels and matching announcement text observed on phone. | Independent physical depth checks. |
| Test priority alerts | Caution and Danger displayed. Danger speech and three pulses confirmed on phone. | On-phone check of the selectable quiet Farther case. |
| Calibration and Live zones | Save and reopen confirmed on phone. Three-zone estimator tested in software. | Real tagged references and held-out accuracy evaluation. |
| Hazard Log and CSV | Saved alerts persisted after restart. CSV export confirmed on phone. | Optional GPS and location export deferred. |
| Accessibility and performance | Basic speech and vibration confirmed. Some debug frames exceeded two seconds. | TalkBack, offline speech, mounted endurance, and capture-to-feedback timing. |

**Thesis status.** The alert demonstration works. Claims about real danger distance or walking assistance still require physical evaluation. See the [phase requirements](Assistive_Navigation_PRD.md) and [mobile implementation notes](../../apps/mobile/README.md).

import 'dart:async';
import 'detector.dart';

import 'package:flutter/material.dart';

import 'android_haptic_output.dart';
import 'detection_haptics.dart';
import 'detection_speech.dart';
import 'flutter_speech_output.dart';
import 'path_preferences.dart';
import 'zone_preview.dart';

typedef AlertObject = ({ResearchZone zone, String label, String direction});

// Explicit demonstration rules; these do not estimate physical distance.
List<AlertObject> liveRuleCandidates(Iterable<Detection> objects) {
  final result = <AlertObject>[];
  for (final d in objects) {
    if (!d.closer && d.direction != 'ahead') continue;
    result.add((
      zone: d.closer && d.direction == 'ahead'
          ? ResearchZone.danger
          : ResearchZone.caution,
      label: d.label,
      direction: d.direction,
    ));
  }
  return result..sort((a, b) => a.zone.index.compareTo(b.zone.index));
}

class PriorityAlertOutput {
  PriorityAlertOutput(this.voice, this.haptics);
  final SpeechOutput voice;
  final HapticOutput haptics;
  int generation = 0;
  AlertObject? _last;

  void invalidate() {
    generation++;
    _last = null;
  }

  Future<void> stop() async {
    invalidate();
    await Future.wait([voice.stop(), haptics.cancel()]);
  }

  Future<void> present(
    List<AlertObject> scene,
    PathPreferences preferences,
    void Function(String) show, {
    required bool vibration,
    required bool voiceEnabled,
    bool rulePreview = false,
  }) async {
    final candidates =
        scene.where((o) => o.zone != ResearchZone.farther).toList()
          ..sort((a, b) => a.zone.index.compareTo(b.zone.index));
    final target = candidates.firstOrNull;
    if (target == _last) return;
    final token = ++generation;
    final previous = _last;
    _last = target;
    if (previous != null) await Future.wait([voice.stop(), haptics.cancel()]);
    if (token != generation || target == null) return;
    final direction = preferences.direction == DirectionFormat.clockHand
        ? switch (target.direction) {
            'left' => "at 10 o'clock",
            'right' => "at 2 o'clock",
            _ => "at 12 o'clock",
          }
        : target.direction == 'ahead'
        ? 'directly ahead'
        : 'on the ${target.direction}';
    final prefix = target.zone == ResearchZone.danger ? 'Warning' : 'Caution';
    final message =
        '${rulePreview ? 'Test. ' : ''}$prefix. ${target.label} $direction.';
    show(message);
    Future<void> pulses() async {
      final count = target.zone == ResearchZone.danger ? 3 : 1;
      for (var i = 0; i < count; i++) {
        if (token != generation) return;
        await haptics.pulse();
        if (i + 1 < count) {
          await Future<void>.delayed(const Duration(milliseconds: 240));
        }
      }
    }

    try {
      await Future.wait([
        if (voiceEnabled) voice.speak(message),
        if (vibration) pulses(),
      ]);
    } catch (_) {
      if (token == generation) rethrow;
    }
  }
}

class DangerDemoScreen extends StatefulWidget {
  const DangerDemoScreen({
    super.key,
    required this.preferences,
    required this.muted,
  });
  final PathPreferences preferences;
  final bool muted;
  @override
  State<DangerDemoScreen> createState() => _DangerDemoScreenState();
}

class _DangerDemoScreenState extends State<DangerDemoScreen>
    with WidgetsBindingObserver {
  final output = PriorityAlertOutput(
    FlutterSpeechOutput(),
    AndroidHapticOutput(),
  );
  int run = 0;
  bool playing = false, stopping = false;
  String status = 'Ready';
  ResearchZone? selectedCase;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed && playing) unawaited(_stop());
  }

  Future<void> _stop() async {
    ++run;
    setState(() {
      playing = false;
      stopping = true;
      status = 'Stopped';
    });
    try {
      await output.stop();
    } catch (_) {
      if (mounted) setState(() => status = 'Could not confirm output stopped.');
    } finally {
      if (mounted) setState(() => stopping = false);
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    ++run;
    unawaited(output.stop().catchError((Object _) {}));
    super.dispose();
  }

  Future<void> _play() async {
    if (playing || stopping) return;
    final id = ++run;
    final prefs = widget.preferences;
    bool current() => mounted && id == run;
    void show(String text) {
      if (current()) setState(() => status = text);
    }

    setState(() {
      playing = true;
      status = 'Preparing test';
    });
    try {
      if (selectedCase == ResearchZone.farther) {
        await output.present(
          const [
            (zone: ResearchZone.farther, label: 'Chair', direction: 'ahead'),
          ],
          prefs,
          show,
          vibration: true,
          voiceEnabled: true,
        );
        show('Test Farther. No urgent alert.');
        return;
      }
      output.invalidate();
      final useVoice =
          prefs.delivery != AlertDelivery.hapticOnly && !widget.muted;
      final useHaptics =
          prefs.delivery != AlertDelivery.voiceOnly &&
          prefs.hapticsEnabled &&
          await output.haptics.prepare();
      if (!current()) return;
      if (!useVoice && !useHaptics) {
        show('Enable speech or vibration to run the test.');
        return;
      }
      if (useVoice) {
        await output.voice.prepare();
        if (!current()) return;
        await output.voice.setRate(prefs.speechRate);
      }
      if (!current()) return;
      const person = (
        zone: ResearchZone.caution,
        label: 'Person',
        direction: 'right',
      );
      const chair = (
        zone: ResearchZone.danger,
        label: 'Chair',
        direction: 'ahead',
      );
      Future<void> send(List<AlertObject> scene) => output.present(
        scene,
        prefs,
        show,
        vibration: useHaptics,
        voiceEnabled: useVoice,
      );
      if (selectedCase != null) {
        if (current()) {
          await send([selectedCase == ResearchZone.danger ? chair : person]);
        }
        return;
      }
      await Future.wait([
        send([person]),
        () async {
          await Future<void>.delayed(const Duration(milliseconds: 900));
          if (current()) await send([person, chair]);
          if (current()) await send([person, chair]);
        }(),
      ]);
    } catch (_) {
      if (current()) {
        await _stop();
        if (mounted) {
          setState(
            () => status =
                'Feedback unavailable. Check voice and vibration settings.',
          );
        }
      }
    } finally {
      if (current()) setState(() => playing = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Zone test')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Simulated scene',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: selectedCase?.name ?? 'sequence',
            decoration: const InputDecoration(labelText: 'Test case'),
            items: [
              const DropdownMenuItem(
                value: 'sequence',
                child: Text('Caution to Danger'),
              ),
              for (final zone in ResearchZone.values)
                DropdownMenuItem(value: zone.name, child: Text(zone.title)),
            ],
            onChanged: playing || stopping
                ? null
                : (value) => setState(() {
                    selectedCase = ResearchZone.values
                        .where((z) => z.name == value)
                        .firstOrNull;
                    status = 'Ready';
                  }),
          ),
          const SizedBox(height: 12),
          if (selectedCase == null)
            const Text(
              'A person is on the right in the caution zone. A chair then enters the danger zone directly ahead. With vibration enabled, caution gives one pulse and danger gives three.',
            ),
          const SizedBox(height: 24),
          Text(status, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: playing || stopping || !widget.preferences.ready
                ? null
                : _play,
            child: const Text('Start test'),
          ),
          OutlinedButton(
            onPressed: playing ? _stop : null,
            child: const Text('Stop test'),
          ),
        ],
      ),
    ),
  );
}

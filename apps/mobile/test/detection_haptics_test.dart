import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:thesis_navigation/detection_haptics.dart';
import 'package:thesis_navigation/detection_speech.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/path_preferences.dart';
import 'detection_speech_test.dart' show FakeSpeech;

class FakeHaptics implements HapticOutput {
  int pulses = 0, cancels = 0, probes = 0;
  bool supported = true, fail = false;
  Completer<bool>? preparation;
  Completer<void>? playback;
  @override
  Future<bool> prepare() async {
    probes++;
    return preparation == null ? supported : await preparation!.future;
  }

  @override
  Future<void> pulse() async {
    if (fail) throw StateError('hardware failure');
    pulses++;
    await playback?.future;
  }

  @override
  Future<void> cancel() async {
    cancels++;
  }
}

const person = Detection('person', .95, 'ahead', [.4, .1, .6, .8]);
const chair = Detection('chair', .9, 'left', [.1, .1, .3, .8]);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late FakeHaptics output;
  late PathPreferences prefs;
  late DetectionHaptics haptics;
  late DateTime now;
  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    output = FakeHaptics();
    prefs = PathPreferences();
    await prefs.load();
    now = DateTime(2026);
    haptics = DetectionHaptics(
      output: output,
      preferences: prefs,
      now: () => now,
    );
  });
  tearDown(() {
    haptics.dispose();
    prefs.dispose();
  });
  Future<void> scene(List<Detection> stable, {int ms = 500}) async {
    now = now.add(Duration(milliseconds: ms));
    await haptics.consider(stable, now);
  }

  test(
    'one neutral cue per meaningful scene change, not per object or frame',
    () async {
      await haptics.start();
      await scene([person, chair]);
      for (var i = 0; i < 5; i++) {
        await scene([chair, person]);
      }
      expect(output.pulses, 1);
      await scene([chair]);
      await scene([person, chair]);
      expect(output.pulses, 2);
    },
  );
  test(
    'cooldown applies to changed scenes and honors its exact boundary',
    () async {
      prefs.cooldown = 1.5;
      await haptics.start();
      await scene([person]);
      await scene([person, chair], ms: 1499);
      expect(output.pulses, 1);
      await scene([person, chair], ms: 1);
      expect(output.pulses, 2);
    },
  );
  test('voice-only suppresses vibration and capability probing', () async {
    prefs.delivery = AlertDelivery.voiceOnly;
    await haptics.start();
    await scene([person]);
    expect(output.probes, 0);
    expect(output.pulses, 0);
    expect(haptics.canToggle, isFalse);
  });
  test('haptic-only works independently from the voice engine', () async {
    prefs.delivery = AlertDelivery.hapticOnly;
    await haptics.start();
    await scene([person]);
    expect(output.pulses, 1);
    expect(haptics.ready, isTrue);
  });
  test('category filters and empty scenes do not generate cues', () async {
    prefs.pedestrians = false;
    await haptics.start();
    await scene([person]);
    await scene([]);
    expect(output.pulses, 0);
    await scene([chair]);
    expect(output.pulses, 1);
  });
  test('stale and out-of-order snapshots never cue', () async {
    await haptics.start();
    final old = now;
    now = now.add(const Duration(seconds: 3));
    await haptics.consider([person], old);
    expect(output.pulses, 0);
    await scene([person]);
    await haptics.consider([chair], old);
    expect(output.pulses, 1);
  });
  test(
    'unavailable hardware is reported without crashing or retrying frames',
    () async {
      output.supported = false;
      await haptics.start();
      await scene([person]);
      await scene([chair]);
      expect(haptics.error, contains('unavailable'));
      expect(output.pulses, 0);
      expect(output.probes, 1);
    },
  );
  test(
    'playback failure disables cues and exposes a recoverable status',
    () async {
      output.fail = true;
      await haptics.start();
      await scene([person]);
      await scene([chair]);
      expect(haptics.ready, isFalse);
      expect(haptics.error, contains('playback failed'));
    },
  );
  test('Stop during capability probing cannot revive feedback', () async {
    output.preparation = Completer<bool>();
    final start = haptics.start();
    await haptics.stop();
    output.preparation!.complete(true);
    await start;
    await scene([person]);
    expect(haptics.ready, isFalse);
    expect(output.pulses, 0);
    expect(output.cancels, 1);
  });
  test(
    'saved toggle cancels current output and permits future cues after reenable',
    () async {
      await haptics.start();
      await scene([person]);
      await haptics.toggle();
      await Future<void>.delayed(Duration.zero);
      await scene([person, chair]);
      expect(output.cancels, 1);
      expect(output.pulses, 1);
      expect(prefs.hapticsEnabled, isFalse);
      await haptics.toggle();
      await scene([person, chair]);
      expect(output.pulses, 2);
    },
  );
  test(
    'switching to Voice Only cancels haptics without a replacement pulse',
    () async {
      await haptics.start();
      await scene([person]);
      prefs.update(delivery: AlertDelivery.voiceOnly);
      await Future<void>.delayed(Duration.zero);
      await scene([chair]);
      expect(output.cancels, 1);
      expect(output.pulses, 1);
    },
  );
  test(
    'Stop cancels pending output and restart clears the scene baseline',
    () async {
      output.playback = Completer<void>();
      await haptics.start();
      final playing = scene([person]);
      await Future<void>.delayed(Duration.zero);
      await haptics.stop();
      output.playback!.complete();
      await playing;
      output.playback = null;
      await scene([chair]);
      expect(output.pulses, 1);
      await haptics.start();
      await scene([person]);
      expect(output.pulses, 2);
    },
  );

  for (final mode in AlertDelivery.values) {
    test('integrated stable-scene delivery works in ${mode.name}', () async {
      prefs.delivery = mode;
      final voice = FakeSpeech();
      final speech = DetectionSpeech(
        output: voice,
        preferences: prefs,
        now: () => now,
        onStableScene: haptics.consider,
      );
      await haptics.start();
      await speech.start();
      await speech.consider([person]);
      now = now.add(const Duration(milliseconds: 500));
      await speech.consider([person]);
      await Future<void>.delayed(Duration.zero);
      expect(voice.messages.length, mode == AlertDelivery.hapticOnly ? 0 : 1);
      expect(output.pulses, mode == AlertDelivery.voiceOnly ? 0 : 1);
      speech.dispose();
    });
  }
  test('muting audio does not mute the independent haptic cue', () async {
    final voice = FakeSpeech();
    final speech = DetectionSpeech(
      output: voice,
      preferences: prefs,
      now: () => now,
      onStableScene: haptics.consider,
    );
    await haptics.start();
    await speech.start();
    await speech.toggleMute();
    await speech.consider([person]);
    now = now.add(const Duration(milliseconds: 500));
    await speech.consider([person]);
    await Future<void>.delayed(Duration.zero);
    expect(voice.messages, isEmpty);
    expect(output.pulses, 1);
    speech.dispose();
  });
  test('voice setup failure does not prevent vibration', () async {
    final voice = FakeSpeech()..initialization = Completer<void>();
    final speech = DetectionSpeech(
      output: voice,
      preferences: prefs,
      now: () => now,
      onStableScene: haptics.consider,
    );
    await haptics.start();
    final preparing = speech.start();
    voice.initialization!.completeError(StateError('no local voice'));
    await preparing;
    await speech.consider([person]);
    now = now.add(const Duration(milliseconds: 500));
    await speech.consider([person]);
    await Future<void>.delayed(Duration.zero);
    expect(speech.ready, isFalse);
    expect(output.pulses, 1);
    speech.dispose();
  });

  test('unavailable vibration does not prevent voice announcements', () async {
    output.supported = false;
    final voice = FakeSpeech();
    final speech = DetectionSpeech(
      output: voice,
      preferences: prefs,
      now: () => now,
      onStableScene: haptics.consider,
    );
    await haptics.start();
    await speech.start();
    await speech.consider([person]);
    now = now.add(const Duration(milliseconds: 500));
    await speech.consider([person]);
    expect(voice.messages, ['person, ahead.']);
    expect(output.pulses, 0);
    speech.dispose();
  });

  test(
    'turning haptics off during preparation does not issue a delayed cue',
    () async {
      output.preparation = Completer<bool>();
      final preparing = haptics.start();
      await haptics.toggle();
      await scene([person]);
      output.preparation!.complete(true);
      await preparing;
      await scene([person]);
      expect(output.pulses, 0);
      expect(prefs.hapticsEnabled, isFalse);
    },
  );
  test(
    'haptic preference persists and legacy data retains the enabled default',
    () async {
      prefs.update(hapticsEnabled: false);
      await prefs.save();
      final reloaded = PathPreferences();
      await reloaded.load();
      expect(reloaded.hapticsEnabled, isFalse);
      await reloaded.reset();
      expect(reloaded.hapticsEnabled, isTrue);
      reloaded.dispose();
      SharedPreferences.setMockInitialValues({
        PathPreferences.storageKey: '{"delivery":"hapticOnly"}',
      });
      final legacy = PathPreferences();
      await legacy.load();
      expect(legacy.hapticsEnabled, isTrue);
      legacy.dispose();
    },
  );
}

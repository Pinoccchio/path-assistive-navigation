import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detection_speech.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/path_preferences.dart';
import 'package:thesis_navigation/scene_tracker.dart';

class FakeSpeech implements SpeechOutput {
  final messages = <String>[];
  final rates = <double>[];
  int stops = 0;
  Completer<void>? initialization, configuration, playback;
  bool fail = false;
  @override
  Future<void> prepare() async {
    await initialization?.future;
  }

  @override
  Future<void> setRate(double rate) async {
    rates.add(rate);
    await configuration?.future;
  }

  @override
  Future<void> speak(String text) async {
    if (fail) throw StateError('engine error');
    messages.add(text);
    await playback?.future;
  }

  @override
  Future<void> stop() async {
    stops++;
  }
}

const chair = Detection('chair', .9, 'left', [.1, .1, .3, .8]);
const person = Detection('person', .95, 'ahead', [.4, .1, .6, .8]);

void main() {
  late FakeSpeech output;
  late PathPreferences prefs;
  late DetectionSpeech speech;
  late DateTime now;
  setUp(() {
    output = FakeSpeech();
    prefs = PathPreferences()..ready = true;
    now = DateTime(2026, 11, 10);
    speech = DetectionSpeech(
      output: output,
      preferences: prefs,
      now: () => now,
      // Formatting/cancellation in isolation; default tracking has its own tests.
      tracker: TemporalSceneTracker(confirmationFrames: 1, maxMissedFrames: 0),
    );
  });
  tearDown(() {
    speech.dispose();
    prefs.dispose();
  });

  test(
    'summarizes multiple objects ordered by confidence without distance',
    () async {
      await speech.start();
      await speech.consider([chair, person]);
      expect(output.messages, ['person, ahead. chair, left.']);
      expect(output.rates, [1.5]);
    },
  );

  test(
    'counts people in the same direction and keeps bicycle separate',
    () async {
      await speech.start();
      await speech.consider([
        person,
        const Detection('person', .88, 'ahead', [.7, .1, .9, .8]),
        const Detection('bicycle', .85, 'left', [.1, .2, .4, .8]),
      ]);
      expect(output.messages, ['2 people, ahead. bicycle, left.']);
    },
  );

  test('same class in different directions stays in separate groups', () async {
    await speech.start();
    await speech.consider([
      person,
      const Detection('person', .85, 'left', [.1, .1, .3, .8]),
      const Detection('person', .8, 'right', [.7, .1, .9, .8]),
    ]);
    expect(output.messages, ['person, ahead. person, left.']);
  });

  test('automatic speech stays bounded to two groups', () async {
    await speech.start();
    await speech.consider([
      person,
      chair,
      const Detection('bicycle', .85, 'left', [.1, .1, .3, .8]),
      const Detection('plant pot', .8, 'right', [.7, .1, .9, .8]),
      const Detection('plant pot', .7, 'right', [.75, .2, .95, .9]),
    ]);
    expect(output.messages, ['person, ahead. chair, left.']);
  });

  test('plural stairs and normal object plurals remain readable', () async {
    await speech.start();
    await speech.consider([
      chair,
      chair,
      const Detection('stairs', .85, 'ahead', [.1, .1, .4, .8]),
      const Detection('stairs', .8, 'ahead', [.6, .1, .9, .8]),
    ]);
    expect(output.messages, ['2 chairs, left. 2 sets of stairs, ahead.']);
  });

  test(
    'summary uses latest frame counts instead of accumulating people',
    () async {
      await speech.start();
      await speech.consider([person, person]);
      now = now.add(const Duration(seconds: 2));
      await speech.consider([person]);
      expect(output.messages, ['2 people, ahead.', 'person, ahead.']);
    },
  );

  test('repeat replays the complete multi-object summary', () async {
    await speech.start();
    await speech.consider([person, chair]);
    await speech.repeat();
    expect(output.messages, [
      'person, ahead. chair, left.',
      'Last announcement: person, ahead. chair, left.',
    ]);
  });

  test(
    'clock directions apply to all groups and disabled vehicles are omitted',
    () async {
      prefs.direction = DirectionFormat.clockHand;
      prefs.vehicles = false;
      await speech.start();
      await speech.consider([
        person,
        chair,
        const Detection('bicycle', .99, 'right', [.7, .1, .9, .8]),
      ]);
      expect(output.messages, ["person, 12 o'clock. chair, 10 o'clock."]);
    },
  );

  test(
    'non-finite confidence, unknown labels and directions are not spoken',
    () async {
      await speech.start();
      await speech.consider([
        const Detection('person', double.nan, 'ahead', [.1, .1, .4, .8]),
        const Detection('person', 2, 'ahead', [.1, .1, .4, .8]),
        const Detection('unknown', .9, 'left', [.1, .1, .4, .8]),
        const Detection('chair', .9, 'unknown', [.1, .1, .4, .8]),
      ]);
      expect(output.messages, isEmpty);
    },
  );

  test('silence for empty, invalid and disabled categories', () async {
    prefs.pedestrians = prefs.vehicles = prefs.stairs = false;
    await speech.start();
    await speech.consider([]);
    await speech.consider([
      person,
      const Detection('stairs', .9, 'ahead', [.1, .1, .5, .5]),
      const Detection('car', .9, 'ahead', [.1, .1, .5, .5]),
      const Detection('chair', .2, 'ahead', [.1, .1, .5, .5]),
      const Detection('chair', .9, 'ahead', [0, 0, 0, 0]),
    ]);
    expect(output.messages, isEmpty);
    await speech.consider([person, chair]);
    expect(output.messages, ['chair, left.']);
  });

  test('busy frames are dropped rather than queued', () async {
    output.playback = Completer<void>();
    await speech.start();
    final first = speech.consider([chair]);
    await Future<void>.delayed(Duration.zero);
    await speech.consider([person]);
    expect(output.messages, ['chair, left.']);
    output.playback!.complete();
    await first;
    expect(output.messages.length, 1);
  });

  test('cooldown begins when the previous utterance finishes', () async {
    prefs.cooldown = 1.5;
    await speech.start();
    await speech.consider([chair]);
    now = now.add(const Duration(milliseconds: 1499));
    await speech.consider([person]);
    expect(output.messages.length, 1);
    now = now.add(const Duration(milliseconds: 1));
    await speech.consider([person]);
    expect(output.messages.length, 2);
  });

  test('mute interrupts and unmute permits future detection speech', () async {
    await speech.start();
    await speech.toggleMute();
    await speech.consider([chair]);
    expect(output.messages, isEmpty);
    expect(output.stops, 1);
    await speech.toggleMute();
    await speech.consider([chair]);
    expect(output.messages, ['chair, left.']);
  });

  test(
    'repeat is explicit, bypasses cooldown, and is cleared on Stop',
    () async {
      await speech.start();
      await speech.repeat();
      expect(output.messages, isEmpty);
      await speech.consider([chair]);
      await speech.repeat();
      expect(output.messages, [
        'chair, left.',
        'Last announcement: chair, left.',
      ]);
      await speech.stop();
      await speech.repeat();
      await speech.consider([person]);
      expect(output.messages.length, 2);
      expect(speech.canRepeat, isFalse);
    },
  );

  test('haptic-only delivery never speaks', () async {
    prefs.delivery = AlertDelivery.hapticOnly;
    await speech.start();
    await speech.consider([chair]);
    await speech.repeat();
    expect(output.messages, isEmpty);
  });

  test('clock direction uses coarse horizontal labels', () async {
    prefs.direction = DirectionFormat.clockHand;
    prefs.speechRate = 2;
    await speech.start();
    await speech.consider([chair]);
    expect(output.messages, ["chair, 10 o'clock."]);
    expect(output.rates, [2]);
  });

  test('Stop during engine initialization cannot revive speech', () async {
    output.initialization = Completer<void>();
    final start = speech.start();
    await speech.stop();
    output.initialization!.complete();
    await start;
    await speech.consider([chair]);
    expect(speech.ready, isFalse);
    expect(output.messages, isEmpty);
  });

  test('muting during initialization still allows later unmute', () async {
    output.initialization = Completer<void>();
    final start = speech.start();
    await speech.toggleMute();
    output.initialization!.complete();
    await start;
    await speech.toggleMute();
    await speech.consider([chair]);
    expect(output.messages, ['chair, left.']);
  });

  for (final cancel in ['stop', 'mute', 'dispose']) {
    test('$cancel cancels speech awaiting rate configuration', () async {
      output.configuration = Completer<void>();
      await speech.start();
      final pending = speech.consider([chair]);
      if (cancel == 'stop') await speech.stop();
      if (cancel == 'mute') await speech.toggleMute();
      // Use a separate controller to avoid disposing twice in tearDown.
      if (cancel == 'dispose') {
        final other = DetectionSpeech(
          output: output,
          preferences: prefs,
          tracker: TemporalSceneTracker(
            confirmationFrames: 1,
            maxMissedFrames: 0,
          ),
        );
        await other.start();
        final work = other.consider([person]);
        other.dispose();
        await speech.stop();
        output.configuration!.complete();
        await work;
        await pending;
      } else {
        output.configuration!.complete();
        await pending;
      }
      expect(output.messages, isEmpty);
    });
  }

  test('engine failure is visible and does not retry every frame', () async {
    output.fail = true;
    await speech.start();
    await speech.consider([chair]);
    expect(speech.error, contains('Voice playback failed'));
    expect(speech.ready, isFalse);
    await speech.consider([chair]);
    expect(output.rates.length, 1);
  });
}

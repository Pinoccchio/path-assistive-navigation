import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detection_speech.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/path_preferences.dart';
import 'detection_speech_test.dart' show FakeSpeech;

const person = Detection('person', .95, 'ahead', [.4, .1, .6, .8]);
const chair = Detection('chair', .9, 'left', [.1, .1, .3, .8]);
const scene = [
  person,
  chair,
  Detection('bicycle', .85, 'left', [.1, .2, .4, .9]),
  Detection('plant pot', .8, 'right', [.7, .1, .9, .8]),
  Detection('car', .75, 'right', [.6, .2, .9, .9]),
];

class NotifyingPreferences extends PathPreferences {
  void storageNotification() => notifyListeners();
}

void main() {
  late DetectionSpeech speech;
  late FakeSpeech output;
  late PathPreferences prefs;
  late DateTime now;
  setUp(() async {
    output = FakeSpeech();
    prefs = NotifyingPreferences()..ready = true;
    now = DateTime(2026);
    speech = DetectionSpeech(
      output: output,
      preferences: prefs,
      now: () => now,
    );
    await speech.start();
  });
  tearDown(() {
    speech.dispose();
    prefs.dispose();
  });
  Future<void> frame(List<Detection> boxes, {int ms = 500}) async {
    now = now.add(Duration(milliseconds: ms));
    await speech.consider(boxes);
  }

  Future<void> confirm(List<Detection> boxes) async {
    await frame(boxes);
    await frame(boxes);
  }

  test(
    'waits for stable detections then stays quiet for unchanged scene',
    () async {
      await frame([person]);
      expect(output.messages, isEmpty);
      await frame([person]);
      expect(output.messages, ['person, ahead.']);
      for (var i = 0; i < 10; i++) {
        await frame([person]);
      }
      expect(output.messages.length, 1);
    },
  );
  test(
    'manual comparison follows the current label and clears on tie or missed box',
    () async {
      const left = Detection('chair', .9, 'left', [
        .1,
        .1,
        .3,
        .8,
      ], closer: true);
      const right = Detection('chair', .9, 'right', [.7, .1, .9, .8]);
      const nearRight = Detection('chair', .9, 'right', [
        .7,
        .1,
        .9,
        .8,
      ], closer: true);
      await confirm([left, right]);
      expect(
        output.messages.last,
        contains('The chair on the left appears closer.'),
      );
      await speech.describeScene();
      expect(
        output.messages.last,
        'Two chairs. The chair on the left appears closer.',
      );
      await frame([chair, nearRight]);
      await speech.describeScene();
      expect(
        output.messages.last,
        'Two chairs. The chair on the right appears closer.',
      );
      await frame([chair]);
      await speech.describeScene();
      expect(output.messages.last, isNot(contains('closer')));
      await frame([chair, right]);
      await speech.describeScene();
      expect(output.messages.last, isNot(contains('closer')));
    },
  );

  test(
    'fresh 1.7-second depth frames announce a changed winner automatically once',
    () async {
      const nearLeft = Detection('chair', .9, 'left', [
        .1,
        .1,
        .3,
        .8,
      ], closer: true);
      const right = Detection('chair', .9, 'right', [.7, .1, .9, .8]);
      const nearRight = Detection('chair', .9, 'right', [
        .7,
        .1,
        .9,
        .8,
      ], closer: true);
      Future<void> slow(List<Detection> boxes) async {
        final received = now;
        now = now.add(const Duration(milliseconds: 1712));
        await speech.consider(boxes, observedAt: received);
      }

      await slow([nearLeft, right]);
      expect(output.messages.single, contains('on the left appears closer'));
      for (var i = 0; i < 6; i++) {
        await slow([nearLeft, right]);
      }
      expect(output.messages.length, 1);
      await slow([chair, nearRight]);
      expect(output.messages.last, contains('on the right appears closer'));
      await speech.describeScene();
      expect(
        output.messages.last,
        'Two chairs. The chair on the right appears closer.',
      );
    },
  );

  test('confidence or detection order changes do not repeat speech', () async {
    await confirm([person, chair]);
    const lower = Detection('person', .8, 'ahead', [.4, .1, .6, .8]);
    await frame([chair, lower]);
    await frame([lower, chair]);
    expect(output.messages.length, 1);
  });

  test(
    'unchanged storage notifications preserve quiet speech and detail cursor',
    () async {
      await confirm(scene);
      await speech.describeScene();
      (prefs as NotifyingPreferences).storageNotification();
      await frame(scene);
      await frame(scene);
      await frame(scene);
      expect(output.messages.length, 2);
      expect(speech.hasMoreDetails, isTrue);
    },
  );

  test(
    'disabled categories do not report that confirmation is pending',
    () async {
      prefs.pedestrians = false;
      await frame([person]);
      await speech.describeScene();
      expect(
        output.messages.last,
        'No stable objects detected. Path condition is unknown.',
      );
    },
  );
  test(
    'brief occlusion does not recount but persistent count changes do',
    () async {
      const second = Detection('person', .85, 'ahead', [.65, .1, .8, .8]);
      await confirm([person, second]);
      await frame([person]);
      await frame([person, second]);
      expect(output.messages, ['2 people, ahead.']);
      await frame([person]);
      await frame([person]);
      expect(output.messages, ['2 people, ahead.', 'person, ahead.']);
    },
  );
  test('new confirmed objects announce only changed groups', () async {
    await confirm([person]);
    await frame([person, chair]);
    await frame([person, chair]);
    expect(output.messages, ['person, ahead.', 'chair, left.']);
  });
  test(
    'Describe and More expose groups omitted from automatic summary',
    () async {
      await confirm(scene);
      expect(output.messages, ['person, ahead. chair, left.']);
      await speech.describeScene();
      expect(
        output.messages.last,
        'person, ahead. bicycle, left. chair, left. 2 more objects. More details available.',
      );
      expect(speech.hasMoreDetails, isTrue);
      await frame(scene);
      await speech.moreDetails();
      expect(output.messages.last, 'car, right. plant pot, right.');
      expect(speech.hasMoreDetails, isFalse);
    },
  );
  test('details paging ignores confidence reordering', () async {
    await confirm(scene);
    await speech.describeScene();
    await frame(scene.reversed.toList());
    await speech.moreDetails();
    expect(output.messages.last, 'car, right. plant pot, right.');
  });
  test('details restart with notice when scene changes', () async {
    await confirm(scene);
    await speech.describeScene();
    await frame(scene.take(4).toList());
    await frame(scene.take(4).toList());
    await speech.moreDetails();
    expect(output.messages.last, startsWith('Scene changed.'));
    expect(output.messages.last, contains('person, ahead.'));
  });
  test('stale camera descriptions do not read old objects', () async {
    await confirm(scene);
    now = now.add(const Duration(seconds: 3));
    await speech.describeScene();
    expect(
      output.messages.last,
      'Camera information is unavailable. Wait for a fresh frame.',
    );
    expect(speech.hasMoreDetails, isFalse);
  });
  test('empty and unconfirmed scenes are explicit only on request', () async {
    await frame([]);
    expect(output.messages, isEmpty);
    await speech.describeScene();
    expect(
      output.messages.last,
      'No stable objects detected. Path condition is unknown.',
    );
    await frame([person]);
    await speech.describeScene();
    expect(output.messages.last, 'Confirming detections. Please try again.');
  });
  test(
    'frames during speech update tracking without queueing announcements',
    () async {
      output.playback = Completer<void>();
      await frame([person]);
      final playing = frame([person]);
      await Future<void>.delayed(Duration.zero);
      await frame([person, chair]);
      await frame([person, chair]);
      expect(output.messages, ['person, ahead.']);
      output.playback!.complete();
      await playing;
      output.playback = null;
      await speech.describeScene();
      expect(output.messages.last, 'person, ahead. chair, left.');
    },
  );
  test('muted frames refresh the next requested scene', () async {
    await speech.toggleMute();
    await confirm([person, chair]);
    expect(output.messages, isEmpty);
    await speech.toggleMute();
    await speech.describeScene();
    expect(output.messages.last, 'person, ahead. chair, left.');
  });
  test(
    'scene changes during rate configuration cancel outdated speech',
    () async {
      output.configuration = Completer<void>();
      await frame([person]);
      final pending = frame([person]);
      await frame([]);
      await frame([]);
      output.configuration!.complete();
      await pending;
      expect(output.messages, isEmpty);
    },
  );
  test('slow configuration cannot issue a stale scene description', () async {
    await confirm([person]);
    output.configuration = Completer<void>();
    final pending = speech.describeScene();
    now = now.add(const Duration(seconds: 3));
    output.configuration!.complete();
    await pending;
    expect(output.messages, ['person, ahead.']);
  });

  test(
    'slow inference results are rejected using their callback time',
    () async {
      final captured = speech.markFrameReceived();
      now = now.add(const Duration(seconds: 3));
      await speech.consider([person], observedAt: captured);
      await speech.describeScene();
      expect(output.messages, [
        'Camera information is unavailable. Wait for a fresh frame.',
      ]);
    },
  );

  test('out-of-order results cannot overwrite the latest scene', () async {
    await confirm(scene);
    await speech.consider(
      [],
      observedAt: now.subtract(const Duration(milliseconds: 500)),
    );
    await speech.describeScene();
    expect(output.messages.last, contains('person, ahead.'));
  });
  test(
    'Stop clears paging, repeat and confirmation before next session',
    () async {
      await confirm(scene);
      await speech.describeScene();
      await speech.stop();
      expect(speech.hasMoreDetails, isFalse);
      expect(speech.canRepeat, isFalse);
      await speech.start();
      await frame([person]);
      expect(output.messages.length, 2);
    },
  );
}

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/danger_demo.dart';
import 'package:thesis_navigation/zone_preview.dart';
import 'package:thesis_navigation/path_preferences.dart';
import 'detection_speech_test.dart' show FakeSpeech;
import 'detection_haptics_test.dart' show FakeHaptics;

void main() {
  testWidgets(
    'selecting Farther shows its quiet result without device plugins',
    (tester) async {
      final prefs = PathPreferences()..ready = true;
      await tester.pumpWidget(
        MaterialApp(home: DangerDemoScreen(preferences: prefs, muted: false)),
      );
      await tester.tap(find.byType(DropdownButton<String>));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Farther').last);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Start test'));
      await tester.pumpAndSettle();
      expect(find.text('Test Farther. No urgent alert.'), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      prefs.dispose();
    },
  );
  const caution = (
    zone: ResearchZone.caution,
    label: 'Person',
    direction: 'right',
  );
  const danger = (
    zone: ResearchZone.danger,
    label: 'Chair',
    direction: 'ahead',
  );
  test('real detections drive demo priority without a ruler record', () async {
    const ahead = Detection('chair', .9, 'ahead', [.3, .2, .6, .8]);
    const winner = Detection('chair', .9, 'ahead', [
      .3,
      .2,
      .6,
      .8,
    ], closer: true);
    const left = Detection('person', .8, 'left', [
      .0,
      .1,
      .2,
      .7,
    ], closer: true);
    final voice = FakeSpeech();
    final prefs = PathPreferences();
    final output = PriorityAlertOutput(voice, FakeHaptics());
    final alerts = liveRuleCandidates([ahead, left]);
    expect(alerts.every((a) => a.zone == ResearchZone.caution), isTrue);
    await output.present(
      alerts,
      prefs,
      (_) {},
      vibration: false,
      voiceEnabled: true,
      rulePreview: true,
    );
    await output.present(
      liveRuleCandidates([left, winner]),
      prefs,
      (_) {},
      vibration: false,
      voiceEnabled: true,
      rulePreview: true,
    );
    expect(voice.messages.first, startsWith('Test. Caution.'));
    expect(voice.messages.last, 'Test. Warning. chair directly ahead.');
    expect(liveRuleCandidates([]), isEmpty);
    prefs.dispose();
  });
  test(
    'danger interrupts caution, uses three pulses and deduplicates the repeated frame',
    () async {
      final voice = FakeSpeech();
      final haptic = FakeHaptics();
      final prefs = PathPreferences();
      final output = PriorityAlertOutput(voice, haptic);
      final interrupted = Completer<void>();
      voice.playback = interrupted;
      final first = output.present(
        [caution],
        prefs,
        (_) {},
        vibration: true,
        voiceEnabled: true,
      );
      expect(voice.messages, ['Caution. Person on the right.']);
      voice.playback = null;
      final next = output.present(
        [caution, danger],
        prefs,
        (_) {},
        vibration: true,
        voiceEnabled: true,
      );
      interrupted.completeError(StateError('interrupted'));
      await Future.wait([first, next]);
      await output.present(
        [danger, caution],
        prefs,
        (_) {},
        vibration: true,
        voiceEnabled: true,
      );
      expect(voice.messages, [
        'Caution. Person on the right.',
        'Warning. Chair directly ahead.',
      ]);
      expect(voice.stops, 1);
      expect(haptic.pulses, 4);
      prefs.dispose();
    },
  );
  test('stop prevents pending pulses; muted speech stays silent', () async {
    final voice = FakeSpeech();
    final haptic = FakeHaptics();
    final prefs = PathPreferences();
    final output = PriorityAlertOutput(voice, haptic);
    final pending = output.present(
      [danger],
      prefs,
      (_) {},
      vibration: true,
      voiceEnabled: false,
    );
    await output.stop();
    await pending;
    expect(haptic.pulses, 1);
    expect(haptic.cancels, 1);
    expect(voice.messages, isEmpty);
    prefs.dispose();
  });
}

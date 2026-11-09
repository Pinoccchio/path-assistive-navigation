import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detection_overlay.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/session_view.dart';

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    final fonts = FontLoader('Inter')
      ..addFont(rootBundle.load('assets/fonts/inter-regular.ttf'))
      ..addFont(rootBundle.load('assets/fonts/inter-bold.ttf'));
    await fonts.load();
    await (FontLoader(
      'MaterialIcons',
    )..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
  });

  Future<void> pumpView(
    WidgetTester tester, {
    SessionPhase phase = SessionPhase.idle,
    Size size = const Size(390, 844),
    double scale = 1,
    List<Detection> detections = const [],
    String? error,
    VoidCallback? onToggle,
    VoidCallback? onToggleAudio,
    VoidCallback? onRepeat,
    VoidCallback? onDescribeScene,
    VoidCallback? onMoreDetails,
    bool hasMoreDetails = false,
    bool audioMuted = false,
    String? voiceStatus,
    bool hapticsOn = false,
    String? hapticStatus,
    VoidCallback? onToggleHaptics,
  }) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        theme: buildPathTheme(),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(
            context,
          ).copyWith(textScaler: TextScaler.linear(scale)),
          child: RepaintBoundary(
            key: const ValueKey('full-capture'),
            child: child!,
          ),
        ),
        home: RepaintBoundary(
          key: const ValueKey('capture'),
          child: SessionView(
            phase: phase,
            onToggle: onToggle ?? () {},
            onToggleAudio: onToggleAudio,
            onRepeat: onRepeat,
            onDescribeScene: onDescribeScene,
            onMoreDetails: onMoreDetails,
            hasMoreDetails: hasMoreDetails,
            audioMuted: audioMuted,
            voiceStatus: voiceStatus,
            hapticsOn: hapticsOn,
            hapticStatus: hapticStatus,
            onToggleHaptics: onToggleHaptics,
            detections: detections,
            elapsedMs: 143,
            processedFrames: 12,
            error: error,
            preview: ColoredBox(
              color: const Color(0xFF202020),
              child: DetectionOverlay(detections: detections),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.runAsync(() async {
      await precacheImage(
        const AssetImage('assets/figma/cpu.png'),
        tester.element(find.byType(SessionView)),
      );
    });
    await tester.pumpAndSettle();
  }

  Future<void> capture(
    WidgetTester tester,
    String name, {
    bool fullScreen = false,
  }) async {
    if (!const bool.fromEnvironment('CAPTURE_PATH_UI')) return;
    final boundary = tester.renderObject<RenderRepaintBoundary>(
      find.byKey(ValueKey(fullScreen ? 'full-capture' : 'capture')),
    );
    await tester.runAsync(() async {
      final image = await boundary.toImage();
      final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
      final output = File('../../qa/path-ui/$name.png');
      await output.parent.create(recursive: true);
      await output.writeAsBytes(bytes!.buffer.asUint8List());
      image.dispose();
    });
  }

  for (final size in [const Size(390, 844), const Size(320, 700)]) {
    for (final scale in [1.0, 2.0]) {
      testWidgets('idle and live reflow at $size, text $scale', (tester) async {
        final handle = tester.ensureSemantics();
        final suffix = '${size.width.toInt()}-${scale.toInt()}x';
        await pumpView(tester, size: size, scale: scale);
        expect(tester.takeException(), isNull);
        await capture(tester, 'idle-$suffix');
        if (scale == 1) {
          final mute = tester.getTopLeft(
            find.widgetWithText(OutlinedButton, 'Mute audio'),
          );
          final haptics = tester.getTopLeft(
            find.widgetWithText(OutlinedButton, 'Repeat'),
          );
          expect(mute.dy, closeTo(haptics.dy, 1));
          expect(haptics.dx, greaterThan(mute.dx));
        }
        await tester.ensureVisible(
          find.byKey(const ValueKey('session-toggle')),
        );
        expect(
          tester.getSize(find.byKey(const ValueKey('session-toggle'))).height,
          greaterThanOrEqualTo(64),
        );
        const detections = [
          Detection('electrical pole', .85, 'ahead', [.2, .2, .8, .8]),
        ];
        await pumpView(
          tester,
          size: size,
          scale: scale,
          phase: SessionPhase.live,
          detections: detections,
        );
        expect(
          find.bySemanticsLabel(
            'electrical pole, ahead, 85 percent confidence',
          ),
          findsOneWidget,
        );
        expect(tester.takeException(), isNull);
        await capture(tester, 'live-$suffix');
        await tester.ensureVisible(
          find.byKey(const ValueKey('session-toggle')),
        );
        await tester.pumpAndSettle();
        await capture(tester, 'live-controls-$suffix');
        expect(tester.takeException(), isNull);
        handle.dispose();
      });
    }
  }

  testWidgets('start and stop invoke the session action', (tester) async {
    var calls = 0;
    for (final phase in [SessionPhase.idle, SessionPhase.live]) {
      await pumpView(tester, phase: phase, onToggle: () => calls++);
      await tester.ensureVisible(find.byKey(const ValueKey('session-toggle')));
      await tester.tap(find.byKey(const ValueKey('session-toggle')));
    }
    expect(calls, 2);
  });

  testWidgets(
    'camera dominates normal phone view with all main actions visible',
    (tester) async {
      for (final size in [const Size(390, 844), const Size(320, 700)]) {
        await pumpView(
          tester,
          size: size,
          phase: SessionPhase.live,
          voiceStatus: 'Last spoken: Person ahead. Bicycle left.',
          detections: const [
            Detection('person', .95, 'ahead', [.36, .15, .64, .75]),
            Detection('bicycle', .9, 'left', [.03, .48, .29, .95]),
            Detection('chair', .85, 'right', [.72, .5, .97, .9]),
          ],
          onDescribeScene: () {},
          onToggleAudio: () {},
          onRepeat: () {},
        );
        final camera = tester.getRect(
          find.byKey(const ValueKey('camera-panel')),
        );
        expect(camera.height, greaterThan(size.height * .60));
        expect(find.text('LEFT'), findsNothing);
        expect(find.text('CENTER'), findsNothing);
        expect(find.text('RIGHT'), findsNothing);
        for (final label in ['Mute audio', 'Repeat', 'Stop']) {
          final button = find.widgetWithText(OutlinedButton, label);
          final rect = tester.getRect(button);
          expect(rect.bottom, lessThanOrEqualTo(size.height));
          expect(rect.width, greaterThanOrEqualTo(64));
          expect(rect.height, greaterThanOrEqualTo(64));
        }
        expect(tester.takeException(), isNull);
        await capture(tester, 'camera-first-live-${size.width.toInt()}');
      }
    },
  );

  testWidgets('full spoken message is available from the compact overlay', (
    tester,
  ) async {
    const message =
        'Two people ahead. Bicycle left. Chair right. More objects are available in the scene description.';
    await pumpView(
      tester,
      phase: SessionPhase.live,
      voiceStatus: 'Last spoken: $message',
    );
    await tester.tap(find.text(message));
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(AlertDialog),
        matching: find.text(message),
      ),
      findsOneWidget,
    );
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });

  testWidgets('haptics menu shows real state and invokes its toggle', (
    tester,
  ) async {
    var toggles = 0;
    await pumpView(
      tester,
      hapticsOn: true,
      hapticStatus: 'Haptics on for detection updates',
      onToggleHaptics: () => toggles++,
    );
    await tester.tap(find.byTooltip('Open navigation menu'));
    await tester.pumpAndSettle();
    expect(find.text('Haptics on for detection updates'), findsOneWidget);
    await capture(tester, 'haptics-menu-on', fullScreen: true);
    await tester.tap(find.byType(CheckedPopupMenuItem<String>));
    await tester.pumpAndSettle();
    expect(toggles, 1);
    expect(find.byType(AlertDialog), findsNothing);
    await pumpView(
      tester,
      hapticsOn: false,
      hapticStatus: 'Haptics off in Voice Only mode',
    );
    await tester.tap(find.byTooltip('Open navigation menu'));
    await tester.pumpAndSettle();
    expect(find.text('Haptics off'), findsOneWidget);
    expect(
      tester
          .widget<CheckedPopupMenuItem<String>>(
            find.byType(CheckedPopupMenuItem<String>),
          )
          .enabled,
      isFalse,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('real audio controls invoke callbacks and display voice state', (
    tester,
  ) async {
    var mutes = 0, repeats = 0;
    await pumpView(
      tester,
      phase: SessionPhase.live,
      voiceStatus: 'chair, left.',
      onToggleAudio: () => mutes++,
      onRepeat: () => repeats++,
    );
    await tester.ensureVisible(find.text('Mute audio'));
    await tester.tap(find.text('Mute audio'));
    await tester.ensureVisible(find.text('Repeat'));
    await tester.tap(find.text('Repeat'));
    expect(mutes, 1);
    expect(repeats, 1);
    expect(find.text('chair, left.'), findsOneWidget);
    expect(find.byType(AlertDialog), findsNothing);
    await capture(tester, 'audio-live-controls');
    await pumpView(
      tester,
      audioMuted: true,
      voiceStatus: 'Audio muted',
      onToggleAudio: () {},
    );
    expect(find.text('Unmute audio'), findsOneWidget);
    final repeat = tester.widget<OutlinedButton>(
      find.widgetWithText(OutlinedButton, 'Repeat'),
    );
    expect(repeat.onPressed, isNull);
    expect(tester.takeException(), isNull);
  });

  testWidgets('multi-object speech summary reflows with reachable controls', (
    tester,
  ) async {
    for (final fixture in [
      (const Size(390, 844), 1.0),
      (const Size(320, 700), 2.0),
    ]) {
      await pumpView(
        tester,
        phase: SessionPhase.live,
        size: fixture.$1,
        scale: fixture.$2,
        voiceStatus:
            '2 people, ahead. bicycle, left. chair, right. 3 more objects.',
        onToggleAudio: () {},
        onRepeat: () {},
      );
      expect(tester.takeException(), isNull);
      await tester.ensureVisible(find.text('Repeat'));
      await tester.tap(find.text('Repeat'));
      expect(tester.takeException(), isNull);
      if (fixture.$2 == 1) await capture(tester, 'audio-multiple-controls');
    }
  });

  testWidgets(
    'scene primary action pages details and menu restarts description',
    (tester) async {
      var descriptions = 0, details = 0;
      for (final fixture in [
        (const Size(390, 844), 1.0),
        (const Size(320, 700), 2.0),
      ]) {
        await pumpView(
          tester,
          size: fixture.$1,
          scale: fixture.$2,
          phase: SessionPhase.live,
          voiceStatus: 'Last spoken: 2 people, ahead. bicycle, left.',
          onDescribeScene: () => descriptions++,
        );
        final describe = find.byKey(const ValueKey('scene-description'));
        await tester.ensureVisible(describe);
        await tester.pumpAndSettle();
        await tester.tap(describe);
        expect(tester.getSize(describe).height, greaterThanOrEqualTo(64));
        await pumpView(
          tester,
          size: fixture.$1,
          scale: fixture.$2,
          phase: SessionPhase.live,
          hasMoreDetails: true,
          onMoreDetails: () => details++,
          onDescribeScene: () => descriptions++,
        );
        final more = find.byKey(const ValueKey('scene-description'));
        expect(find.text('More details'), findsOneWidget);
        await tester.ensureVisible(more);
        await tester.pumpAndSettle();
        await tester.tap(more);
        await capture(tester, 'camera-first-details-${fixture.$2.toInt()}x');
        await tester.ensureVisible(find.byTooltip('Open navigation menu'));
        await tester.pumpAndSettle();
        await tester.tap(find.byTooltip('Open navigation menu'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Describe scene'));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
      }
      expect(descriptions, 4);
      expect(details, 2);
      await pumpView(tester, phase: SessionPhase.live);
      expect(
        tester
            .widget<FilledButton>(
              find.byKey(const ValueKey('scene-description')),
            )
            .onPressed,
        isNull,
      );
    },
  );

  testWidgets('busy states disable actions; errors remain readable', (
    tester,
  ) async {
    for (final phase in [SessionPhase.starting, SessionPhase.stopping]) {
      await pumpView(tester, phase: phase);
      expect(
        tester
            .widget<FilledButton>(find.byKey(const ValueKey('session-toggle')))
            .onPressed,
        isNull,
      );
      expect(tester.takeException(), isNull);
      await capture(tester, phase.name);
    }
    await pumpView(
      tester,
      error: 'Camera permission denied. Allow access in Android settings.',
    );
    expect(find.textContaining('Camera permission denied'), findsOneWidget);
    await capture(tester, 'permission-error');
    expect(tester.takeException(), isNull);
  });

  testWidgets('empty detections report uncertainty without sample telemetry', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    await pumpView(tester, phase: SessionPhase.live);
    expect(
      find.bySemanticsLabel(
        'No object detected in this frame. Path condition is unknown.',
      ),
      findsOneWidget,
    );
    expect(find.textContaining('1.2m'), findsNothing);
    expect(find.textContaining('GPS Lock'), findsNothing);
    await capture(tester, 'live-empty');
    handle.dispose();
  });

  testWidgets('detection semantics are grouped without frame announcements', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();

    await pumpView(
      tester,
      phase: SessionPhase.live,
      detections: const [
        Detection('chair', .9, 'left', [.1, .1, .6, .6]),
      ],
    );
    final label = find.bySemanticsLabel('chair, left, 90 percent confidence');
    expect(label, findsOneWidget);
    expect(
      tester
          .getSemantics(label)
          .getSemanticsData()
          .hasFlag(ui.SemanticsFlag.isLiveRegion),
      isFalse,
    );
    semantics.dispose();
  });
}

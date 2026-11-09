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
          child: child!,
        ),
        home: RepaintBoundary(
          key: const ValueKey('capture'),
          child: SessionView(
            phase: phase,
            onToggle: onToggle ?? () {},
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

  Future<void> capture(WidgetTester tester, String name) async {
    if (!const bool.fromEnvironment('CAPTURE_PATH_UI')) return;
    final boundary = tester.renderObject<RenderRepaintBoundary>(
      find.byKey(const ValueKey('capture')),
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
          final mute = tester.getTopLeft(find.text('MUTE AUDIO'));
          final haptics = tester.getTopLeft(find.text('HAPTICS ON'));
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

  testWidgets('all unfinished Figma controls explain development status', (
    tester,
  ) async {
    await pumpView(tester);
    expect(find.text('In development'), findsNWidgets(3));
    for (final label in ['Mute audio', 'Haptics on', 'Repeat last alert']) {
      await tester.ensureVisible(find.text(label.toUpperCase()));
      await tester.tap(find.text(label.toUpperCase()));
      await tester.pumpAndSettle();
      expect(find.text('$label — In development'), findsOneWidget);
      await tester.tap(find.text('Close'));
      await tester.pumpAndSettle();
    }
    expect(find.textContaining('Research test only.'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('busy states disable actions; errors remain readable', (
    tester,
  ) async {
    for (final phase in [SessionPhase.starting, SessionPhase.stopping]) {
      await pumpView(tester, phase: phase);
      expect(
        tester
            .widget<TextButton>(find.byKey(const ValueKey('session-toggle')))
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

import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:thesis_navigation/hazard_log_screen.dart';
import 'package:thesis_navigation/main.dart';
import 'package:thesis_navigation/path_preferences.dart';
import 'package:thesis_navigation/session_view.dart';
import 'package:thesis_navigation/settings_screen.dart';

const previewEvents = [
  HazardLogEntry(
    object: 'Chair',
    direction: 'Center',
    time: '10:42:08',
    severity: HazardSeverity.danger,
    distanceMeters: 1.2,
  ),
  HazardLogEntry(
    object: 'Pedestrian',
    direction: 'Left',
    time: '10:41:56',
    severity: HazardSeverity.caution,
    distanceMeters: 2.4,
  ),
  HazardLogEntry(
    object: 'Vehicle',
    direction: 'Right',
    time: '10:41:32',
    severity: HazardSeverity.safe,
    distanceMeters: 4.8,
  ),
];

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    await (FontLoader('Inter')
          ..addFont(rootBundle.load('assets/fonts/inter-regular.ttf'))
          ..addFont(rootBundle.load('assets/fonts/inter-bold.ttf')))
        .load();
    await (FontLoader(
      'MaterialIcons',
    )..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
  });

  Future<void> pump(
    WidgetTester tester,
    Widget child, {
    Size size = const Size(390, 844),
    double scale = 1,
    EdgeInsets safeArea = EdgeInsets.zero,
  }) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        theme: buildPathTheme(),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: TextScaler.linear(scale),
            padding: safeArea,
            viewPadding: safeArea,
          ),
          child: child!,
        ),
        home: KeyedSubtree(
          key: UniqueKey(),
          child: RepaintBoundary(
            key: const ValueKey('screen-capture'),
            child: child,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.runAsync(() async {
      final context = tester.element(
        find.byKey(const ValueKey('screen-capture')),
      );
      for (final asset in [
        'back',
        'map-pin',
        'triangle-alert',
        'caution',
        'safe',
      ]) {
        for (final width in [60, 72, 84, 96]) {
          await precacheImage(
            ResizeImage(AssetImage('assets/figma/$asset.png'), width: width),
            context,
          );
        }
      }
    });
    await tester.pumpAndSettle();
  }

  Future<void> capture(WidgetTester tester, String name) async {
    if (!const bool.fromEnvironment('CAPTURE_PATH_UI')) return;
    final boundary = tester.renderObject<RenderRepaintBoundary>(
      find.byKey(const ValueKey('screen-capture')),
    );
    await tester.pumpAndSettle(const Duration(milliseconds: 100));
    await tester.runAsync(() async {
      final image = await boundary.toImage();
      final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('../../qa/path-ui/$name.png');
      await file.parent.create(recursive: true);
      await file.writeAsBytes(bytes!.buffer.asUint8List());
      image.dispose();
    });
  }

  for (final size in [const Size(390, 844), const Size(320, 700)]) {
    for (final scale in [1.0, 2.0]) {
      testWidgets('settings and history reflow at $size, text $scale', (
        tester,
      ) async {
        final prefs = PathPreferences();
        await prefs.load();
        final suffix = '${size.width.toInt()}-${scale.toInt()}x';
        await pump(
          tester,
          SettingsScreen(preferences: prefs),
          size: size,
          scale: scale,
        );
        expect(tester.takeException(), isNull);
        await capture(tester, 'settings-$suffix');
        await tester.ensureVisible(find.text('Pedestrians'));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
        await capture(tester, 'settings-bottom-$suffix');
        await pump(tester, const HazardLogScreen(), size: size, scale: scale);
        await capture(tester, 'hazard-empty-$suffix');
        await tester.scrollUntilVisible(
          find.byKey(const ValueKey('hazard-preview-danger')),
          200,
        );
        expect(find.text('0 events'), findsOneWidget);
        expect(find.text('No detections yet'), findsNothing);
        expect(find.textContaining('San Francisco'), findsNothing);
        expect(tester.takeException(), isNull);
        await tester.scrollUntilVisible(find.text('Cancel alert'), 200);
        await tester.pumpAndSettle();
        await tester.ensureVisible(find.text('Cancel alert'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Cancel alert'));
        await tester.pumpAndSettle();
        expect(find.text('Cancel alert — In development'), findsOneWidget);
        await tester.tap(find.text('Close'));
        await tester.pumpAndSettle();
        await pump(
          tester,
          const HazardLogScreen(entries: previewEvents),
          size: size,
          scale: scale,
        );
        expect(tester.takeException(), isNull);
        expect(find.text('3 events'), findsOneWidget);
        await capture(tester, 'hazard-fixture-$suffix');
        prefs.dispose();
      });
    }
  }

  for (final scale in [.85, 1.0]) {
    testWidgets('all settings fit the Note 40 viewport at text $scale', (
      tester,
    ) async {
      final prefs = PathPreferences();
      await prefs.load();
      const safeArea = EdgeInsets.only(top: 28, bottom: 24);
      await pump(
        tester,
        SettingsScreen(preferences: prefs),
        size: const Size(360, 812),
        scale: scale,
        safeArea: safeArea,
      );
      final lastControl = find.ancestor(
        of: find.text('Pedestrians'),
        matching: find.byType(OutlinedButton),
      );
      expect(
        tester.getBottomRight(lastControl).dy,
        lessThanOrEqualTo(812 - safeArea.bottom),
      );
      expect(
        tester.getTopLeft(find.text('Accessibility & Alerts')).dy,
        greaterThanOrEqualTo(safeArea.top),
      );
      for (final control in tester.widgetList<OutlinedButton>(
        find.byType(OutlinedButton),
      )) {
        expect(
          control.style!.minimumSize!.resolve({})!.height,
          greaterThanOrEqualTo(64),
        );
      }
      expect(tester.takeException(), isNull);
      await capture(tester, 'settings-phone-${(scale * 100).round()}');
      prefs.dispose();
    });
  }

  testWidgets('settings selections, switches and sliders survive reloading', (
    tester,
  ) async {
    final prefs = PathPreferences();
    await prefs.load();
    await pump(tester, SettingsScreen(preferences: prefs));
    await tester.tap(find.textContaining('Voice Only'));
    await tester.pumpAndSettle();
    await tester.tap(find.textContaining('Clock-Hand System'));
    await tester.pumpAndSettle();
    for (final key in ['Speech Rate', 'Alert Cooldown']) {
      final slider = find.byKey(ValueKey(key));
      await tester.ensureVisible(slider);
      await tester.drag(slider, const Offset(80, 0));
      await tester.pumpAndSettle();
    }
    await tester.ensureVisible(find.text('Stairs'));
    await tester.tap(find.text('Stairs'));
    await tester.pumpAndSettle();
    await prefs.save();
    final reloaded = PathPreferences();
    await reloaded.load();
    expect(reloaded.delivery, AlertDelivery.voiceOnly);
    expect(reloaded.direction, DirectionFormat.clockHand);
    expect(reloaded.stairs, isFalse);
    expect(reloaded.speechRate, greaterThan(1.5));
    expect(reloaded.cooldown, greaterThan(1));
    expect(reloaded.error, isNull);
    prefs.dispose();
    reloaded.dispose();
  });

  testWidgets('bad stored settings retain usable defaults and allow retry', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({
      PathPreferences.storageKey: '{broken',
    });
    final prefs = PathPreferences();
    await prefs.load();
    await pump(tester, SettingsScreen(preferences: prefs));
    expect(prefs.ready, isTrue);
    expect(
      find.textContaining('Saved settings are unavailable'),
      findsOneWidget,
    );
    expect(find.text('Reset settings'), findsNothing);
    expect(find.text('In development'), findsNothing);
    await tester.tap(find.text('Retry'));
    await tester.pumpAndSettle();
    expect(prefs.ready, isTrue);
    expect(prefs.error, isNull);
    prefs.dispose();
  });

  testWidgets('storage failure keeps full-contrast selections interactive', (
    tester,
  ) async {
    final prefs = PathPreferences(
      loadStorage: () async => throw MissingPluginException(),
    );
    await prefs.load();
    await pump(tester, SettingsScreen(preferences: prefs));
    expect(prefs.ready, isTrue);
    await tester.tap(find.textContaining('Voice Only'));
    await tester.pumpAndSettle();
    expect(prefs.delivery, AlertDelivery.voiceOnly);
    final selected = tester.widget<Text>(find.textContaining('Voice Only'));
    expect(selected.style!.color, Colors.black);
    double contrast(Color a, Color b) {
      final first = a.computeLuminance();
      final second = b.computeLuminance();
      return first > second
          ? (first + .05) / (second + .05)
          : (second + .05) / (first + .05);
    }

    expect(
      contrast(selected.style!.color!, pathYellow),
      greaterThanOrEqualTo(7),
    );
    final unselected = tester.widget<Text>(find.textContaining('Haptic Only'));
    expect(unselected.style!.color, Colors.white);
    expect(
      contrast(unselected.style!.color!, Colors.black),
      greaterThanOrEqualTo(7),
    );
    await tester.ensureVisible(find.byKey(const ValueKey('Speech Rate')));
    expect(
      tester
          .widget<Slider>(find.byKey(const ValueKey('Speech Rate')))
          .onChanged,
      isNotNull,
    );
    await tester.ensureVisible(find.text('Stairs'));
    await tester.tap(find.text('Stairs'));
    await tester.pumpAndSettle();
    expect(prefs.stairs, isFalse);
    expect(tester.takeException(), isNull);
    await capture(tester, 'settings-storage-unavailable');
    prefs.dispose();
  });

  testWidgets('clear log can be undone; cancel is explicitly unavailable', (
    tester,
  ) async {
    await pump(tester, const HazardLogScreen(entries: previewEvents));
    await tester.ensureVisible(find.text('Clear log'));
    await tester.tap(find.text('Clear log'));
    await tester.pumpAndSettle();
    expect(find.text('0 events'), findsOneWidget);
    await tester.tap(find.text('Undo'));
    await tester.pumpAndSettle();
    expect(find.text('3 events'), findsOneWidget);
  });

  for (final config in [
    (const Size(390, 844), 1.0),
    (const Size(360, 812), .85),
    (const Size(320, 700), 2.0),
  ]) {
    testWidgets('Figma log preview preserves sample content at $config', (
      tester,
    ) async {
      await pump(
        tester,
        const HazardLogScreen(previewMode: true),
        size: config.$1,
        scale: config.$2,
      );
      expect(find.text('PREVIEW'), findsOneWidget);
      expect(find.text('200 Market St, San Francisco'), findsOneWidget);
      expect(find.text('GPS accuracy ±5m'), findsOneWidget);
      await tester.scrollUntilVisible(find.text('3 events'), 200);
      expect(find.text('3 events'), findsOneWidget);
      await capture(
        tester,
        'hazard-figma-${config.$1.width.toInt()}-${(config.$2 * 100).round()}',
      );
      await tester.scrollUntilVisible(find.text('Vehicle'), 200);
      expect(find.text('4.8m · Right'), findsOneWidget);
      await tester.scrollUntilVisible(find.text('Cancel alert'), 200);
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Cancel alert'));
      await tester.pumpAndSettle();
      expect(
        find.text('Shake phone to clear log or cancel alert.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
      if (config.$2 <= 1) {
        final cards = find.byWidgetPredicate(
          (widget) =>
              widget is ConstrainedBox && widget.constraints.minHeight == 124,
        );
        expect(cards, findsNWidgets(3));
        expect(tester.getSize(cards.first).height, closeTo(124, 1));
      }
    });
  }

  testWidgets(
    'clearing a preview affects only its sample rows and supports Undo',
    (tester) async {
      await pump(tester, const HazardLogScreen(previewMode: true));
      await tester.ensureVisible(find.text('Clear log'));
      await tester.tap(find.text('Clear log'));
      await tester.pumpAndSettle();
      expect(find.text('0 events'), findsOneWidget);
      expect(find.text('PREVIEW'), findsOneWidget);
      expect(find.text('Preview log cleared'), findsOneWidget);
      await tester.tap(find.text('Undo'));
      await tester.pumpAndSettle();
      expect(find.text('3 events'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'empty log uses source-shaped development cards without fake events',
    (tester) async {
      await pump(tester, const HazardLogScreen());
      for (final severity in HazardSeverity.values) {
        await tester.scrollUntilVisible(
          find.byKey(ValueKey('hazard-preview-${severity.name}')),
          200,
        );
        expect(
          find.byKey(ValueKey('hazard-preview-${severity.name}')),
          findsOneWidget,
        );
      }
      expect(find.text('0 events'), findsOneWidget);
      expect(find.text('Chair'), findsNothing);
      expect(find.textContaining('1.2m'), findsNothing);
      await tester.scrollUntilVisible(find.text('Clear log'), 200);
      await tester.tap(find.text('Clear log'));
      await tester.pumpAndSettle();
      expect(find.text('No saved detections'), findsOneWidget);
      await tester.tap(find.text('Close'));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('hazard source layout fits phone controls at normal text size', (
    tester,
  ) async {
    await pump(
      tester,
      const HazardLogScreen(),
      size: const Size(360, 812),
      scale: .85,
      safeArea: const EdgeInsets.only(top: 28, bottom: 24),
    );
    expect(
      tester
          .getBottomRight(find.widgetWithText(OutlinedButton, 'Cancel alert'))
          .dy,
      lessThanOrEqualTo(788),
    );
    await capture(tester, 'hazard-phone-85');
    expect(tester.takeException(), isNull);
  });

  testWidgets('HUD menu opens both screens and Back returns to camera', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      const RepaintBoundary(
        key: ValueKey('screen-capture'),
        child: ResearchApp(),
      ),
    );
    await tester.pumpAndSettle();
    await capture(tester, 'hud-navigation');
    for (final item in ['Settings & Accessibility', 'Hazard Log & GPS']) {
      await tester.tap(find.byTooltip('Open navigation menu'));
      await tester.pumpAndSettle();
      await tester.tap(find.text(item));
      await tester.pumpAndSettle();
      expect(find.text('Back'), findsOneWidget);
      await capture(
        tester,
        item.startsWith('Settings') ? 'settings-route' : 'hazard-log-route',
      );
      await tester.tap(find.text('Back'));
      await tester.pumpAndSettle();
      expect(find.text('PATH / IDLE'), findsOneWidget);
    }
    expect(tester.takeException(), isNull);
  });

  testWidgets('switch semantics and adjustable settings expose current state', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    final prefs = PathPreferences();
    await prefs.load();
    await pump(tester, SettingsScreen(preferences: prefs));
    await tester.ensureVisible(find.text('Stairs'));
    expect(
      tester
          .getSemantics(find.bySemanticsLabel('Stairs'))
          .getSemanticsData()
          .hasFlag(ui.SemanticsFlag.isToggled),
      isTrue,
    );
    handle.dispose();
    prefs.dispose();
  });
}

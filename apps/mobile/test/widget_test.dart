import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/main.dart';

void main() {
  testWidgets('initial camera session is stopped and marked research-only', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const ResearchApp());
    expect(find.text('Camera is off'), findsOneWidget);
    expect(find.text('IDLE'), findsOneWidget);
    expect(find.text('Start camera session'), findsOneWidget);
    expect(find.textContaining('Research test only.'), findsNothing);
    expect(find.text('Mute audio'), findsOneWidget);
    expect(find.text('HAPTICS ON'), findsNothing);
    expect(find.text('Repeat'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('idle controls fit a compact phone screen', (tester) async {
    tester.view.physicalSize = const Size(320, 700);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const ResearchApp());
    expect(find.text('Start camera session'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

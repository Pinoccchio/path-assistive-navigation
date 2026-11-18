import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:thesis_navigation/hazard_history.dart';
import 'package:thesis_navigation/hazard_log_screen.dart';

void main() {
  testWidgets(
    'cancel and save export the displayed snapshot without editing history',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final history = HazardHistory();
      final at = DateTime.utc(2026, 11, 19, 7, 4, 5);
      await history.add(
        HazardEvent(at, 'Test', 'Danger', 'chair, "red"', 'ahead'),
      );
      const channel = MethodChannel('path/hazard_export');
      final messenger = tester.binding.defaultBinaryMessenger;
      final calls = <MethodCall>[];
      messenger.setMockMethodCallHandler(channel, (call) async {
        calls.add(call);
        return calls.length > 1;
      });
      addTearDown(() => messenger.setMockMethodCallHandler(channel, null));
      await tester.pumpWidget(
        MaterialApp(home: RecordedHazardLog(history: history)),
      );
      await tester.pumpAndSettle();
      for (var i = 0; i < 2; i++) {
        await tester.tap(find.text('Export CSV'));
        await tester.pumpAndSettle();
        expect(
          find.text('Exported 1 alerts to CSV.'),
          i == 0 ? findsNothing : findsOneWidget,
        );
      }
      expect(calls.last.method, 'saveCsv');
      expect(calls.last.arguments['name'], endsWith('.csv'));
      expect(
        calls.last.arguments['csv'],
        'timestamp_utc,mode,severity,object,direction\r\n"2026-11-19T07:04:05.000Z","Test","Danger","chair, ""red""","ahead"\r\n',
      );
      expect((await history.read()).length, 1);
    },
  );
}

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';
import 'package:thesis_navigation/calibration_screen.dart';
import 'package:thesis_navigation/depth_preview.dart';
import 'package:thesis_navigation/detector.dart';

void main() {
  test(
    'captured color scene removes portrait padding and keeps object coordinates',
    () {
      final frame = Float32List(512 * 512 * 3);
      for (var y = 0; y < 512; y++) {
        for (var x = 128; x < 384; x++) {
          frame[(y * 512 + x) * 3 + (x < 256 ? 0 : 2)] = 1;
        }
      }
      final photo = img.decodeJpg(encodeCalibrationFrame((frame, .5)))!;
      expect([photo.width, photo.height], [256, 512]);
      expect(photo.getPixel(2, 256).r, greaterThan(240));
      expect(photo.getPixel(253, 256).b, greaterThan(240));
    },
  );

  testWidgets(
    'selects the frozen object, validates cm and persists one paired sample',
    (tester) async {
      SharedPreferencesAsyncPlatform.instance =
          InMemorySharedPreferencesAsync.empty();
      final depth = DepthMap.fromOutput(
        Float32List.fromList(
          List.generate(256 * 256, (i) => i % 256 < 128 ? 10.0 : 35.0),
        ),
      );
      final page = MaterialApp(
        home: CalibrationScreen(
          depth: depth,
          detections: const [
            Detection('chair', .9, 'left', [0, 0, .5, 1]),
            Detection('chair', .8, 'right', [.5, 0, 1, 1], closer: true),
          ],
          frameUtc: DateTime.utc(2026),
          aspect: .75,
        ),
      );
      await tester.pumpWidget(page);
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<DropdownButton<int>>(find.byType(DropdownButton<int>))
            .value,
        1,
      );
      await tester.scrollUntilVisible(
        find.text('Save sample'),
        100,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Save sample'));
      await tester.pumpAndSettle();
      expect(find.textContaining('greater than zero'), findsOneWidget);
      await tester.tap(find.byType(DropdownButton<int>));
      await tester.pumpAndSettle();
      await tester.tap(find.text('2. chair - right').last);
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '125.5');
      await tester.tap(find.text('Save sample'));
      await tester.pumpAndSettle();
      final store = SharedPreferencesAsync();
      final key = (await store.getKeys()).single;
      final row = jsonDecode((await store.getString(key))!);
      expect(row['distanceCm'], 125.5);
      expect(row['medianInverseDepth'], 35);
      expect(row['direction'], 'right');
      expect(find.text('Sample saved on phone'), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      await tester.pumpWidget(page);
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Saved samples: 1'),
        100,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.text('Saved samples: 1'), findsOneWidget);
    },
  );
}

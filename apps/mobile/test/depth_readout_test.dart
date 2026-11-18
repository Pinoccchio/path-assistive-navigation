import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/depth_preview.dart';
import 'package:thesis_navigation/session_view.dart';

void main() {
  testWidgets(
    'research timings stay outside camera and feedback on narrow phones',
    (tester) async {
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);
      for (final scale in [1.0, 2.0]) {
        tester.view.physicalSize = const Size(320, 680);
        await tester.pumpWidget(
          MaterialApp(
            home: MediaQuery(
              data: MediaQueryData(
                size: const Size(320, 680),
                textScaler: TextScaler.linear(scale),
              ),
              child: SessionView(
                phase: SessionPhase.live,
                onToggle: () {},
                preview: const ColoredBox(color: Colors.blue),
                voiceStatus: 'Listening for detections',
                researchPanel: DepthReadout(
                  map: DepthMap.fromOutput(Float32List(256 * 256)),
                  detectorMs: 810,
                  combinedMs: 1685,
                  aspect: .75,
                ),
              ),
            ),
          ),
        );
        final camera = tester.getRect(
          find.byKey(const ValueKey('camera-panel')),
        );
        for (final value in ['Detector 810 ms', 'Combined 1685 ms']) {
          final rect = tester.getRect(find.text(value));
          expect(rect.bottom, lessThanOrEqualTo(camera.top));
          expect(rect.right, lessThanOrEqualTo(320));
        }
        expect(tester.takeException(), isNull);
      }
    },
  );
}

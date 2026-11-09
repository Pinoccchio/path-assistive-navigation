import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detection_overlay.dart';
import 'package:thesis_navigation/detector.dart';

void main() {
  test(
    'each object label includes its own direction instead of confidence',
    () {
      expect(
        detectionBoxLabel(const Detection('person', .9, 'ahead', [0, 0, 1, 1])),
        'PERSON · AHEAD',
      );
      expect(
        detectionBoxLabel(const Detection('bicycle', .8, 'left', [0, 0, 1, 1])),
        'BICYCLE · LEFT',
      );
      expect(
        detectionBoxLabel(const Detection('chair', .8, 'right', [0, 0, 1, 1])),
        'CHAIR · RIGHT',
      );
    },
  );

  for (final imageSize in [const Size(480, 640), const Size(640, 480)]) {
    testWidgets('entire $imageSize image fits without cropping or stretching', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(400, 800);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ProportionalDetectionPreview(
              imageSize: imageSize,
              image: const ColoredBox(color: Colors.grey),
              detections: const [
                Detection('person', .9, 'ahead', [0, 0, 1, 1]),
                Detection('electrical pole', .9, 'right', [.75, .7, 1, 1]),
              ],
            ),
          ),
        ),
      );
      final plane = tester.getRect(
        find.byKey(const ValueKey('camera-image-plane')),
      );
      expect(plane.width / plane.height, closeTo(imageSize.aspectRatio, .0001));
      expect(plane.left, greaterThanOrEqualTo(0));
      expect(plane.right, lessThanOrEqualTo(400));
      expect(plane.top, greaterThanOrEqualTo(0));
      expect(plane.bottom, lessThanOrEqualTo(800));
      final overlay = tester.getSize(find.byType(DetectionOverlay));
      expect(overlay.width, closeTo(plane.width, .001));
      expect(overlay.height, closeTo(plane.height, .001));
      expect(tester.takeException(), isNull);
    });
  }
}

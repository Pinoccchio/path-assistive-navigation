import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/depth_preview.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/detection_overlay.dart';

void main() {
  const left = [0.0, 0.0, 0.5, 1.0];
  const right = [0.5, 0.0, 1.0, 1.0];
  DepthMap scene(double a, double b) => DepthMap.fromOutput(
    Float32List.fromList(
      List.generate(256 * 256, (i) => i % 256 < 128 ? a : b),
    ),
  );
  test('closer label follows the strongest distinct box', () {
    expect(scene(200, 100).closerBox([left, right]), 0);
    expect(scene(100, 200).closerBox([left, right]), 1);
    expect(
      detectionBoxLabel(
        const Detection('chair', .9, 'left', left, closer: true),
      ),
      endsWith('CLOSER'),
    );
  });
  test(
    'withholds a winner for ties, weak separation or inadequate coverage',
    () {
      for (final boxes in [
        <List<double>>[],
        [left],
        [left, right],
        [left, right, left],
      ]) {
        expect(scene(101, 100).closerBox(boxes), isNull);
      }
      expect(scene(100, 100).closerBox([left, right]), isNull);
      expect(scene(200, 100).closerBox([left, left, right]), isNull);
      expect(
        scene(200, 100).closerBox([
          left,
          [.9, .9, .901, .901],
        ]),
        isNull,
      );
    },
  );
}

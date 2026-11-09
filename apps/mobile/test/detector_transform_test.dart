import 'package:flutter_test/flutter_test.dart';
import 'dart:typed_data';
import 'package:thesis_navigation/detector.dart';

void main() {
  Float32List outputAt(double x, {double width = 20}) {
    final values = Float32List(12 * 5376);
    values[0] = x;
    values[5376] = 256;
    values[2 * 5376] = width;
    values[3 * 5376] = 100;
    values[4 * 5376] = .9;
    return values;
  }

  for (final rotation in [90, 270]) {
    test('direction removes portrait padding at rotation $rotation', () {
      // Landscape camera becomes 288x512 portrait, with 112px side padding.
      for (final example in [
        (184.0, 'left'),
        (256.0, 'ahead'),
        (328.0, 'right'),
      ]) {
        final detected = decodeDetections(
          outputAt(example.$1),
          512,
          288,
          rotation,
        ).single;
        expect(detected.direction, example.$2);
      }
    });
  }

  test('portrait sensor and landscape sensor use the same image thirds', () {
    expect(
      decodeDetections(outputAt(184), 288, 512, 0).single.direction,
      'left',
    );
    expect(
      decodeDetections(outputAt(128), 512, 288, 0).single.direction,
      'left',
    );
    expect(
      decodeDetections(outputAt(384), 512, 288, 180).single.direction,
      'right',
    );
  });

  test('direction treats one third as ahead and two thirds as right', () {
    // 384x512 portrait: padding 64, thirds at model x=192 and 320 exactly.
    expect(
      decodeDetections(outputAt(191), 512, 384, 90).single.direction,
      'left',
    );
    expect(
      decodeDetections(outputAt(192), 512, 384, 90).single.direction,
      'ahead',
    );
    expect(
      decodeDetections(outputAt(319), 512, 384, 90).single.direction,
      'ahead',
    );
    expect(
      decodeDetections(outputAt(320), 512, 384, 90).single.direction,
      'right',
    );
  });

  test('same-class NMS still removes duplicate raw model boxes', () {
    final values = outputAt(184);
    for (var channel = 0; channel < 12; channel++) {
      values[channel * 5376 + 1] = values[channel * 5376];
    }
    expect(decodeDetections(values, 512, 288, 90).length, 1);
  });
  test('removes portrait letterbox padding before drawing a box', () {
    expect(modelBoxToPreview([64, 0, 448, 512], 640, 480, 90), [0, 0, 1, 1]);
    expect(modelBoxToPreview([160, 128, 352, 384], 640, 480, 90), [
      0.25,
      0.25,
      0.75,
      0.75,
    ]);
  });

  test('removes landscape letterbox padding before drawing a box', () {
    expect(modelBoxToPreview([0, 64, 512, 448], 640, 480, 0), [0, 0, 1, 1]);
  });
}

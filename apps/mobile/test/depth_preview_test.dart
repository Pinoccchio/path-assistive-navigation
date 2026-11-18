import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/depth_preview.dart';

void main() {
  test(
    'portrait input removes detector padding and preserves RGB ordering',
    () {
      final rgb = Float32List(512 * 512 * 3);
      for (var y = 0; y < 512; y++) {
        for (var x = 128; x < 384; x++) {
          rgb[(y * 512 + x) * 3] = 1;
        }
      }
      final input = prepareDepthInput((rgb, 256, 512));
      for (final offset in [0, input.length - 3]) {
        expect(input[offset], closeTo((1 - 0.485) / 0.229, 0.001));
        expect(input[offset + 1], closeTo(-0.456 / 0.224, 0.001));
      }
    },
  );
  test(
    'relative map handles flat frames and preserves inverse depth order',
    () {
      final values = Float32List(256 * 256);
      expect(DepthMap.fromOutput(values).shades.toSet(), {128});
      values[4 * 256 + 4] = 10;
      final map = DepthMap.fromOutput(values);
      expect(map.shades.first, 255);
      expect(map.shades.last, 0);
    },
  );
}

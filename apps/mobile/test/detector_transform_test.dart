import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detector.dart';

void main() {
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

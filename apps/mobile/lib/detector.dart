import 'dart:math' as math;

import 'depth_preview.dart';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

const classNames = [
  'person',
  'chair',
  'stairs',
  'car',
  'bicycle',
  'electrical pole',
  'plant pot',
  'motorcycle',
];

class Detection {
  const Detection(
    this.label,
    this.score,
    this.direction,
    this.box, {
    this.closer = false,
  });
  final bool closer;
  final String label;
  final double score;
  final String direction;
  final List<double> box;
}

class DetectionResult {
  const DetectionResult(
    this.detections,
    this.elapsedMs, {
    this.depth,
    this.totalMs,
    this.frameRgb,
  });
  final List<Detection> detections;
  final int elapsedMs;
  final DepthMap? depth;
  final int? totalMs;
  final Float32List? frameRgb;
}

class Detector {
  Detector._(this._interpreter, this._worker, this._depth);
  final DepthPreviewModel? _depth;
  final Interpreter _interpreter;
  final IsolateInterpreter _worker;

  static Future<Detector> load() async {
    final interpreter = await Interpreter.fromAsset(
      'assets/model/best_float32.tflite',
      options: InterpreterOptions()..threads = 2,
    );
    final input = interpreter.getInputTensor(0);
    final output = interpreter.getOutputTensor(0);
    if (!listEquals(input.shape, [1, 512, 512, 3]) ||
        !listEquals(output.shape, [1, 12, 5376])) {
      interpreter.close();
      throw StateError('Unexpected model tensor shapes.');
    }
    final worker = await IsolateInterpreter.create(
      address: interpreter.address,
    );
    try {
      final depth = depthPreviewEnabled ? await DepthPreviewModel.load() : null;
      return Detector._(interpreter, worker, depth);
    } catch (_) {
      await worker.close();
      interpreter.close();
      rethrow;
    }
  }

  Future<DetectionResult> detect(CameraImage frame, int sensorRotation) async {
    final timer = Stopwatch()..start();
    if (frame.format.group != ImageFormatGroup.yuv420 ||
        frame.planes.length != 3) {
      throw StateError(
        'Unsupported camera image format: ${frame.format.group}',
      );
    }
    final input = await compute(_prepareFrame, <String, Object>{
      'width': frame.width,
      'height': frame.height,
      'rotation': sensorRotation,
      'planes': frame.planes.map((plane) => plane.bytes).toList(),
      'rowStrides': frame.planes.map((plane) => plane.bytesPerRow).toList(),
      'pixelStrides': frame.planes
          .map((plane) => plane.bytesPerPixel ?? 1)
          .toList(),
    });
    final output = Uint8List(12 * 5376 * 4);
    await _worker.run(input.buffer.asUint8List(), output);
    final values = output.buffer.asFloat32List();
    final detections = decodeDetections(
      values,
      frame.width,
      frame.height,
      sensorRotation,
    );
    final detectorMs = timer.elapsedMilliseconds;
    final rotated = sensorRotation % 180 != 0;
    final depth = await _depth?.estimate(
      input,
      rotated ? frame.height : frame.width,
      rotated ? frame.width : frame.height,
    );
    final closer = depth?.closerBox([
      for (final detection in detections) detection.box,
    ]);
    if (closer != null) {
      final d = detections[closer];
      detections[closer] = Detection(
        d.label,
        d.score,
        d.direction,
        d.box,
        closer: true,
      );
    }
    return DetectionResult(
      detections,
      detectorMs,
      depth: depth,
      frameRgb: depth == null ? null : input,
      totalMs: timer.elapsedMilliseconds,
    );
  }

  Future<void> close() async {
    await _depth?.close();
    await _worker.close();
    _interpreter.close();
  }
}

/// Converts a box in the 512-pixel letterboxed model image to normalized
/// coordinates of the portrait-oriented camera preview.
List<double> modelBoxToPreview(
  List<double> box,
  int frameWidth,
  int frameHeight,
  int sensorRotation,
) {
  final rotated = sensorRotation % 180 != 0;
  final imageWidth = rotated ? frameHeight : frameWidth;
  final imageHeight = rotated ? frameWidth : frameHeight;
  final scale = math.min(512 / imageWidth, 512 / imageHeight);
  final padX = (512 - imageWidth * scale) / 2;
  final padY = (512 - imageHeight * scale) / 2;
  return [
    ((box[0] - padX) / (imageWidth * scale)).clamp(0.0, 1.0),
    ((box[1] - padY) / (imageHeight * scale)).clamp(0.0, 1.0),
    ((box[2] - padX) / (imageWidth * scale)).clamp(0.0, 1.0),
    ((box[3] - padY) / (imageHeight * scale)).clamp(0.0, 1.0),
  ];
}

Float32List _prepareFrame(Map<String, Object> data) {
  final width = data['width']! as int;
  final height = data['height']! as int;
  final rotation = (data['rotation']! as int) % 360;
  final planes = data['planes']! as List<Uint8List>;
  final rows = data['rowStrides']! as List<int>;
  final pixels = data['pixelStrides']! as List<int>;
  final orientedWidth = rotation == 90 || rotation == 270 ? height : width;
  final orientedHeight = rotation == 90 || rotation == 270 ? width : height;
  final scale = math.min(512 / orientedWidth, 512 / orientedHeight);
  final scaledWidth = orientedWidth * scale;
  final scaledHeight = orientedHeight * scale;
  final padX = (512 - scaledWidth) / 2;
  final padY = (512 - scaledHeight) / 2;
  final input = Float32List(512 * 512 * 3);
  input.fillRange(0, input.length, 114 / 255);
  for (var ty = 0; ty < 512; ty++) {
    final oy = ((ty - padY) / scale).floor();
    if (oy < 0 || oy >= orientedHeight) continue;
    for (var tx = 0; tx < 512; tx++) {
      final ox = ((tx - padX) / scale).floor();
      if (ox < 0 || ox >= orientedWidth) continue;
      late int sx, sy;
      switch (rotation) {
        case 90:
          sx = oy;
          sy = height - 1 - ox;
          break;
        case 180:
          sx = width - 1 - ox;
          sy = height - 1 - oy;
          break;
        case 270:
          sx = width - 1 - oy;
          sy = ox;
          break;
        default:
          sx = ox;
          sy = oy;
          break;
      }
      final yIndex = sy * rows[0] + sx * pixels[0];
      final uvX = sx ~/ 2;
      final uvY = sy ~/ 2;
      final uIndex = uvY * rows[1] + uvX * pixels[1];
      final vIndex = uvY * rows[2] + uvX * pixels[2];
      if (yIndex >= planes[0].length ||
          uIndex >= planes[1].length ||
          vIndex >= planes[2].length) {
        continue;
      }
      final y = planes[0][yIndex].toDouble();
      final u = planes[1][uIndex] - 128.0;
      final v = planes[2][vIndex] - 128.0;
      final index = (ty * 512 + tx) * 3;
      input[index] = ((y + 1.402 * v).clamp(0, 255)) / 255;
      input[index + 1] =
          ((y - 0.344136 * u - 0.714136 * v).clamp(0, 255)) / 255;
      input[index + 2] = ((y + 1.772 * u).clamp(0, 255)) / 255;
    }
  }
  return input;
}

typedef _ModelDetection = ({String label, double score, List<double> box});

/// Decode and suppress in model space, then derive direction in preview space.
/// The rear camera preview is not mirrored. 'ahead' is the center third.
List<Detection> decodeDetections(
  Float32List output,
  int frameWidth,
  int frameHeight,
  int sensorRotation,
) {
  if (output.length != 12 * 5376 || frameWidth <= 0 || frameHeight <= 0) {
    throw ArgumentError('Invalid detector output or frame dimensions.');
  }
  return _decode(output).map((detection) {
    final box = modelBoxToPreview(
      detection.box,
      frameWidth,
      frameHeight,
      sensorRotation,
    );
    final center = (box[0] + box[2]) / 2;
    return Detection(
      detection.label,
      detection.score,
      center < 1 / 3
          ? 'left'
          : center < 2 / 3
          ? 'ahead'
          : 'right',
      box,
    );
  }).toList();
}

List<_ModelDetection> _decode(Float32List output) {
  const count = 5376;
  final candidates = <_ModelDetection>[];
  for (var i = 0; i < count; i++) {
    var bestClass = 0;
    var bestScore = 0.25;
    for (var cls = 0; cls < classNames.length; cls++) {
      final score = output[(4 + cls) * count + i];
      if (score > bestScore) {
        bestClass = cls;
        bestScore = score;
      }
    }
    if (bestScore == 0.25) continue;
    final x = output[i];
    final y = output[count + i];
    final w = output[2 * count + i];
    final h = output[3 * count + i];
    if (!x.isFinite ||
        !y.isFinite ||
        !w.isFinite ||
        !h.isFinite ||
        w <= 0 ||
        h <= 0) {
      continue;
    }
    final box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2];
    candidates.add((label: classNames[bestClass], score: bestScore, box: box));
  }
  candidates.sort((a, b) => b.score.compareTo(a.score));
  final accepted = <_ModelDetection>[];
  for (final candidate in candidates) {
    if (accepted.length >= 12) break;
    if (accepted.any(
      (other) =>
          other.label == candidate.label &&
          _iou(other.box, candidate.box) > 0.5,
    )) {
      continue;
    }
    accepted.add(candidate);
  }
  return accepted;
}

double _iou(List<double> a, List<double> b) {
  final left = math.max(a[0], b[0]);
  final top = math.max(a[1], b[1]);
  final right = math.min(a[2], b[2]);
  final bottom = math.min(a[3], b[3]);
  final intersection = math.max(0, right - left) * math.max(0, bottom - top);
  final areaA = math.max(0, a[2] - a[0]) * math.max(0, a[3] - a[1]);
  final areaB = math.max(0, b[2] - b[0]) * math.max(0, b[3] - b[1]);
  return intersection / (areaA + areaB - intersection + 1e-6);
}

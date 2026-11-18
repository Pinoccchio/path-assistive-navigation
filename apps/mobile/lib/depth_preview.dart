import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

const depthPreviewEnabled =
    !kReleaseMode &&
    bool.fromEnvironment('PATH_DEPTH_PREVIEW', defaultValue: true);

class DepthPreviewModel {
  DepthPreviewModel._(this.model, this.worker);
  final Interpreter model;
  final IsolateInterpreter worker;

  static Future<DepthPreviewModel> load() async {
    final model = await Interpreter.fromAsset(
      'assets/model/midas_small.tflite',
      options: InterpreterOptions()..threads = 2,
    );
    try {
      final input = model.getInputTensor(0);
      final output = model.getOutputTensor(0);
      if (!listEquals(input.shape, [1, 256, 256, 3]) ||
          !listEquals(output.shape, [1, 256, 256, 1]) ||
          input.type != TensorType.float32 ||
          output.type != TensorType.float32) {
        throw StateError('Unexpected MiDaS tensor format');
      }
      return DepthPreviewModel._(
        model,
        await IsolateInterpreter.create(address: model.address),
      );
    } catch (_) {
      model.close();
      rethrow;
    }
  }

  Future<DepthMap> estimate(Float32List rgb, int width, int height) async {
    final input = await compute(prepareDepthInput, (rgb, width, height));
    final output = Float32List(256 * 256);
    await worker.run(input.buffer.asUint8List(), output.buffer.asUint8List());
    return DepthMap.fromOutput(output);
  }

  Future<void> close() async {
    await worker.close();
    model.close();
  }
}

// Reuse the oriented RGB detector frame, removing its letterbox before resizing.
Float32List prepareDepthInput((Float32List, int, int) frame) {
  final (rgb, width, height) = frame;
  final scale = 512 / math.max(width, height);
  final w = width * scale;
  final h = height * scale;
  final input = Float32List(256 * 256 * 3);
  const mean = [0.485, 0.456, 0.406];
  const std = [0.229, 0.224, 0.225];
  for (int y = 0; y < 256; y++) {
    final sy = ((512 - h) / 2 + (y + 0.5) * h / 256).floor();
    for (int x = 0; x < 256; x++) {
      final sx = ((512 - w) / 2 + (x + 0.5) * w / 256).floor();
      for (int c = 0; c < 3; c++) {
        input[(y * 256 + x) * 3 + c] =
            (rgb[(sy * 512 + sx) * 3 + c] - mean[c]) / std[c];
      }
    }
  }
  return input;
}

class DepthMap {
  DepthMap._(this.shades, this._samples);
  final List<double> _samples;
  final Uint8List shades;
  static const side = 32;
  factory DepthMap.fromOutput(Float32List values) {
    final samples = List.generate(
      side * side,
      (i) => values[((i ~/ side) * 8 + 4) * 256 + (i % side) * 8 + 4],
    );
    if (samples.any((v) => !v.isFinite)) {
      throw StateError('Invalid MiDaS output');
    }
    final min = samples.reduce(math.min);
    final range = samples.reduce(math.max) - min;
    return DepthMap._(
      Uint8List.fromList([
        for (final v in samples)
          range > 0 ? ((v - min) * 255 / range).round() : 128,
      ]),
      samples,
    );
  }

  double? medianInverseDepth(List<double> box) {
    if (box.length != 4 || box.any((v) => !v.isFinite || v < 0 || v > 1)) {
      return null;
    }
    final dx = (box[2] - box[0]) / 4;
    final dy = (box[3] - box[1]) / 4;
    final samples = <double>[];
    for (var y = 0; y < side; y++) {
      final cy = (y + 0.5) / side;
      if (cy < box[1] + dy || cy > box[3] - dy) continue;
      for (var x = 0; x < side; x++) {
        final cx = (x + 0.5) / side;
        if (cx >= box[0] + dx && cx <= box[2] - dx) {
          samples.add(_samples[y * side + x]);
        }
      }
    }
    if (samples.length < 4) return null;
    samples.sort();
    return (samples[(samples.length - 1) ~/ 2] + samples[samples.length ~/ 2]) /
        2;
  }

  // Research heuristic: compare median inverse depth inside the central half
  // of each box. Abstain if any object has too few samples to compare.
  int? closerBox(List<List<double>> boxes) {
    if (boxes.length < 2) return null;
    final scores = <({int index, double depth})>[];
    for (var index = 0; index < boxes.length; index++) {
      final box = boxes[index];
      final median = medianInverseDepth(box);
      if (median == null) return null;
      scores.add((index: index, depth: median));
    }
    scores.sort((a, b) => b.depth.compareTo(a.depth));
    final first = scores.first;
    final gap = first.depth - scores[1].depth;
    final span = _samples.reduce(math.max) - _samples.reduce(math.min);
    final margin = math.max(first.depth.abs(), span) * 0.10;
    return gap > margin ? first.index : null;
  }
}

class DepthPainter extends CustomPainter {
  DepthPainter(this.map);
  final DepthMap map;
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..isAntiAlias = false;
    final dx = size.width / DepthMap.side;
    final dy = size.height / DepthMap.side;
    for (int i = 0; i < map.shades.length; i++) {
      final shade = map.shades[i];
      paint.color = Color.fromARGB(255, shade, shade, shade);
      canvas.drawRect(
        Rect.fromLTWH(
          (i % DepthMap.side) * dx,
          (i ~/ DepthMap.side) * dy,
          dx,
          dy,
        ),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(DepthPainter oldDelegate) => map != oldDelegate.map;
}

class DepthReadout extends StatelessWidget {
  const DepthReadout({
    super.key,
    required this.map,
    required this.detectorMs,
    required this.combinedMs,
    required this.aspect,
    this.onCalibrate,
    this.zoneStatus,
  });
  final DepthMap map;
  final int detectorMs, combinedMs;
  final double aspect;
  final VoidCallback? onCalibrate;
  final String? zoneStatus;

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 8),
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
    decoration: BoxDecoration(
      color: const Color(0xff181818),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(
      children: [
        SizedBox(
          width: 56,
          height: 72,
          child: Center(
            child: AspectRatio(
              aspectRatio: aspect,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: CustomPaint(painter: DepthPainter(map)),
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Relative depth',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (zoneStatus != null)
                Text(
                  zoneStatus!,
                  style: const TextStyle(
                    color: Colors.amber,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              const Text(
                'Brighter means closer',
                style: TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 4),
              Wrap(
                spacing: 16,
                runSpacing: 2,
                children: [
                  Text(
                    'Detector $detectorMs ms',
                    style: const TextStyle(fontSize: 16),
                  ),
                  Text(
                    'Combined $combinedMs ms',
                    style: const TextStyle(fontSize: 16),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (onCalibrate != null)
          IconButton(
            tooltip: 'Calibrate distance',
            icon: const Icon(Icons.straighten),
            onPressed: onCalibrate,
          ),
      ],
    ),
  );
}

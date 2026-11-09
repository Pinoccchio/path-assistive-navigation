import 'package:flutter/material.dart';

import 'detector.dart';

String detectionBoxLabel(Detection detection) =>
    '${detection.label.toUpperCase()} · ${detection.direction.toUpperCase()}';

/// Fits the entire oriented image and paints labels in display logical pixels,
/// so fitting a camera image does not shrink its text or misalign its boxes.
class ProportionalDetectionPreview extends StatelessWidget {
  const ProportionalDetectionPreview({
    super.key,
    required this.imageSize,
    required this.image,
    required this.detections,
  });
  final Size imageSize;
  final Widget image;
  final List<Detection> detections;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final fitted = applyBoxFit(
        BoxFit.contain,
        imageSize,
        constraints.biggest,
      ).destination;
      return Center(
        child: SizedBox(
          key: const ValueKey('camera-image-plane'),
          width: fitted.width,
          height: fitted.height,
          child: Stack(
            fit: StackFit.expand,
            children: [
              image,
              DetectionOverlay(detections: detections),
            ],
          ),
        ),
      );
    },
  );
}

class DetectionOverlay extends StatelessWidget {
  const DetectionOverlay({super.key, required this.detections});

  final List<Detection> detections;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) => IgnorePointer(
        child: ExcludeSemantics(
          child: CustomPaint(
            painter: _DetectionPainter(
              detections,
              constraints.biggest,
              MediaQuery.textScalerOf(context),
            ),
            size: Size.infinite,
          ),
        ),
      ),
    );
  }
}

class _DetectionPainter extends CustomPainter {
  _DetectionPainter(this.detections, this.bounds, this.textScaler) {
    if (bounds.width < 32 || bounds.height < 32 || !bounds.isFinite) return;
    for (final detection in detections) {
      final box = detection.box;
      if (box.length != 4 ||
          box.any((v) => !v.isFinite) ||
          box[2] <= box[0] ||
          box[3] <= box[1]) {
        continue;
      }
      final rect = Rect.fromLTRB(
        (box[0] * bounds.width).clamp(2.0, bounds.width - 2),
        (box[1] * bounds.height).clamp(2.0, bounds.height - 2),
        (box[2] * bounds.width).clamp(2.0, bounds.width - 2),
        (box[3] * bounds.height).clamp(2.0, bounds.height - 2),
      );
      if (rect.isEmpty) continue;
      final text = TextPainter(
        text: TextSpan(
          text: detectionBoxLabel(detection),
          style: const TextStyle(
            fontFamily: 'Inter',
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.w700,
            height: 1.15,
          ),
        ),
        textDirection: TextDirection.ltr,
        textScaler: textScaler,
        maxLines: 2,
        ellipsis: '…',
      )..layout(maxWidth: bounds.width - 20);
      final width = text.width + 12, height = text.height + 8;
      Rect at(double x, double y) => Rect.fromLTWH(
        x.clamp(4.0, bounds.width - width - 4),
        y.clamp(4.0, (bounds.height - height - 4).clamp(4.0, bounds.height)),
        width,
        height,
      );
      final candidates = [
        at(rect.left, rect.top - height),
        at(rect.left, rect.top),
        at(rect.right - width, rect.bottom),
        at(rect.right - width, rect.top - height),
      ];
      final label = candidates.firstWhere(
        (r) => _drawn.every((d) => !r.overlaps(d.label.outerRect.inflate(2))),
        orElse: () => candidates.first,
      );
      _drawn.add(
        _DrawnBox(
          rect,
          RRect.fromRectAndRadius(label, const Radius.circular(4)),
          text,
          Offset(label.left + 6, label.top + 4),
        ),
      );
    }
  }

  final List<Detection> detections;
  final Size bounds;
  final TextScaler textScaler;
  final _drawn = <_DrawnBox>[];
  static const color = Color(0xFFFFD700);
  final Paint outline = Paint()
    ..color = color
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2.5;
  final Paint background = Paint()..color = const Color(0xFF000000);

  @override
  void paint(Canvas canvas, Size size) {
    for (final box in _drawn) {
      canvas.drawRect(box.rect, outline);
      canvas.drawRRect(box.label, background);
      box.text.paint(canvas, box.textOffset);
    }
  }

  @override
  bool shouldRepaint(covariant _DetectionPainter oldDelegate) =>
      oldDelegate.detections != detections ||
      oldDelegate.bounds != bounds ||
      oldDelegate.textScaler != textScaler;
}

class _DrawnBox {
  const _DrawnBox(this.rect, this.label, this.text, this.textOffset);
  final Rect rect;
  final RRect label;
  final TextPainter text;
  final Offset textOffset;
}

import 'package:flutter/material.dart';

import 'detector.dart';

class DetectionOverlay extends StatelessWidget {
  const DetectionOverlay({super.key, required this.detections});

  final List<Detection> detections;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: ExcludeSemantics(
        child: CustomPaint(
          painter: _DetectionPainter(detections),
          size: Size.infinite,
        ),
      ),
    );
  }
}

class _DetectionPainter extends CustomPainter {
  _DetectionPainter(this.detections);

  final List<Detection> detections;
  static const color = Color(0xFFFFD700);
  final Paint outline = Paint()
    ..color = color
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2.5;
  final Paint background = Paint()..color = const Color(0xFF000000);

  @override
  void paint(Canvas canvas, Size size) {
    for (final detection in detections) {
      final box = detection.box;
      if (box.length != 4 || box[2] <= box[0] || box[3] <= box[1]) continue;
      final rect = Rect.fromLTRB(
        box[0] * size.width,
        box[1] * size.height,
        box[2] * size.width,
        box[3] * size.height,
      );
      canvas.drawRect(rect, outline);
      final text = TextPainter(
        text: TextSpan(
          text: '${detection.label} ${(detection.score * 100).round()}%',
          style: const TextStyle(
            fontFamily: 'Inter',
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
        maxLines: 1,
        ellipsis: '…',
      )..layout(maxWidth: size.width - 16);
      final labelWidth = text.width + 12;
      final labelHeight = text.height + 6;
      final labelX = rect.left.clamp(0.0, size.width - labelWidth);
      final labelY = (rect.top - labelHeight).clamp(
        0.0,
        size.height - labelHeight,
      );
      final labelRect = Rect.fromLTWH(labelX, labelY, labelWidth, labelHeight);
      canvas.drawRRect(
        RRect.fromRectAndRadius(labelRect, const Radius.circular(4)),
        background,
      );
      text.paint(canvas, Offset(labelX + 6, labelY + 3));
    }
  }

  @override
  bool shouldRepaint(covariant _DetectionPainter oldDelegate) =>
      oldDelegate.detections != detections;
}

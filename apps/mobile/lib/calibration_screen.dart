import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import 'package:shared_preferences/shared_preferences.dart';

import 'depth_preview.dart';
import 'detector.dart';
import 'zone_preview.dart';

// Remove detector letterboxing before drawing normalized object boxes.
Uint8List encodeCalibrationFrame((Float32List, double) frame) {
  final (rgb, aspect) = frame;
  final w = (aspect < 1 ? 512 * aspect : 512).round().clamp(1, 512);
  final h = (aspect > 1 ? 512 / aspect : 512).round().clamp(1, 512);
  final image = img.Image(width: w, height: h);
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      final i = (((512 - h) ~/ 2 + y) * 512 + (512 - w) ~/ 2 + x) * 3;
      image.setPixelRgb(
        x,
        y,
        (rgb[i] * 255).round(),
        (rgb[i + 1] * 255).round(),
        (rgb[i + 2] * 255).round(),
      );
    }
  }
  return img.encodeJpg(image);
}

class CalibrationScreen extends StatefulWidget {
  const CalibrationScreen({
    super.key,
    required this.depth,
    required this.detections,
    required this.frameUtc,
    required this.aspect,
    this.rgb,
  });
  final DepthMap depth;
  final List<Detection> detections;
  final DateTime frameUtc;
  final double aspect;
  final Float32List? rgb;

  @override
  State<CalibrationScreen> createState() => _CalibrationScreenState();
}

class _CalibrationScreenState extends State<CalibrationScreen> {
  static const prefix = 'path.calibration.v1.';
  final distance = TextEditingController();
  final store = SharedPreferencesAsync();
  late final estimates = widget.detections
      .map((d) => widget.depth.medianInverseDepth(d.box))
      .toList();
  late final photo = widget.rgb == null
      ? null
      : compute(encodeCalibrationFrame, (widget.rgb!, widget.aspect));
  int? selected;
  ResearchZone? referenceZone;
  String? error;
  bool saving = false, saved = false;
  int? count;

  @override
  void initState() {
    super.initState();
    final index = estimates.indexWhere((v) => v != null);
    final closer = widget.detections.indexWhere((d) => d.closer);
    selected = closer >= 0 && estimates[closer] != null
        ? closer
        : index < 0
        ? null
        : index;
    _loadCount();
  }

  Future<void> _loadCount() async {
    try {
      final keys = await store.getKeys();
      if (mounted && !saved) {
        setState(() => count = keys.where((k) => k.startsWith(prefix)).length);
      }
    } catch (_) {
      if (mounted) setState(() => error = 'Could not read local samples.');
    }
  }

  Future<void> _save() async {
    final index = selected;
    if (index == null || saving || saved) return;
    final cm = double.tryParse(distance.text.trim());
    if (cm == null || !cm.isFinite || cm <= 0) {
      setState(
        () => error =
            'Enter a measured distance greater than zero in centimeters.',
      );
      return;
    }
    setState(() {
      saving = true;
      error = null;
    });
    final object = widget.detections[index];
    final id = '$prefix${widget.frameUtc.microsecondsSinceEpoch}.$index';
    try {
      await store.setString(
        id,
        jsonEncode({
          'frameUtc': widget.frameUtc.toIso8601String(),
          'objectIndex': index,
          'label': object.label,
          'direction': object.direction,
          'box': object.box,
          'confidence': object.score,
          'distanceCm': cm,
          if (referenceZone != null)
            'physicalReferenceZone': referenceZone!.name,
          'medianInverseDepth': estimates[index],
          'model': 'MiDaS v2.1 small',
        }),
      );
      if (mounted) {
        setState(() {
          saved = true;
          if (count != null) count = count! + 1;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => error = 'Could not save on this phone. Try again.');
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  void dispose() {
    distance.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final index = selected;
    final locked = saved || saving;
    return Scaffold(
      appBar: AppBar(title: const Text('Distance calibration')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              'Researchers use this screen to test when PATH should say "nearby." '
              'Measure from the phone camera to the selected object in centimeters, '
              'then save the measurement with its depth reading.',
              style: TextStyle(fontSize: 16, height: 1.4),
            ),
            const SizedBox(height: 16),
            const Text(
              'Captured scene',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 180,
              child: Center(
                child: AspectRatio(
                  aspectRatio: widget.aspect,
                  child: LayoutBuilder(
                    builder: (context, size) => Stack(
                      fit: StackFit.expand,
                      children: [
                        FutureBuilder<Uint8List>(
                          future: photo,
                          builder: (context, snapshot) => snapshot.hasData
                              ? Image.memory(snapshot.data!, fit: BoxFit.fill)
                              : CustomPaint(
                                  painter: DepthPainter(widget.depth),
                                ),
                        ),
                        if (index != null)
                          Positioned.fromRect(
                            rect: Rect.fromLTRB(
                              widget.detections[index].box[0] * size.maxWidth,
                              widget.detections[index].box[1] * size.maxHeight,
                              widget.detections[index].box[2] * size.maxWidth,
                              widget.detections[index].box[3] * size.maxHeight,
                            ),
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: Colors.yellow,
                                  width: 3,
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            if (index == null)
              const Text(
                'No object has enough depth samples. Return to the camera and capture another frame.',
              )
            else ...[
              DropdownButtonFormField<int>(
                value: index,
                isExpanded: true,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Selected object',
                ),
                items: [
                  for (var i = 0; i < estimates.length; i++)
                    if (estimates[i] != null)
                      DropdownMenuItem(
                        value: i,
                        child: Text(
                          '${i + 1}. ${widget.detections[i].label} - ${widget.detections[i].direction}',
                        ),
                      ),
                ],
                onChanged: locked
                    ? null
                    : (value) => setState(() {
                        selected = value;
                        referenceZone = null;
                        distance.clear();
                        error = null;
                      }),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  'Relative depth score: ${estimates[index]!.toStringAsFixed(2)}\nHigher means closer within this frame.',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: distance,
                enabled: !locked,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Measured distance (cm)',
                  hintText: 'Enter tape measurement',
                ),
              ),
              const SizedBox(height: 16),
              ExpansionTile(
                title: const Text('Physical zone reference'),
                subtitle: Text(
                  referenceZone?.title ?? 'Optional for measured objects',
                ),
                children: [
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      'For a real object, select the zone assigned by your study protocol at the measured distance. Leave monitor and practice samples untagged.',
                    ),
                  ),
                  Wrap(
                    spacing: 8,
                    children: [
                      for (final zone in ResearchZone.values)
                        ChoiceChip(
                          label: Text(zone.title),
                          selected: referenceZone == zone,
                          onSelected: locked
                              ? null
                              : (on) => setState(
                                  () => referenceZone = on ? zone : null,
                                ),
                        ),
                    ],
                  ),
                ],
              ),
              OutlinedButton(
                onPressed: saving
                    ? null
                    : () => Navigator.push<void>(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ZonePreviewScreen(
                            scene: [
                              for (var i = 0; i < widget.detections.length; i++)
                                (
                                  label: widget.detections[i].label,
                                  direction: widget.detections[i].direction,
                                  score: estimates[i],
                                ),
                            ],
                            label: widget.detections[index].label,
                            direction: widget.detections[index].direction,
                            score: estimates[index]!,
                            frameUtc: widget.frameUtc,
                          ),
                        ),
                      ),
                child: const Text('View zone estimate'),
              ),
              FilledButton(
                onPressed: locked ? null : _save,
                child: Text(
                  saved
                      ? 'Sample saved on phone'
                      : saving
                      ? 'Saving...'
                      : 'Save sample',
                ),
              ),
            ],
            if (error != null)
              Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            if (count != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text('Saved samples: $count'),
              ),
            TextButton(
              onPressed: saving ? null : () => Navigator.pop(context),
              child: const Text('Return to camera'),
            ),
          ],
        ),
      ),
    );
  }
}

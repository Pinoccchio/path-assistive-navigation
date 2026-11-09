import 'dart:math' as math;
import 'detector.dart';

bool validSceneDetection(Detection d) =>
    d.score.isFinite &&
    d.score > .25 &&
    d.score <= 1 &&
    classNames.contains(d.label) &&
    const ['left', 'ahead', 'right'].contains(d.direction) &&
    d.box.length == 4 &&
    d.box.every((v) => v.isFinite && v >= 0 && v <= 1) &&
    d.box[2] > d.box[0] &&
    d.box[3] > d.box[1];

/// Bounded class-aware box association, not identity recognition or full SORT.
/// Defaults are research parameters; stability and added delay need phone QA.
class TemporalSceneTracker {
  TemporalSceneTracker({this.confirmationFrames = 2, this.maxMissedFrames = 1});
  final int confirmationFrames, maxMissedFrames;
  static const maxGap = Duration(milliseconds: 1500);
  final _tracks = <_Track>[];
  DateTime? _updated;
  void reset() {
    _tracks.clear();
    _updated = null;
  }

  List<Detection> update(List<Detection> detections, DateTime now) {
    if (_updated != null && now.difference(_updated!) > maxGap) reset();
    _updated = now;
    _tracks.removeWhere((t) => now.difference(t.seen) > maxGap);
    final current = detections.where(validSceneDetection).toList()
      ..sort((a, b) => b.score.compareTo(a.score));
    final boxes = current.take(12).toList();
    final pairs = <({int track, int box, double overlap})>[];
    for (var i = 0; i < _tracks.length; i++) {
      for (var j = 0; j < boxes.length; j++) {
        if (_tracks[i].detection.label != boxes[j].label) continue;
        final overlap = _iou(_tracks[i].detection.box, boxes[j].box);
        if (overlap >= .2) pairs.add((track: i, box: j, overlap: overlap));
      }
    }
    pairs.sort((a, b) {
      final result = b.overlap.compareTo(a.overlap);
      if (result != 0) return result;
      final track = a.track.compareTo(b.track);
      return track != 0 ? track : a.box.compareTo(b.box);
    });
    final usedTracks = <int>{}, usedBoxes = <int>{};
    for (final pair in pairs) {
      if (usedTracks.contains(pair.track) || usedBoxes.contains(pair.box)) {
        continue;
      }
      usedTracks.add(pair.track);
      usedBoxes.add(pair.box);
      _tracks[pair.track].observe(boxes[pair.box], now, confirmationFrames);
    }
    for (var i = 0; i < _tracks.length; i++) {
      if (!usedTracks.contains(i)) {
        _tracks[i].misses++;
        if (!_tracks[i].confirmed) _tracks[i].hits = 0;
      }
    }
    _tracks.removeWhere((t) => t.misses > maxMissedFrames);
    for (var j = 0; j < boxes.length; j++) {
      if (!usedBoxes.contains(j)) {
        _tracks.add(_Track(boxes[j], now, confirmationFrames <= 1));
      }
    }
    return [
      for (final t in _tracks)
        if (t.confirmed)
          Detection(
            t.detection.label,
            t.detection.score,
            t.direction,
            List.unmodifiable(t.detection.box),
          ),
    ];
  }

  double _iou(List<double> a, List<double> b) {
    final intersection =
        math.max(0.0, math.min(a[2], b[2]) - math.max(a[0], b[0])) *
        math.max(0.0, math.min(a[3], b[3]) - math.max(a[1], b[1]));
    final union =
        (a[2] - a[0]) * (a[3] - a[1]) +
        (b[2] - b[0]) * (b[3] - b[1]) -
        intersection;
    return union > 0 ? intersection / union : 0;
  }
}

class _Track {
  _Track(this.detection, this.seen, this.confirmed)
    : direction = detection.direction;
  Detection detection;
  DateTime seen;
  bool confirmed;
  int hits = 1, misses = 0, directionHits = 0;
  String direction;
  String? pendingDirection;
  void observe(Detection next, DateTime now, int confirmations) {
    hits++;
    misses = 0;
    seen = now;
    detection = next;
    confirmed = confirmed || hits >= confirmations;
    if (next.direction == direction) {
      pendingDirection = null;
      directionHits = 0;
    } else {
      directionHits = pendingDirection == next.direction
          ? directionHits + 1
          : 1;
      pendingDirection = next.direction;
      if (directionHits >= confirmations) {
        direction = next.direction;
        pendingDirection = null;
        directionHits = 0;
      }
    }
  }
}

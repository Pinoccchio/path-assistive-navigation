import 'detector.dart';
import 'path_preferences.dart';

typedef SceneKey = ({String label, String direction});

class SceneGroup {
  const SceneGroup(this.key, this.count, this.score);
  final SceneKey key;
  final int count;
  final double score;
  String phrase(DirectionFormat format) {
    final label = key.label;
    final objects = count == 1
        ? label
        : switch (label) {
            'person' => '$count people',
            'stairs' => '$count sets of stairs',
            _ => '$count ${label}s',
          };
    final direction = format == DirectionFormat.clockHand
        ? switch (key.direction) {
            'left' => "10 o'clock",
            'right' => "2 o'clock",
            _ => "12 o'clock",
          }
        : key.direction;
    return '$objects, $direction.';
  }
}

List<SceneGroup> groupScene(Iterable<Detection> detections) {
  final groups = <SceneKey, ({int count, double score})>{};
  for (final d in detections) {
    final key = (label: d.label, direction: d.direction);
    final previous = groups[key];
    groups[key] = (
      count: (previous?.count ?? 0) + 1,
      score: previous == null || d.score > previous.score
          ? d.score
          : previous.score,
    );
  }
  return [
    for (final g in groups.entries)
      SceneGroup(g.key, g.value.count, g.value.score),
  ]..sort((a, b) {
    final confidence = b.score.compareTo(a.score);
    if (confidence != 0) return confidence;
    final label = a.key.label.compareTo(b.key.label);
    return label != 0 ? label : a.key.direction.compareTo(b.key.direction);
  });
}

String sceneSignature(List<SceneGroup> groups, DirectionFormat format) {
  final keys = [
    for (final g in groups) '${g.key.label}:${g.key.direction}:${g.count}',
  ]..sort();
  return '${format.name}|${keys.join('|')}';
}

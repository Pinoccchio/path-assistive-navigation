import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum ResearchZone {
  danger('Danger'),
  caution('Caution'),
  farther('Farther');

  const ResearchZone(this.title);
  final String title;
}

typedef ZoneReference = ({ResearchZone zone, double cm, double score});

String estimateZone(List<ZoneReference> references, double current) {
  final groups = [
    for (final zone in ResearchZone.values)
      references
          .where(
            (r) =>
                r.zone == zone && r.cm.isFinite && r.cm > 0 && r.score.isFinite,
          )
          .toList(),
  ];
  final missing = ResearchZone.values.where((z) => groups[z.index].isEmpty);
  if (missing.isNotEmpty) {
    return 'Need measured references for ${missing.map((z) => z.title).join(', ')}.';
  }
  final depths = [
    for (final g in groups) (g.map((r) => r.score).toList()..sort()),
  ];
  final distances = [
    for (final g in groups) (g.map((r) => r.cm).toList()..sort()),
  ];
  for (var i = 0; i < 2; i++) {
    if (distances[i].last >= distances[i + 1].first ||
        depths[i].first <= depths[i + 1].last) {
      return 'Uncertain: the measured distances or depth scores overlap or are out of order.';
    }
  }
  if (!current.isFinite ||
      current > depths.first.last ||
      current < depths.last.first) {
    return 'Unknown: outside the observed depth range.';
  }
  for (var i = 0; i < 2; i++) {
    final boundary = (depths[i].first + depths[i + 1].last) / 2;
    if (current == boundary) return 'Uncertain: score is on a zone boundary.';
    if (current > boundary) return ResearchZone.values[i].title;
  }
  return ResearchZone.farther.title;
}

typedef SceneObjectDepth = ({String label, String direction, double? score});
typedef ScenePriority = ({int index, ResearchZone? zone});

List<ScenePriority> rankScene(
  List<SceneObjectDepth> scene,
  Map<String, List<ZoneReference>> references,
) {
  final priorities = <ScenePriority>[];
  for (var i = 0; i < scene.length; i++) {
    final object = scene[i];
    final estimate = estimateZone(
      references[object.label] ?? [],
      object.score ?? double.nan,
    );
    final zone = ResearchZone.values
        .where((z) => z.title == estimate)
        .firstOrNull;
    priorities.add((index: i, zone: zone));
  }
  priorities.sort((a, b) {
    final byZone = (a.zone?.index ?? 3).compareTo(b.zone?.index ?? 3);
    return byZone == 0 ? a.index.compareTo(b.index) : byZone;
  });
  return priorities;
}

Future<Map<String, List<ZoneReference>>> readZoneReferences({
  DateTime? excludeFrame,
}) async {
  final store = SharedPreferencesAsync();
  final keys = (await store.getKeys())
      .where((k) => k.startsWith('path.calibration.v1.'))
      .toSet();
  if (keys.isEmpty) return {};
  final rows = await store.getAll(allowList: keys);
  final result = <String, List<ZoneReference>>{};
  for (final value in rows.values.whereType<String>()) {
    final row = jsonDecode(value);
    if (row is! Map ||
        row['label'] is! String ||
        row['model'] != 'MiDaS v2.1 small' ||
        row['frameUtc'] == excludeFrame?.toIso8601String()) {
      continue;
    }
    final zone = ResearchZone.values
        .where((z) => z.name == row['physicalReferenceZone'])
        .firstOrNull;
    final cm = row['distanceCm'], score = row['medianInverseDepth'];
    if (zone != null && cm is num && score is num) {
      result.putIfAbsent(row['label'] as String, () => []).add((
        zone: zone,
        cm: cm.toDouble(),
        score: score.toDouble(),
      ));
    }
  }
  return result;
}

class ZonePreviewScreen extends StatefulWidget {
  const ZonePreviewScreen({
    super.key,
    required this.label,
    required this.direction,
    required this.score,
    required this.frameUtc,
    required this.scene,
  });
  final List<SceneObjectDepth> scene;
  final String label, direction;
  final double score;
  final DateTime frameUtc;
  @override
  State<ZonePreviewScreen> createState() => _ZonePreviewScreenState();
}

class _ZonePreviewScreenState extends State<ZonePreviewScreen> {
  late final data = readZoneReferences(excludeFrame: widget.frameUtc);
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Zone estimate')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            '${widget.label} - ${widget.direction}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          Text('Captured depth score: ${widget.score.toStringAsFixed(2)}'),
          const SizedBox(height: 20),
          FutureBuilder<Map<String, List<ZoneReference>>>(
            future: data,
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return const Text('Could not read calibration samples.');
              }
              if (!snapshot.hasData) return const LinearProgressIndicator();
              final rows = snapshot.data![widget.label] ?? <ZoneReference>[];
              final priorities = rankScene(widget.scene, snapshot.data!);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    estimateZone(rows, widget.score),
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  for (final z in ResearchZone.values)
                    Text(
                      '${z.title} references: ${rows.where((r) => r.zone == z).length}',
                    ),
                  const SizedBox(height: 16),
                  Text(
                    'Scene priority',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  for (final item in priorities.where((p) => p.zone != null))
                    Text(
                      '${item.zone!.title}: ${widget.scene[item.index].label}, ${widget.scene[item.index].direction}',
                    ),
                  if (priorities.every((p) => p.zone == null))
                    const Text('No object has an estimated zone yet.'),
                  if (priorities.any((p) => p.zone == null)) ...[
                    const SizedBox(height: 8),
                    const Text('Unclassified objects'),
                    for (final item in priorities.where((p) => p.zone == null))
                      Text(
                        '${widget.scene[item.index].label}, ${widget.scene[item.index].direction}',
                      ),
                  ],
                  const SizedBox(height: 16),
                  const Text(
                    'Research preview. Compare this estimate with a separately measured scene. Only tagged physical samples of the same object class from other frames are used.',
                  ),
                ],
              );
            },
          ),
        ],
      ),
    ),
  );
}

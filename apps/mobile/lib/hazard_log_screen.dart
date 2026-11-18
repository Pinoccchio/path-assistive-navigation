import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'path_page.dart';
import 'hazard_history.dart';
import 'session_view.dart';

enum HazardSeverity { danger, caution, safe }

/// UI input only. The runtime alert/history pipeline is not connected yet.
class HazardLogEntry {
  const HazardLogEntry({
    required this.object,
    required this.direction,
    required this.time,
    required this.severity,
    this.distanceMeters,
  });
  final String object, direction, time;
  final HazardSeverity severity;
  final double? distanceMeters;
}

class HazardLogScreen extends StatefulWidget {
  const HazardLogScreen({
    super.key,
    this.entries = const [],
    this.previewMode = false,
  });
  final List<HazardLogEntry> entries;
  final bool previewMode;

  @override
  State<HazardLogScreen> createState() => _HazardLogScreenState();
}

class _HazardLogScreenState extends State<HazardLogScreen> {
  late List<HazardLogEntry> _entries;

  @override
  void initState() {
    super.initState();
    _entries = List.of(widget.previewMode ? _figmaEntries : widget.entries);
  }

  @override
  void didUpdateWidget(covariant HazardLogScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.entries != oldWidget.entries ||
        widget.previewMode != oldWidget.previewMode) {
      _entries = List.of(widget.previewMode ? _figmaEntries : widget.entries);
    }
  }

  void _clear() {
    if (_entries.isEmpty) {
      showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('No saved detections'),
          content: Text(
            widget.previewMode
                ? 'The preview log is already empty.'
                : 'The displayed cards are layout placeholders. Detection history is in development.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              style: TextButton.styleFrom(minimumSize: const Size(64, 64)),
              child: const Text('Close'),
            ),
          ],
        ),
      );
      return;
    }
    final previous = List<HazardLogEntry>.of(_entries);
    setState(() => _entries.clear());
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          widget.previewMode ? 'Preview log cleared' : 'Log cleared',
        ),
        action: SnackBarAction(
          label: 'Undo',
          onPressed: () {
            if (mounted) setState(() => _entries = previous);
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final expandedText = MediaQuery.textScalerOf(context).scale(18) > 27;
          final compact =
              !widget.previewMode &&
              constraints.maxHeight < 800 &&
              MediaQuery.textScalerOf(context).scale(18) <= 23;
          final cards = _entries.isEmpty
              ? widget.previewMode
                    ? <Widget>[
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 48),
                          child: Text(
                            'No detections',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 24, color: Colors.white),
                          ),
                        ),
                      ]
                    : [
                        for (final severity in HazardSeverity.values)
                          _HazardCard(
                            key: ValueKey('hazard-preview-${severity.name}'),
                            entry: HazardLogEntry(
                              object: 'In development',
                              direction: '',
                              time: '\u2014',
                              severity: severity,
                            ),
                            preview: true,
                            compact: compact,
                          ),
                      ]
              : [
                  for (final entry in _entries)
                    _HazardCard(
                      entry: entry,
                      compact: compact,
                      sampleData: widget.previewMode,
                    ),
                ];
          return ListView(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            children: [
              if (widget.previewMode && expandedText) ...[
                Semantics(
                  label:
                      'Design preview. All location and hazard data are samples.',
                  excludeSemantics: true,
                  child: const Align(
                    alignment: Alignment.centerRight,
                    child: Text(
                      'PREVIEW',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: pathYellow,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
              ],
              const PathPageHeader(title: 'Hazard Log & GPS Context'),
              SizedBox(height: compact ? 16 : 24),
              ConstrainedBox(
                constraints: BoxConstraints(minHeight: compact ? 92 : 100),
                child: DecoratedBox(
                  decoration: _panelDecoration,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        ExcludeSemantics(
                          child: Image.asset(
                            'assets/figma/map-pin.png',
                            width: 20,
                            height: 24,
                            cacheWidth: 60,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Semantics(
                            container: true,
                            excludeSemantics: widget.previewMode,
                            label: widget.previewMode
                                ? 'Design preview sample location. 200 Market St, San Francisco. GPS accuracy 5 meters.'
                                : null,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  widget.previewMode
                                      ? '200 Market St, San Francisco'
                                      : 'GPS context',
                                  style: const TextStyle(
                                    fontSize: 20,
                                    height: 1.2,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  widget.previewMode
                                      ? 'GPS accuracy ±5m'
                                      : 'In development',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    height: 22 / 18,
                                    color: Color(0xFFBDBDBD),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Wrap(
                alignment: WrapAlignment.spaceBetween,
                spacing: 16,
                runSpacing: 8,
                children: [
                  const Text(
                    'Recent detections',
                    style: TextStyle(
                      fontSize: 18,
                      height: 22 / 18,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${_entries.length} events',
                        style: const TextStyle(
                          fontSize: 18,
                          height: 22 / 18,
                          color: Color(0xFFBDBDBD),
                        ),
                      ),
                      if (widget.previewMode && !expandedText) ...[
                        const SizedBox(width: 8),
                        Semantics(
                          label:
                              'Design preview. Sample data, not live GPS or detections.',
                          excludeSemantics: true,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              border: Border.all(color: pathYellow),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Padding(
                              padding: EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              child: Text(
                                'PREVIEW',
                                style: TextStyle(
                                  fontSize: 12,
                                  height: 1.2,
                                  fontWeight: FontWeight.w700,
                                  color: pathYellow,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),
              for (var i = 0; i < cards.length; i++) ...[
                if (i > 0) const SizedBox(height: 16),
                cards[i],
              ],
              const SizedBox(height: 16),
              LayoutBuilder(
                builder: (context, constraints) {
                  final clear = _LogAction(
                    label: 'Clear log',
                    onPressed: _clear,
                  );
                  final cancel = _LogAction(
                    label: 'Cancel alert',
                    onPressed: () =>
                        showPathDevelopment(context, 'Cancel alert'),
                  );
                  if (MediaQuery.textScalerOf(context).scale(18) > 27) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [clear, const SizedBox(height: 16), cancel],
                    );
                  }
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: clear),
                      const SizedBox(width: 16),
                      Expanded(child: cancel),
                    ],
                  );
                },
              ),
              const SizedBox(height: 16),
              Text(
                widget.previewMode
                    ? 'Shake phone to clear log or cancel alert.'
                    : 'Shake controls \u00b7 In development',
                style: const TextStyle(
                  fontSize: 18,
                  height: 1.3,
                  color: Color(0xFFBDBDBD),
                ),
              ),
            ],
          );
        },
      ),
    ),
  );
}

final _panelDecoration = BoxDecoration(
  color: pathSurface,
  borderRadius: BorderRadius.circular(12),
  border: Border.all(color: const Color(0xFF333333), width: 2),
);

// Exact example content from THESIS Figma node 2:1734. Never used as live data.
const _figmaEntries = [
  HazardLogEntry(
    object: 'Chair',
    direction: 'Center',
    time: '10:42:08',
    severity: HazardSeverity.danger,
    distanceMeters: 1.2,
  ),
  HazardLogEntry(
    object: 'Pedestrian',
    direction: 'Left',
    time: '10:41:56',
    severity: HazardSeverity.caution,
    distanceMeters: 2.4,
  ),
  HazardLogEntry(
    object: 'Vehicle',
    direction: 'Right',
    time: '10:41:32',
    severity: HazardSeverity.safe,
    distanceMeters: 4.8,
  ),
];

class _LogAction extends StatelessWidget {
  const _LogAction({required this.label, required this.onPressed});
  final String label;
  final VoidCallback onPressed;
  @override
  Widget build(BuildContext context) => OutlinedButton(
    onPressed: onPressed,
    style: OutlinedButton.styleFrom(
      foregroundColor: Colors.white,
      side: const BorderSide(color: Color(0xFFB3B3B3), width: 2),
      minimumSize: const Size.fromHeight(64),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
    child: Text(
      label,
      textAlign: TextAlign.center,
      style: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 18,
        height: 22 / 18,
        fontWeight: FontWeight.w700,
        color: Colors.white,
      ),
    ),
  );
}

class _HazardCard extends StatelessWidget {
  const _HazardCard({
    super.key,
    required this.entry,
    this.preview = false,
    this.compact = false,
    this.sampleData = false,
  });
  final HazardLogEntry entry;
  final bool preview, compact, sampleData;

  @override
  Widget build(BuildContext context) {
    final asset = switch (entry.severity) {
      HazardSeverity.danger => 'triangle-alert',
      HazardSeverity.caution => 'caution',
      HazardSeverity.safe => 'safe',
    };
    final detail = preview
        ? 'Distance / direction \u2014'
        : '${entry.distanceMeters == null ? '' : '${entry.distanceMeters!.toStringAsFixed(1)}m \u00b7 '}${entry.direction}';
    return Semantics(
      container: true,
      excludeSemantics: true,
      label: preview
          ? '${entry.severity.name} card layout placeholder. In development. Distance and direction unavailable.'
          : '${sampleData ? 'Design preview sample. ' : ''}${entry.severity.name}. ${entry.object}. $detail. ${entry.time}',
      child: ConstrainedBox(
        constraints: BoxConstraints(minHeight: compact ? 112 : 124),
        child: DecoratedBox(
          decoration: _panelDecoration,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 36,
                  height: 36,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: Colors.black,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Image.asset(
                        'assets/figma/$asset.png',
                        width: 28,
                        height: 28,
                        cacheWidth: 84,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SizedBox(
                        width: double.infinity,
                        child: Wrap(
                          alignment: WrapAlignment.spaceBetween,
                          spacing: 16,
                          runSpacing: 8,
                          children: [
                            Text(
                              entry.severity.name.toUpperCase(),
                              style: const TextStyle(
                                fontSize: 14,
                                height: 17 / 14,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              entry.time,
                              style: const TextStyle(
                                fontSize: 14,
                                height: 17 / 14,
                                color: Color(0xFFBDBDBD),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        entry.object,
                        style: const TextStyle(
                          fontSize: 24,
                          height: 29 / 24,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        detail,
                        style: TextStyle(
                          fontSize: 20,
                          height: 1.2,
                          color: preview
                              ? const Color(0xFFBDBDBD)
                              : Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class RecordedHazardLog extends StatefulWidget {
  const RecordedHazardLog({super.key, required this.history});
  final HazardHistory history;
  @override
  State<RecordedHazardLog> createState() => _RecordedHazardLogState();
}

class _RecordedHazardLogState extends State<RecordedHazardLog> {
  late Future<List<HazardEvent>> rows = widget.history.read();
  bool busy = false;
  Future<void> _export(List<HazardEvent> events) async {
    if (busy || events.isEmpty) return;
    setState(() => busy = true);
    try {
      final stamp = DateTime.now().toUtc().toIso8601String().replaceAll(
        ':',
        '-',
      );
      final saved = await const MethodChannel('path/hazard_export')
          .invokeMethod<bool>('saveCsv', {
            'name': 'PATH-hazard-log-$stamp.csv',
            'csv': hazardHistoryCsv(events),
          });
      if (mounted && saved == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Exported ${events.length} alerts to CSV.')),
        );
      }
    } on MissingPluginException {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Update the PATH Android build to enable CSV export.',
            ),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not export CSV. Try another destination.'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _edit({List<String>? restore}) async {
    if (busy) return;
    setState(() => busy = true);
    try {
      if (restore != null) {
        await widget.history.restore(restore);
      } else {
        final previous = await widget.history.clear();
        if (mounted) {
          ScaffoldMessenger.of(context).clearSnackBars();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('Log cleared'),
              action: SnackBarAction(
                label: 'Undo',
                onPressed: () {
                  if (mounted) _edit(restore: previous);
                },
              ),
            ),
          );
        }
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not update saved alerts.')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          busy = false;
          rows = widget.history.read();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: PathPageHeader(title: 'Hazard Log'),
          ),
          Expanded(
            child: FutureBuilder<List<HazardEvent>>(
              future: rows,
              builder: (context, snapshot) {
                if (snapshot.hasError) {
                  return Center(
                    child: TextButton(
                      onPressed: () =>
                          setState(() => rows = widget.history.read()),
                      child: const Text('Could not read alerts. Retry'),
                    ),
                  );
                }
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }
                final events = snapshot.data!;
                if (events.isEmpty) {
                  return const Center(child: Text('No saved alerts yet.'));
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: events.length + 1,
                  itemBuilder: (context, i) {
                    if (i == 0) {
                      return Wrap(
                        alignment: WrapAlignment.spaceBetween,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text('${events.length} saved alerts'),
                          TextButton.icon(
                            onPressed: busy ? null : () => _export(events),
                            icon: const Icon(Icons.file_download_outlined),
                            label: const Text('Export CSV'),
                          ),
                          TextButton(
                            onPressed: busy ? null : () => _edit(),
                            child: const Text('Clear log'),
                          ),
                        ],
                      );
                    }
                    final event = events[i - 1],
                        at = events[i - 1].at.toLocal();
                    final locale = MaterialLocalizations.of(context);
                    final stamp =
                        '${locale.formatMediumDate(at)}, ${at.year}  ${at.hour.toString().padLeft(2, '0')}:${at.minute.toString().padLeft(2, '0')}:${at.second.toString().padLeft(2, '0')}';
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${event.mode} - ${event.severity}',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            Text('${event.object}, ${event.direction}'),
                            Text(stamp),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    ),
  );
}

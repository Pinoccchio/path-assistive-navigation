import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class HazardEvent {
  const HazardEvent(
    this.at,
    this.mode,
    this.severity,
    this.object,
    this.direction,
  );
  final DateTime at;
  final String mode, severity, object, direction;
  String encode() => jsonEncode([
    at.toUtc().toIso8601String(),
    mode,
    severity,
    object,
    direction,
  ]);
  factory HazardEvent.decode(String value) {
    final row = List<String>.from(jsonDecode(value) as List);
    return HazardEvent(DateTime.parse(row[0]), row[1], row[2], row[3], row[4]);
  }
}

String hazardHistoryCsv(List<HazardEvent> events) {
  String field(String value) => '"${value.replaceAll('"', '""')}"';
  final lines = [
    'timestamp_utc,mode,severity,object,direction',
    for (final e in events)
      [
        e.at.toUtc().toIso8601String(),
        e.mode,
        e.severity,
        e.object,
        e.direction,
      ].map(field).join(','),
  ];
  return '${lines.join('\r\n')}\r\n';
}

/// Serialize reads and writes so opening the log immediately after an alert
/// includes that event, even while the platform write is pending.
class HazardHistory {
  static const _key = 'path.alertHistory.v1';
  Future<void> _pending = Future.value();
  Future<T> _run<T>(Future<T> Function(SharedPreferences) operation) {
    final result = _pending.then(
      (_) async => operation(await SharedPreferences.getInstance()),
    );
    _pending = result.then<void>((_) {}, onError: (Object _, StackTrace __) {});
    return result;
  }

  Future<List<HazardEvent>> read() => _run(
    (prefs) async =>
        (prefs.getStringList(_key) ?? []).map(HazardEvent.decode).toList(),
  );
  Future<void> _write(SharedPreferences prefs, List<String> values) async {
    if (!await prefs.setStringList(_key, values)) {
      throw StateError('History write failed');
    }
  }

  Future<void> add(HazardEvent event) => _run((prefs) async {
    await _write(prefs, [event.encode(), ...?prefs.getStringList(_key)]);
  });
  Future<List<String>> clear() => _run((prefs) async {
    final previous = prefs.getStringList(_key) ?? [];
    await _write(prefs, []);
    return previous;
  });
  Future<void> restore(List<String> previous) => _run((prefs) async {
    await _write(prefs, [...?prefs.getStringList(_key), ...previous]);
  });
}

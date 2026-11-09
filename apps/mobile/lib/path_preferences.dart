import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum AlertDelivery { voiceAndHaptic, voiceOnly, hapticOnly }

enum DirectionFormat { clockHand, threeZone }

/// Saved UI preferences. Alert output is not enabled by these selections yet.
class PathPreferences extends ChangeNotifier {
  PathPreferences({Future<SharedPreferences> Function()? loadStorage})
    : _loadStorage = loadStorage ?? SharedPreferences.getInstance;

  final Future<SharedPreferences> Function() _loadStorage;
  static const storageKey = 'path.accessibility.v1';
  AlertDelivery delivery = AlertDelivery.voiceAndHaptic;
  DirectionFormat direction = DirectionFormat.threeZone;
  double speechRate = 1.5;
  double cooldown = 1;
  bool stairs = true;
  bool vehicles = true;
  bool pedestrians = true;
  bool ready = false;
  String? error;
  bool _disposed = false;
  SharedPreferences? _storage;
  Future<void> _writes = Future<void>.value();

  Future<void> load() async {
    try {
      _storage = await _loadStorage();
      final raw = _storage!.getString(storageKey);
      if (raw != null) {
        final data = jsonDecode(raw) as Map<String, dynamic>;
        delivery = AlertDelivery.values.firstWhere(
          (value) => value.name == data['delivery'],
          orElse: () => delivery,
        );
        direction = DirectionFormat.values.firstWhere(
          (value) => value.name == data['direction'],
          orElse: () => direction,
        );
        speechRate = ((data['speechRate'] as num?)?.toDouble() ?? 1.5).clamp(
          1,
          2,
        );
        cooldown = ((data['cooldown'] as num?)?.toDouble() ?? 1).clamp(.5, 3);
        stairs = data['stairs'] is bool ? data['stairs'] as bool : true;
        vehicles = data['vehicles'] is bool ? data['vehicles'] as bool : true;
        pedestrians = data['pedestrians'] is bool
            ? data['pedestrians'] as bool
            : true;
      }
      error = null;
      ready = true;
    } catch (_) {
      error = 'Saved settings are unavailable. Changes apply to this session.';
    }
    ready = true;
    _notify();
  }

  void update({
    AlertDelivery? delivery,
    DirectionFormat? direction,
    double? speechRate,
    double? cooldown,
    bool? stairs,
    bool? vehicles,
    bool? pedestrians,
  }) {
    if (!ready) return;
    this.delivery = delivery ?? this.delivery;
    this.direction = direction ?? this.direction;
    this.speechRate = speechRate ?? this.speechRate;
    this.cooldown = cooldown ?? this.cooldown;
    this.stairs = stairs ?? this.stairs;
    this.vehicles = vehicles ?? this.vehicles;
    this.pedestrians = pedestrians ?? this.pedestrians;
    _notify();
    save();
  }

  Future<void> save() {
    final snapshot = jsonEncode({
      'delivery': delivery.name,
      'direction': direction.name,
      'speechRate': speechRate,
      'cooldown': cooldown,
      'stairs': stairs,
      'vehicles': vehicles,
      'pedestrians': pedestrians,
    });
    _writes = _writes.then((_) async {
      try {
        _storage ??= await _loadStorage();
        if (!await _storage!.setString(storageKey, snapshot)) {
          throw StateError('Settings write failed');
        }
        error = null;
      } catch (_) {
        error = 'Settings could not be saved. Changes apply to this session.';
      }
      _notify();
    });
    return _writes;
  }

  Future<void> reset() async {
    try {
      delivery = AlertDelivery.voiceAndHaptic;
      direction = DirectionFormat.threeZone;
      speechRate = 1.5;
      cooldown = 1;
      stairs = vehicles = pedestrians = true;
      ready = true;
      _notify();
      await save();
    } catch (_) {
      error = 'Could not reset settings.';
      _notify();
    }
  }

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

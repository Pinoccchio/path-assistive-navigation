import 'package:flutter/foundation.dart';
import 'detector.dart';
import 'feedback_clock.dart';
import 'path_preferences.dart';
import 'scene_summary.dart';
import 'scene_tracker.dart';

abstract interface class HapticOutput {
  Future<bool> prepare();
  Future<void> pulse();
  Future<void> cancel();
}

/// One neutral detection-update pulse. No direction or severity is encoded.
/// Consumes the speech pipeline's stable scene, independently of TTS or mute.
class DetectionHaptics extends ChangeNotifier {
  DetectionHaptics({
    required HapticOutput output,
    required this.preferences,
    DateTime Function()? now,
  }) : _output = output,
       _now = now ?? createFeedbackClock() {
    _configuration = _values;
    preferences.addListener(_preferencesChanged);
  }
  final HapticOutput _output;
  final PathPreferences preferences;
  final DateTime Function() _now;
  bool active = false, ready = false;
  bool _disposed = false, _busy = false, _checking = false;
  int _generation = 0, _session = 0;
  String? error;
  DateTime? _lastCue, _lastObservation;
  Map<SceneKey, int> _announced = {};
  Object? _configuration;
  Object get _values => (
    preferences.delivery,
    preferences.hapticsEnabled,
    preferences.cooldown,
    preferences.stairs,
    preferences.vehicles,
    preferences.pedestrians,
  );
  bool get enabled =>
      preferences.ready &&
      preferences.hapticsEnabled &&
      preferences.delivery != AlertDelivery.voiceOnly;
  bool get canToggle =>
      preferences.ready && preferences.delivery != AlertDelivery.voiceOnly;
  String get status {
    if (preferences.delivery == AlertDelivery.voiceOnly) {
      return 'Haptics off in Voice Only mode';
    }
    if (!preferences.hapticsEnabled) return 'Haptics off';
    if (error != null) return error!;
    if (!active) return 'Haptics enabled for the next session';
    return ready
        ? 'Haptics on for detection updates'
        : 'Checking vibration support';
  }

  Future<void> start() async {
    ++_generation;
    final session = ++_session;
    active = true;
    ready = false;
    error = null;
    _busy = false;
    _checking = false;
    _announced = {};
    _lastCue = null;
    _lastObservation = null;
    _notify();
    if (enabled) await _prepare(session);
  }

  Future<void> _prepare(int session) async {
    if (_checking) return;
    _checking = true;
    try {
      final supported = await _output.prepare().timeout(
        const Duration(seconds: 5),
      );
      if (_disposed || !active || session != _session) return;
      ready = supported;
      error = supported ? null : 'Haptics unavailable on this device';
    } catch (_) {
      if (_disposed || !active || session != _session) return;
      error = 'Haptics unavailable. Restart the session to retry.';
      ready = false;
    } finally {
      if (session == _session) {
        _checking = false;
        _notify();
      }
    }
  }

  bool _enabledClass(Detection d) => switch (d.label) {
    'stairs' => preferences.stairs,
    'person' => preferences.pedestrians,
    'car' || 'bicycle' || 'motorcycle' => preferences.vehicles,
    _ => true,
  };
  Future<void> consider(List<Detection> stable, DateTime observedAt) async {
    if (_disposed || !active) return;
    final now = _now();
    if (observedAt.isAfter(now) ||
        (_lastObservation != null && observedAt.isBefore(_lastObservation!))) {
      return;
    }
    if (now.difference(observedAt) > const Duration(seconds: 2)) {
      _announced = {};
      return;
    }
    if (_lastObservation != null &&
        observedAt.difference(_lastObservation!) > const Duration(seconds: 2)) {
      _announced = {};
    }
    _lastObservation = observedAt;
    final groups = groupScene(
      stable.where((d) => validSceneDetection(d) && _enabledClass(d)),
    );
    final present = {for (final group in groups) group.key: group.count};
    _announced.removeWhere((key, _) => !present.containsKey(key));
    if (!enabled || !ready || _busy || groups.isEmpty) return;
    if (_lastCue != null &&
        now.difference(_lastCue!).inMilliseconds <
            preferences.cooldown * 1000) {
      return;
    }
    if (!groups.any((g) => _announced[g.key] != g.count)) return;
    final generation = _generation;
    _busy = true;
    _lastCue = now;
    try {
      // Adapter sends one immediate native request; cancel is ordered after it.
      await _output.pulse();
      if (!_disposed && active && generation == _generation && enabled) {
        _announced = present;
      }
    } catch (_) {
      if (!_disposed && active && generation == _generation) {
        error = 'Haptic playback failed. Restart the session to retry.';
        ready = false;
        _notify();
      }
    } finally {
      if (generation == _generation) _busy = false;
    }
  }

  Future<void> interruptForPriority() => _cancel();

  Future<void> toggle() async {
    if (!canToggle) return;
    preferences.update(hapticsEnabled: !preferences.hapticsEnabled);
  }

  void _preferencesChanged() {
    final values = _values;
    if (values != _configuration) {
      _configuration = values;
      _announced = {};
      if (!enabled) _cancel();
    }
    if (active && enabled && !ready && !_checking && error == null) {
      _prepare(_session);
    }
    _notify();
  }

  Future<void> _cancel() async {
    ++_generation;
    _busy = false;
    _announced = {};
    _lastCue = null;
    try {
      await _output.cancel();
    } catch (_) {
      if (!_disposed) error = 'Could not cancel vibration';
    }
    _notify();
  }

  Future<void> stop() async {
    ++_session;
    active = false;
    ready = false;
    _checking = false;
    _lastObservation = null;
    await _cancel();
  }

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    active = false;
    ++_generation;
    ++_session;
    preferences.removeListener(_preferencesChanged);
    _output.cancel().catchError((Object _) {});
    super.dispose();
  }
}

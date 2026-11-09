import 'package:flutter/foundation.dart';
import 'detector.dart';
import 'path_preferences.dart';
import 'scene_summary.dart';
import 'scene_tracker.dart';
import 'feedback_clock.dart';

abstract interface class SpeechOutput {
  Future<void> prepare();
  Future<void> setRate(double multiplier);
  Future<void> speak(String message);
  Future<void> stop();
}

/// Short changed groups automatically; paged details on explicit request.
/// Confidence ordering is not hazard priority. No backlog of old utterances.
class DetectionSpeech extends ChangeNotifier {
  DetectionSpeech({
    required SpeechOutput output,
    required this.preferences,
    DateTime Function()? now,
    TemporalSceneTracker? tracker,
    this.onStableScene,
  }) : _output = output,
       _now = now ?? createFeedbackClock(),
       _tracker = tracker ?? TemporalSceneTracker() {
    _lastPreferences = _preferenceValues;
    preferences.addListener(_preferencesChanged);
  }
  final SpeechOutput _output;
  final PathPreferences preferences;
  final DateTime Function() _now;
  final TemporalSceneTracker _tracker;
  final void Function(List<Detection>, DateTime)? onStableScene;
  static const freshness = Duration(seconds: 2);
  bool active = false, muted = false, ready = false;
  bool _busy = false, _disposed = false;
  int _generation = 0, _session = 0;
  String? error, lastMessage;
  DateTime? _lastFinished, _frameTime;
  List<Detection> _stable = const [];
  bool _hasUnconfirmed = false;
  Map<SceneKey, int> _announced = {};
  String? _descriptionSignature;
  int _descriptionOffset = 0, _descriptionTotal = 0;
  Object? _lastPreferences;
  Object get _preferenceValues => (
    preferences.delivery,
    preferences.direction,
    preferences.speechRate,
    preferences.cooldown,
    preferences.stairs,
    preferences.vehicles,
    preferences.pedestrians,
  );
  bool get voiceEnabled => preferences.delivery != AlertDelivery.hapticOnly;
  bool get _available =>
      !_disposed &&
      active &&
      ready &&
      !muted &&
      voiceEnabled &&
      !_busy &&
      preferences.ready;
  bool get canRepeat => _available && lastMessage != null;
  bool get canDescribe => _available;
  bool get hasMoreDetails =>
      _descriptionOffset > 0 && _descriptionOffset < _descriptionTotal;
  bool get canReadMore => _available && hasMoreDetails;
  bool get _fresh =>
      _frameTime != null && _now().difference(_frameTime!) <= freshness;

  /// Callback time before inference, using the same monotonic clock as speech.
  /// This is not the sensor exposure timestamp.
  DateTime markFrameReceived() => _now();
  List<SceneGroup> get _groups => groupScene(_stable.where(_enabled));
  String get _signature => sceneSignature(_groups, preferences.direction);

  Future<void> start() async {
    ++_generation;
    final session = ++_session;
    active = true;
    ready = false;
    _busy = false;
    error = null;
    _clearScene();
    _notify();
    if (!voiceEnabled) {
      _notify();
      return;
    }
    try {
      await _output.prepare().timeout(const Duration(seconds: 10));
      if (_disposed || !active || session != _session) return;
      ready = true;
    } catch (_) {
      if (_disposed || !active || session != _session) return;
      error =
          'Voice unavailable. Install an offline English voice in Android text-to-speech settings, then restart the session.';
    }
    _notify();
  }

  bool _valid(int generation) =>
      !_disposed && active && generation == _generation;
  bool _enabled(Detection d) => switch (d.label) {
    'stairs' => preferences.stairs,
    'person' => preferences.pedestrians,
    'car' || 'bicycle' || 'motorcycle' => preferences.vehicles,
    _ => true,
  };

  Future<void> consider(
    List<Detection> detections, {
    DateTime? observedAt,
  }) async {
    if (_disposed || !active) return;
    // Always refresh perception while speaking, muted or cooling down.
    final previous = _signature;
    final now = _now();
    final received = observedAt ?? now;
    if ((_frameTime != null && received.isBefore(_frameTime!)) ||
        received.isAfter(now)) {
      return;
    }
    _frameTime = received;
    if (now.difference(received) > freshness) {
      _tracker.reset();
      _stable = const [];
      _announced = {};
      _hasUnconfirmed = false;
      _notify();
      return;
    }
    _stable = _tracker.update(detections, received);
    _hasUnconfirmed =
        detections.any((d) => validSceneDetection(d) && _enabled(d)) &&
        !_stable.any(_enabled);
    final groups = _groups;
    final signature = sceneSignature(groups, preferences.direction);
    onStableScene?.call(List.unmodifiable(_stable), received);
    if (previous != signature) _notify();
    if (!_available) return;
    final present = {for (final g in groups) g.key: g.count};
    _announced.removeWhere((key, _) => !present.containsKey(key));
    if (groups.isEmpty) return; // Never announce a clear path.
    if (_lastFinished != null &&
        now.difference(_lastFinished!).inMilliseconds <
            preferences.cooldown * 1000) {
      return;
    }
    final changed = groups
        .where((g) => _announced[g.key] != g.count)
        .take(2)
        .toList();
    if (changed.isEmpty) return;
    final message = changed
        .map((g) => g.phrase(preferences.direction))
        .join(' ');
    // Handle the whole snapshot rather than queueing omitted groups.
    await _say(message, scene: signature, onIssued: () => _announced = present);
  }

  Future<void> describeScene() async {
    if (!_available) return;
    _descriptionOffset = 0;
    _descriptionSignature = null;
    _descriptionTotal = 0;
    await _describePage();
  }

  Future<void> moreDetails() async {
    if (canReadMore) await _describePage();
  }

  Future<void> _describePage() async {
    if (!_fresh) {
      _descriptionOffset = 0;
      _descriptionTotal = 0;
      await _say('Camera information is unavailable. Wait for a fresh frame.');
      return;
    }
    final groups = _groups;
    final signature = sceneSignature(groups, preferences.direction);
    var prefix = '';
    if (_descriptionSignature != null && _descriptionSignature != signature) {
      prefix = 'Scene changed. ';
      _descriptionOffset = 0;
    }
    if (groups.isEmpty) {
      _descriptionOffset = 0;
      _descriptionTotal = 0;
      await _say(
        _hasUnconfirmed
            ? 'Confirming detections. Please try again.'
            : 'No stable objects detected. Path condition is unknown.',
        scene: signature,
      );
      return;
    }
    // Stable paging order: confidence fluctuations cannot skip a group.
    groups.sort(
      (a, b) => '${a.key.direction}:${a.key.label}'.compareTo(
        '${b.key.direction}:${b.key.label}',
      ),
    );
    final page = groups.skip(_descriptionOffset).take(3).toList();
    final next = _descriptionOffset + page.length;
    final remaining = groups.skip(next).fold(0, (count, g) => count + g.count);
    final message =
        '$prefix${page.map((g) => g.phrase(preferences.direction)).join(' ')}'
        '${remaining > 0 ? ' $remaining more ${remaining == 1 ? 'object' : 'objects'}. More details available.' : ''}';
    await _say(
      message,
      scene: signature,
      onIssued: () {
        _descriptionOffset = next;
        _descriptionTotal = groups.length;
        _descriptionSignature = signature;
        _announced = {for (final g in groups) g.key: g.count};
      },
    );
  }

  Future<void> repeat() async {
    if (canRepeat) {
      await _say('Last announcement: $lastMessage', remember: false);
    }
  }

  Future<void> _say(
    String message, {
    String? scene,
    VoidCallback? onIssued,
    bool remember = true,
  }) async {
    final generation = _generation;
    _busy = true;
    _notify();
    try {
      await _output.setRate(preferences.speechRate);
      if (!_valid(generation) || muted || !voiceEnabled) return;
      if (scene != null && (!_fresh || scene != _signature)) return;
      if (remember) lastMessage = message;
      error = null;
      onIssued?.call();
      _notify();
      await _output.speak(message);
    } catch (_) {
      if (_valid(generation)) {
        error = 'Voice playback failed. Restart the session to retry.';
        ready = false;
      }
    } finally {
      if (_valid(generation)) {
        _lastFinished = _now();
        _busy = false;
        _notify();
      }
    }
  }

  Future<void> toggleMute() async {
    muted = !muted;
    _announced = {};
    _notify();
    if (muted) await _cancelPlayback();
  }

  void _preferencesChanged() {
    // Storage completion/error notifications do not change spoken content.
    final values = _preferenceValues;
    if (values != _lastPreferences) {
      _lastPreferences = values;
      _announced = {};
      _descriptionOffset = 0;
      _descriptionTotal = 0;
      if (!voiceEnabled) _cancelPlayback();
    }
    _notify();
  }

  Future<void> _cancelPlayback() async {
    ++_generation;
    _busy = false;
    try {
      await _output.stop();
    } catch (_) {
      if (!_disposed) error = 'Could not stop voice playback.';
    }
    _notify();
  }

  void _clearScene() {
    _tracker.reset();
    _stable = const [];
    _frameTime = null;
    _announced = {};
    lastMessage = null;
    _lastFinished = null;
    _descriptionSignature = null;
    _descriptionOffset = 0;
    _descriptionTotal = 0;
    _hasUnconfirmed = false;
  }

  Future<void> stop() async {
    ++_session;
    active = false;
    ready = false;
    _clearScene();
    await _cancelPlayback();
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
    _clearScene();
    preferences.removeListener(_preferencesChanged);
    _output.stop().catchError((Object _) {});
    super.dispose();
  }
}

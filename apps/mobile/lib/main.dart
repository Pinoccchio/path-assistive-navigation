import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'detector.dart';
import 'depth_preview.dart';
import 'danger_demo.dart';
import 'zone_preview.dart';
import 'calibration_screen.dart';
import 'detection_overlay.dart';
import 'session_view.dart';
import 'path_preferences.dart';
import 'settings_screen.dart';
import 'hazard_log_screen.dart';
import 'hazard_history.dart';
import 'detection_speech.dart';
import 'flutter_speech_output.dart';
import 'detection_haptics.dart';
import 'android_haptic_output.dart';
import 'feedback_clock.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Colors.transparent,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  runApp(const ResearchApp());
}

class ResearchApp extends StatelessWidget {
  const ResearchApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Navigation Research',
    debugShowCheckedModeBanner: false,
    theme: buildPathTheme(),
    home: const SessionScreen(),
  );
}

class SessionScreen extends StatefulWidget {
  const SessionScreen({super.key});

  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen>
    with WidgetsBindingObserver {
  CameraController? _camera;
  Detector? _detector;
  List<Detection> _detections = const [];
  int? _elapsedMs;
  DepthMap? _depth;
  Float32List? _frameRgb;
  DateTime? _frameUtc;
  int? _totalMs;
  int _processedFrames = 0;
  Future<void>? _pendingFrame;
  DateTime? _lastFrame;
  bool _stopping = false;
  bool _starting = false;
  String? _error;
  final _preferences = PathPreferences();
  late final DetectionSpeech _speech;
  late final DetectionHaptics _haptics;
  late final PriorityAlertOutput _priority;
  Map<String, List<ZoneReference>> _references = {};
  String? _researchStatus;
  bool _priorityActive = false;
  final _history = HazardHistory();
  AlertObject? _loggedAlert;
  int _feedbackEpoch = 0;
  int _sessionGeneration = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    final clock = createFeedbackClock();
    _priority = PriorityAlertOutput(
      FlutterSpeechOutput(),
      AndroidHapticOutput(),
    );
    _haptics = DetectionHaptics(
      output: _priority.haptics,
      preferences: _preferences,
      now: clock,
    )..addListener(_speechChanged);
    _speech = DetectionSpeech(
      output: _priority.voice,
      preferences: _preferences,
      now: clock,
      onStableScene: _haptics.consider,
    )..addListener(_speechChanged);
    _preferences.load();
  }

  void _speechChanged() {
    if (mounted) setState(() {});
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed && (_camera != null || _starting)) {
      _stopSession();
    }
  }

  Future<void> _startSession() async {
    if (_starting || _stopping || _camera != null) return;
    final generation = ++_sessionGeneration;
    setState(() {
      _starting = true;
      _error = null;
      _processedFrames = 0;
      _lastFrame = null;
    });
    CameraController? next;
    Detector? detector;
    try {
      _references = !_preferences.liveRulePreview
          ? await readZoneReferences().catchError(
              (Object _) => <String, List<ZoneReference>>{},
            )
          : {};
      _researchStatus = null;
      detector = await Detector.load();
      final cameras = await availableCameras();
      final rear = cameras.where(
        (camera) => camera.lensDirection == CameraLensDirection.back,
      );
      if (rear.isEmpty) {
        throw CameraException('NoRearCamera', 'No rear camera found.');
      }
      next = CameraController(
        rear.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );
      await next.initialize();
      if (!mounted || generation != _sessionGeneration) {
        await next.dispose();
        await detector.close();
        if (mounted) setState(() => _starting = false);
        return;
      }
      _detector = detector;
      await next.startImageStream((frame) {
        if (_stopping ||
            generation != _sessionGeneration ||
            _pendingFrame != null) {
          return;
        }
        final now = DateTime.now();
        if (_lastFrame != null &&
            now.difference(_lastFrame!).inMilliseconds < 500) {
          return;
        }
        _lastFrame = now;
        final pending = _processFrame(
          frame,
          next!.description.sensorOrientation,
          _speech.markFrameReceived(),
        );
        _pendingFrame = pending;
        pending.whenComplete(() => _pendingFrame = null);
      });
      if (!mounted || generation != _sessionGeneration) {
        await next.stopImageStream();
        await _pendingFrame;
        await next.dispose();
        await detector.close();
        _detector = null;
        if (mounted) setState(() => _starting = false);
        return;
      }
      setState(() {
        _camera = next;
        _starting = false;
      });
      _speech.start();
      _haptics.start();
    } on CameraException catch (error) {
      await next?.dispose();
      await detector?.close();
      _detector = null;
      if (mounted && generation == _sessionGeneration) {
        setState(() {
          _starting = false;
          _error = error.code == 'CameraAccessDenied'
              ? 'Camera permission denied. Allow access in Android settings.'
              : 'Camera unavailable: ${error.description ?? error.code}';
        });
      }
    } catch (error) {
      await next?.dispose();
      await detector?.close();
      _detector = null;
      if (mounted && generation == _sessionGeneration) {
        setState(() {
          _starting = false;
          _error = 'Could not start detection: $error';
        });
      }
    } finally {
      if (mounted && _camera == null) setState(() => _starting = false);
    }
  }

  Future<void> _processFrame(
    CameraImage frame,
    int rotation,
    DateTime receivedAt,
  ) async {
    try {
      final frameUtc = DateTime.now().toUtc();
      final result = await _detector!.detect(frame, rotation);
      if (mounted && !_stopping && _camera != null) {
        setState(() {
          _detections = result.detections;
          _elapsedMs = result.elapsedMs;
          _depth = result.depth;
          _frameRgb = result.frameRgb;
          _frameUtc = frameUtc;
          _totalMs = result.totalMs;
          _processedFrames++;
        });
        _routeFeedback(result, receivedAt).catchError((Object error) {
          if (mounted && _camera != null && !_stopping) {
            setState(() => _researchStatus = 'Research feedback unavailable');
          }
        });
      }
    } catch (error) {
      if (mounted && !_stopping) {
        setState(() => _error = 'Detection paused: $error');
        Future<void>.delayed(Duration.zero, _stopSession);
      }
    }
  }

  Future<void> _routeFeedback(
    DetectionResult result,
    DateTime receivedAt,
  ) async {
    final epoch = ++_feedbackEpoch;
    final demo = _preferences.liveRulePreview;
    final active = _references.isNotEmpty || demo;
    final fresh =
        _speech.markFrameReceived().difference(receivedAt) <=
        DetectionSpeech.freshness;
    final eligible = result.detections.where(
      (d) => switch (d.label) {
        'person' => _preferences.pedestrians,
        'stairs' => _preferences.stairs,
        'car' || 'motorcycle' || 'bicycle' => _preferences.vehicles,
        _ => true,
      },
    );
    final demoAlerts = demo ? liveRuleCandidates(eligible) : <AlertObject>[];
    final scene = <SceneObjectDepth>[
      if (active && fresh && !demo)
        for (final d in eligible)
          (
            label: d.label,
            direction: d.direction,
            score: result.depth?.medianInverseDepth(d.box),
          ),
    ];
    final ranked = active ? rankScene(scene, _references) : <ScenePriority>[];
    final alerts = <AlertObject>[
      if (fresh) ...demoAlerts,
      for (final item in ranked)
        if (item.zone == ResearchZone.danger ||
            item.zone == ResearchZone.caution)
          (
            zone: item.zone!,
            label: scene[item.index].label,
            direction: scene[item.index].direction,
          ),
    ];
    if (alerts.isEmpty) {
      _loggedAlert = null;
      if (_priorityActive) {
        _priorityActive = false;
        await _priority.stop();
        if (!mounted || epoch != _feedbackEpoch) return;
      }
      _researchStatus = demo
          ? (demoAlerts.isEmpty
                ? 'No test alert'
                : 'Top alert: Test ${demoAlerts.first.zone.title} - ${demoAlerts.first.label}, ${demoAlerts.first.direction} (frame too old for feedback)')
          : active
          ? (!fresh
                ? 'Research zone: frame too old'
                : ranked.any((p) => p.zone == ResearchZone.farther)
                ? 'Research estimate: Farther'
                : 'Research zone: Unknown')
          : null;
      await _speech.consider(result.detections, observedAt: receivedAt);
      return;
    }
    if (!_priorityActive) {
      _priorityActive = true;
      await Future.wait([
        _speech.interruptForPriority(),
        _haptics.interruptForPriority(),
      ]);
      if (!mounted || epoch != _feedbackEpoch) return;
    }
    if (_speech.markFrameReceived().difference(receivedAt) >
        DetectionSpeech.freshness) {
      return;
    }
    final first = alerts.first;
    if (_loggedAlert != first) {
      _loggedAlert = first;
      _history
          .add(
            HazardEvent(
              DateTime.now().toUtc(),
              demo ? 'Test' : 'Live',
              first.zone.title,
              first.label,
              first.direction,
            ),
          )
          .catchError((Object _) {
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Could not save alert to Hazard Log.'),
                ),
              );
            }
          });
    }
    _researchStatus =
        'Top alert: ${demo ? 'Test' : 'Research estimate:'} ${first.zone.title} - ${first.label}, ${first.direction}';
    final voice = _speech.ready && _speech.voiceEnabled && !_speech.muted;
    final vibration = _haptics.ready && _haptics.enabled;
    if (voice || vibration) {
      await _priority.present(
        alerts,
        _preferences,
        (_) {
          if (mounted) setState(() {});
        },
        vibration: vibration,
        voiceEnabled: voice,
        rulePreview: demo,
      );
    }
  }

  Future<void> _changeOutput(Future<void> Function() change) async {
    ++_feedbackEpoch;
    if (_priorityActive) await _priority.stop();
    if (mounted) await change();
  }

  Future<void> _stopSession() async {
    ++_sessionGeneration;
    ++_feedbackEpoch;
    _priorityActive = false;
    _loggedAlert = null;
    _researchStatus = null;
    _priority.invalidate();
    final stoppedSpeech = Future.wait<void>([_speech.stop(), _haptics.stop()]);
    final camera = _camera;
    if (camera == null) {
      await stoppedSpeech;
      return;
    }
    _stopping = true;
    if (mounted) setState(() => _camera = null);
    if (camera.value.isStreamingImages) await camera.stopImageStream();
    await _pendingFrame;
    await camera.dispose();
    await _detector?.close();
    await stoppedSpeech;
    _detector = null;
    _stopping = false;
    if (mounted) {
      setState(() {
        _detections = const [];
        _elapsedMs = null;
        _depth = null;
        _frameRgb = null;
        _totalMs = null;
      });
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    ++_sessionGeneration;
    ++_feedbackEpoch;
    _priority.invalidate();
    _speech.removeListener(_speechChanged);
    _speech.dispose();
    _haptics.removeListener(_speechChanged);
    _haptics.dispose();
    final camera = _camera;
    final detector = _detector;
    if (camera != null) {
      // A running inference owns both interpreters until its future completes.
      () async {
        if (camera.value.isStreamingImages) await camera.stopImageStream();
        await _pendingFrame;
        await camera.dispose();
        await detector?.close();
      }();
    }
    _preferences.dispose();
    super.dispose();
  }

  Future<void> _openPage(Widget page) async {
    if (_starting || _stopping) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Wait for the camera to finish.')),
      );
      return;
    }
    await _stopSession();
    if (!mounted) return;
    await Navigator.of(
      context,
    ).push<void>(MaterialPageRoute(builder: (context) => page));
  }

  @override
  Widget build(BuildContext context) {
    final camera = _camera;
    return SessionView(
      phase: _starting
          ? SessionPhase.starting
          : _stopping
          ? SessionPhase.stopping
          : camera != null
          ? SessionPhase.live
          : SessionPhase.idle,
      onToggle: camera != null ? _stopSession : _startSession,
      preview: camera == null
          ? null
          : _CameraViewport(camera: camera, detections: _detections),
      researchPanel: camera != null && _depth != null
          ? DepthReadout(
              onCalibrate: () {
                final depth = _depth;
                if (depth == null || _frameUtc == null || _stopping) return;
                _openPage(
                  CalibrationScreen(
                    depth: depth,
                    rgb: _frameRgb,
                    detections: List.of(_detections),
                    frameUtc: _frameUtc!,
                    aspect:
                        camera.value.previewSize!.height /
                        camera.value.previewSize!.width,
                  ),
                );
              },
              map: _depth!,
              zoneStatus: _researchStatus,
              detectorMs: _elapsedMs!,
              combinedMs: _totalMs!,
              aspect:
                  camera.value.previewSize!.height /
                  camera.value.previewSize!.width,
            )
          : null,
      detections: _detections,
      elapsedMs: _elapsedMs,
      processedFrames: _processedFrames,
      error: _error,
      voiceStatus: _priorityActive
          ? _researchStatus
          : _speech.error ??
                (_haptics.enabled ? _haptics.error : null) ??
                (_speech.muted
                    ? (_haptics.enabled
                          ? 'Audio muted. ${_haptics.status}'
                          : 'Audio muted')
                    : !_speech.voiceEnabled
                    ? _haptics.status
                    : _speech.active && !_speech.ready
                    ? 'Preparing voice'
                    : (_speech.lastMessage == null
                              ? null
                              : 'Last spoken: ${_speech.lastMessage}') ??
                          (camera != null
                              ? 'Listening for detections'
                              : 'Voice ready for session')),
      audioMuted: _speech.muted,
      hapticsOn: _haptics.enabled,
      hapticStatus: _haptics.status,
      onToggleHaptics: _haptics.canToggle
          ? () => _changeOutput(_haptics.toggle)
          : null,
      onToggleAudio: () => _changeOutput(_speech.toggleMute),
      onRepeat: _speech.canRepeat ? _speech.repeat : null,
      onDescribeScene: !_priorityActive && _speech.canDescribe
          ? _speech.describeScene
          : null,
      onMoreDetails: _speech.canReadMore ? _speech.moreDetails : null,
      hasMoreDetails: _speech.hasMoreDetails,
      onOpenSettings: () =>
          _openPage(SettingsScreen(preferences: _preferences)),
      onDangerDemo: () => _openPage(
        DangerDemoScreen(preferences: _preferences, muted: _speech.muted),
      ),
      onOpenLog: () => _openPage(RecordedHazardLog(history: _history)),
    );
  }
}

class _CameraViewport extends StatelessWidget {
  const _CameraViewport({required this.camera, required this.detections});
  final CameraController camera;
  final List<Detection> detections;

  @override
  Widget build(BuildContext context) {
    final preview = camera.value.previewSize!;
    return ProportionalDetectionPreview(
      imageSize: Size(preview.height, preview.width),
      image: CameraPreview(camera),
      detections: detections,
    );
  }
}

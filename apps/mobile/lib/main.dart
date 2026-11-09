import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'detector.dart';
import 'detection_overlay.dart';
import 'session_view.dart';
import 'path_preferences.dart';
import 'settings_screen.dart';
import 'hazard_log_screen.dart';

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
  int _processedFrames = 0;
  Future<void>? _pendingFrame;
  DateTime? _lastFrame;
  bool _stopping = false;
  bool _starting = false;
  String? _error;
  final _preferences = PathPreferences();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _preferences.load();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed && _camera != null) {
      _stopSession();
    }
  }

  Future<void> _startSession() async {
    if (_starting || _stopping || _camera != null) return;
    setState(() {
      _starting = true;
      _error = null;
      _processedFrames = 0;
      _lastFrame = null;
    });
    CameraController? next;
    Detector? detector;
    try {
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
      if (!mounted) {
        await next.dispose();
        await detector.close();
        return;
      }
      _detector = detector;
      await next.startImageStream((frame) {
        if (_stopping || _pendingFrame != null) return;
        final now = DateTime.now();
        if (_lastFrame != null &&
            now.difference(_lastFrame!).inMilliseconds < 500) {
          return;
        }
        _lastFrame = now;
        final pending = _processFrame(
          frame,
          next!.description.sensorOrientation,
        );
        _pendingFrame = pending;
        pending.whenComplete(() => _pendingFrame = null);
      });
      setState(() {
        _camera = next;
        _starting = false;
      });
    } on CameraException catch (error) {
      await next?.dispose();
      await detector?.close();
      _detector = null;
      if (mounted) {
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
      if (mounted) {
        setState(() {
          _starting = false;
          _error = 'Could not start detection: $error';
        });
      }
    }
  }

  Future<void> _processFrame(CameraImage frame, int rotation) async {
    try {
      final result = await _detector!.detect(frame, rotation);
      if (mounted && !_stopping && _camera != null) {
        setState(() {
          _detections = result.detections;
          _elapsedMs = result.elapsedMs;
          _processedFrames++;
        });
      }
    } catch (error) {
      if (mounted && !_stopping) {
        setState(() => _error = 'Detection paused: $error');
        Future<void>.delayed(Duration.zero, _stopSession);
      }
    }
  }

  Future<void> _stopSession() async {
    final camera = _camera;
    if (camera == null) return;
    _stopping = true;
    if (mounted) setState(() => _camera = null);
    if (camera.value.isStreamingImages) await camera.stopImageStream();
    await _pendingFrame;
    await camera.dispose();
    await _detector?.close();
    _detector = null;
    _stopping = false;
    if (mounted) {
      setState(() {
        _detections = const [];
        _elapsedMs = null;
      });
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _camera?.dispose();
    _detector?.close();
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
      detections: _detections,
      elapsedMs: _elapsedMs,
      processedFrames: _processedFrames,
      error: _error,
      onOpenSettings: () =>
          _openPage(SettingsScreen(preferences: _preferences)),
      onOpenLog: () => _openPage(const HazardLogScreen(previewMode: true)),
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
    return SizedBox.expand(
      child: FittedBox(
        fit: BoxFit.contain,
        child: SizedBox(
          width: preview.height,
          height: preview.width,
          child: CameraPreview(
            camera,
            child: DetectionOverlay(detections: detections),
          ),
        ),
      ),
    );
  }
}

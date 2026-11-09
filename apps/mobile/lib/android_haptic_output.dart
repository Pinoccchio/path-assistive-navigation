import 'package:flutter/services.dart';
import 'detection_haptics.dart';

class AndroidHapticOutput implements HapticOutput {
  static const channel = MethodChannel('path/haptics');
  bool _used = false;
  @override
  Future<bool> prepare() async {
    _used = true;
    return await channel.invokeMethod<bool>('hasVibrator') ?? false;
  }

  @override
  Future<void> pulse() async {
    if (await channel.invokeMethod<bool>('pulse') != true) {
      throw StateError('Vibration unavailable');
    }
  }

  @override
  Future<void> cancel() async {
    if (_used) await channel.invokeMethod<void>('cancel');
  }
}

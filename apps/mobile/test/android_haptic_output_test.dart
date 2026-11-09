import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/android_haptic_output.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('path/haptics');
  final calls = <String>[];
  var supported = true;
  setUp(() {
    calls.clear();
    supported = true;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call.method);
          if (call.method == 'hasVibrator' || call.method == 'pulse') {
            return supported;
          }
          return null;
        });
  });
  tearDown(
    () => TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, null),
  );
  test(
    'native capability, pulse and cancel requests keep their order',
    () async {
      final output = AndroidHapticOutput();
      expect(await output.prepare(), isTrue);
      await output.pulse();
      await output.cancel();
      expect(calls, ['hasVibrator', 'pulse', 'cancel']);
    },
  );
  test('unsupported hardware is returned and rejected for playback', () async {
    supported = false;
    final output = AndroidHapticOutput();
    expect(await output.prepare(), isFalse);
    await expectLater(output.pulse(), throwsStateError);
  });
  test(
    'idle cancellation does not initialize or call an unused native channel',
    () async {
      await AndroidHapticOutput().cancel();
      expect(calls, isEmpty);
    },
  );
}

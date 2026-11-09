import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/flutter_speech_output.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('flutter_tts');
  final calls = <MethodCall>[];
  var local = true;
  setUp(() {
    calls.clear();
    local = true;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          if (call.method == 'getVoices') {
            return [
              {'name': 'Cloud', 'locale': 'en-US', 'network_required': '1'},
              if (local)
                {'name': 'Local', 'locale': 'en-US', 'network_required': '0'},
            ];
          }
          return 1;
        });
  });
  tearDown(
    () => TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, null),
  );

  test(
    'selects offline voice and maps UI speed to Android plugin range',
    () async {
      final output = FlutterSpeechOutput();
      await output.prepare();
      await output.setRate(1.5);
      await output.speak('chair, left.');
      await output.stop();
      expect(calls.firstWhere((x) => x.method == 'setVoice').arguments, {
        'name': 'Local',
        'locale': 'en-US',
      });
      expect(
        calls.firstWhere((x) => x.method == 'setSpeechRate').arguments,
        .75,
      );
      expect(calls.firstWhere((x) => x.method == 'setQueueMode').arguments, 0);
      expect(
        calls.firstWhere((x) => x.method == 'speak').arguments,
        'chair, left.',
      );
      expect(calls.last.method, 'stop');
    },
  );

  test('network-only voices do not silently enable cloud speech', () async {
    local = false;
    await expectLater(FlutterSpeechOutput().prepare(), throwsStateError);
    expect(calls.any((x) => x.method == 'speak'), isFalse);
  });
}

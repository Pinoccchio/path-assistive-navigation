import 'package:flutter_tts/flutter_tts.dart';

import 'detection_speech.dart';

class FlutterSpeechOutput implements SpeechOutput {
  FlutterTts? _engine;
  FlutterTts get _tts => _engine ??= FlutterTts();
  int _generation = 0;
  double _rateMultiplier = 1;

  @override
  Future<void> prepare() async {
    final voices = await _tts.getVoices as List<dynamic>;
    final localEnglish = voices.whereType<Map>().where((voice) {
      final network = voice['network_required'];
      return voice['locale'].toString().toLowerCase().startsWith('en') &&
          (network == false ||
              network == 'false' ||
              network == 0 ||
              network == '0');
    });
    if (localEnglish.isEmpty) throw StateError('No offline English voice');
    final voice = localEnglish.first;
    if (await _tts.setLanguage(voice['locale'].toString()) != 1 ||
        await _tts.setVoice({
              'name': voice['name'].toString(),
              'locale': voice['locale'].toString(),
            }) !=
            1) {
      throw StateError('Could not select offline voice');
    }
    await _tts.awaitSpeakCompletion(true);
    await _tts.setQueueMode(0);
  }

  @override
  Future<void> setRate(double multiplier) async {
    // Plugin range is 0..1; Android maps 0.5 to normal engine rate.
    if (await _tts.setSpeechRate((multiplier * .5).clamp(0.0, 1.0)) != 1) {
      throw StateError('Could not set speech rate');
    }
    _rateMultiplier = multiplier.clamp(1.0, 2.0);
  }

  @override
  Future<void> speak(String message) async {
    final generation = ++_generation;
    try {
      // Bounded watchdog scaled to short detail pages, not an alert-latency goal.
      final words = message.split(RegExp(r'\s+')).length;
      final seconds = (3 + words * .8 / _rateMultiplier).ceil().clamp(10, 30);
      if (await _tts.speak(message).timeout(Duration(seconds: seconds)) != 1) {
        throw StateError('Speech failed');
      }
    } catch (_) {
      if (generation == _generation) await _tts.stop();
      rethrow;
    }
  }

  @override
  Future<void> stop() async {
    ++_generation;
    await _engine?.stop();
  }
}

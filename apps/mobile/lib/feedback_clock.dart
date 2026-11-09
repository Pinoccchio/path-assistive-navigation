/// A shared monotonic time domain for frame freshness and feedback cooldowns.
DateTime Function() createFeedbackClock() {
  final clock = Stopwatch()..start();
  return () => DateTime.fromMillisecondsSinceEpoch(
    clock.elapsedMilliseconds,
    isUtc: true,
  );
}

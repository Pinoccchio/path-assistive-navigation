import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:thesis_navigation/hazard_history.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
    'pending alerts persist newest first; undo keeps later alerts',
    () async {
      SharedPreferences.setMockInitialValues({});
      final history = HazardHistory();
      final now = DateTime.utc(2026, 11, 19);
      final caution = HazardEvent(now, 'Test', 'Caution', 'chair', 'left');
      final danger = HazardEvent(
        now.add(const Duration(seconds: 2)),
        'Live',
        'Danger',
        'person',
        'ahead',
      );
      final writes = Future.wait([history.add(caution), history.add(danger)]);
      final records = await history.read();
      await writes;
      expect(records.map((e) => e.encode()), [
        danger.encode(),
        caution.encode(),
      ]);
      final reopened = HazardHistory();
      final previous = await reopened.clear();
      expect(await reopened.read(), isEmpty);
      final later = HazardEvent(
        now.add(const Duration(minutes: 1)),
        'Test',
        'Danger',
        'chair',
        'ahead',
      );
      await reopened.add(later);
      await reopened.restore(previous);
      expect((await reopened.read()).map((e) => e.encode()), [
        later.encode(),
        danger.encode(),
        caution.encode(),
      ]);
    },
  );
}

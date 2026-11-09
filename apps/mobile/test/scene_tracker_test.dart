import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/detector.dart';
import 'package:thesis_navigation/scene_tracker.dart';

const personA = Detection('person', .9, 'ahead', [.35, .1, .5, .8]);
const personB = Detection('person', .85, 'ahead', [.6, .1, .75, .8]);
void main() {
  late TemporalSceneTracker tracker;
  late DateTime now;
  setUp(() {
    tracker = TemporalSceneTracker();
    now = DateTime(2026);
  });
  List<Detection> frame(List<Detection> boxes, {int ms = 500}) {
    now = now.add(Duration(milliseconds: ms));
    return tracker.update(boxes, now);
  }

  test('requires two consecutive observations', () {
    expect(frame([personA]), isEmpty);
    expect(frame([]), isEmpty);
    expect(frame([personA]), isEmpty);
    expect(frame([personA]).length, 1);
  });
  test(
    'one-to-one association preserves two people despite input reordering',
    () {
      frame([personA, personB]);
      expect(frame([personB, personA]).length, 2);
      expect(frame([personA, personB]).length, 2);
    },
  );
  test('one missed frame retains count and two misses expire it', () {
    frame([personA, personB]);
    frame([personA, personB]);
    expect(frame([personA]).length, 2);
    expect(frame([personA]).length, 1);
  });
  test('direction wobble is ignored and persistent direction changes', () {
    frame([personA]);
    frame([personA]);
    const left = Detection('person', .9, 'left', [.3, .1, .45, .8]);
    expect(frame([left]).single.direction, 'ahead');
    expect(frame([personA]).single.direction, 'ahead');
    expect(frame([left]).single.direction, 'ahead');
    expect(frame([left]).single.direction, 'left');
  });
  test('long frame gaps reset confirmation', () {
    frame([personA]);
    frame([personA]);
    expect(frame([personA], ms: 2000), isEmpty);
    expect(frame([personA]).length, 1);
  });
  test('class changes do not inherit confirmed tracks', () {
    frame([personA]);
    frame([personA]);
    const bike = Detection('bicycle', .9, 'ahead', [.35, .1, .5, .8]);
    expect(frame([bike]).map((d) => d.label), ['person']);
    expect(frame([bike]).map((d) => d.label), ['bicycle']);
  });
  test('distant new person requires confirmation', () {
    frame([personA]);
    frame([personA]);
    expect(frame([personB]).length, 1);
    final current = frame([personB]);
    expect(current.length, 1);
    expect(current.single.box, personB.box);
  });
  test('reset clears state', () {
    frame([personA]);
    frame([personA]);
    tracker.reset();
    expect(frame([personA]), isEmpty);
  });
}

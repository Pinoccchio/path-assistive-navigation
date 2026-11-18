import 'package:flutter_test/flutter_test.dart';
import 'package:thesis_navigation/zone_preview.dart';

void main() {
  const rows = [
    (zone: ResearchZone.danger, cm: 40.0, score: 90.0),
    (zone: ResearchZone.caution, cm: 100.0, score: 50.0),
    (zone: ResearchZone.farther, cm: 200.0, score: 20.0),
  ];
  test('ranks measured classes by zone and retains unclassified objects', () {
    final order = rankScene(
      [
        (label: 'chair', direction: 'right', score: 30.0),
        (label: 'person', direction: 'ahead', score: 80.0),
        (label: 'chair', direction: 'left', score: 55.0),
        (label: 'chair', direction: 'ahead', score: 80.0),
        (label: 'chair', direction: 'right', score: null),
      ],
      {'chair': rows},
    );
    expect(order.map((p) => p.index), [3, 2, 0, 1, 4]);
    expect(order.map((p) => p.zone), [
      ResearchZone.danger,
      ResearchZone.caution,
      ResearchZone.farther,
      null,
      null,
    ]);
  });
  test(
    'estimates three reference zones for one object and abstains outside coverage',
    () {
      expect(estimateZone(rows, 80), 'Danger');
      expect(estimateZone(rows, 55), 'Caution');
      expect(estimateZone(rows, 30), 'Farther');
      expect(estimateZone(rows, 70), contains('Uncertain'));
      expect(estimateZone(rows, 150), contains('Unknown'));
      expect(estimateZone([], 55), contains('Need measured'));
      expect(
        estimateZone([
          ...rows,
          (zone: ResearchZone.farther, cm: 210.0, score: 52.0),
        ], 55),
        contains('Uncertain'),
      );
      expect(
        estimateZone([
          ...rows,
          (zone: ResearchZone.danger, cm: 120.0, score: 88.0),
        ], 55),
        contains('Uncertain'),
      );
    },
  );
}

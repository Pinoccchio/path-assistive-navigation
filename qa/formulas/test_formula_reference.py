import math
import unittest
from formula_reference import (direction, iou, quantize, dequantize, normalize_inverse_depth as norm,
                               zone, ema, additive_score, approach_tau, hysteresis, kappa, sus)


class FormulaTests(unittest.TestCase):
    def test_direction_boundaries(self):
        self.assertEqual([direction(x) for x in (0, 1/3, 2/3, 1)], ['left', 'center', 'right', 'right'])

    def test_direction_invalid(self):
        for x in (-.1, 1.1, math.nan):
            with self.assertRaises(ValueError): direction(x)

    def test_direction_requires_unletterboxed_coordinate(self):
        # 288x512 portrait image padded horizontally to the 512 square model.
        preview_x = .25
        model_x = (112 + 288 * preview_x) / 512
        self.assertEqual(direction(preview_x), 'left')
        self.assertEqual(direction(model_x), 'center')

    def test_iou_identical_disjoint_and_empty(self):
        self.assertEqual(iou((0,0,2,2), (0,0,2,2)), 1)
        self.assertEqual(iou((0,0,1,1), (2,2,3,3)), 0)
        self.assertEqual(iou((0,0,0,0), (0,0,0,0)), 0)

    def test_iou_overlap_symmetry(self):
        a, b = (0,0,2,2), (1,1,3,3)
        self.assertAlmostEqual(iou(a,b), 1/7)
        self.assertEqual(iou(a,b), iou(b,a))

    def test_iou_reversed_invalid(self):
        with self.assertRaises(ValueError): iou((2,0,0,1), (0,0,1,1))

    def test_quantization_round_trip_and_saturation(self):
        for value in (-1.23, -.24, 0, .27, 1.23):
            self.assertLessEqual(abs(dequantize(quantize(value,.01,0),.01,0)-value), .005001)
        self.assertEqual(quantize(100,.01,0), 127)
        self.assertEqual(quantize(-100,.01,0), -128)

    def test_quantization_invalid_scale(self):
        with self.assertRaises(ValueError): quantize(1,0,0)

    def test_quantization_zero_point(self):
        self.assertEqual(quantize(0,.1,-12), -12)
        self.assertEqual(dequantize(-12,.1,-12), 0)

    def test_depth_normalization_clips(self):
        self.assertEqual([norm(x,2,8) for x in (0,2,5,8,10)], [0,0,.5,1,1])

    def test_depth_invalid_is_unknown(self):
        for x in (norm(5,5,5), norm(math.nan,2,8), norm(5,8,2)):
            self.assertEqual(zone(x,.4,.7), 'unknown')

    def test_normalization_does_not_preserve_metric_zone(self):
        # Same object raw inverse depth, changed background percentile range.
        self.assertEqual(zone(norm(5,0,6),.4,.7), 'danger')
        self.assertEqual(zone(norm(5,0,20),.4,.7), 'farther')

    def test_zone_boundaries(self):
        self.assertEqual([zone(x,.4,.7) for x in (.399,.4,.699,.7)], ['farther','caution','caution','danger'])

    def test_zone_invalid_thresholds(self):
        with self.assertRaises(ValueError): zone(.5,.7,.4)

    def test_ema_initialization_and_constant(self):
        self.assertEqual(ema(.8,None,.2), .8)
        self.assertAlmostEqual(ema(.8,.8,.2), .8)
        self.assertAlmostEqual(ema(1,0,.2), .2)

    def test_score_bounds_and_monotonicity(self):
        for value in (0,.25,.5,.75,1):
            self.assertAlmostEqual(additive_score(1,[value]*4,[.25]*4), value)
        self.assertGreater(additive_score(.9,[1,.5],[.5,.5]), additive_score(.9,[.5,.5],[.5,.5]))

    def test_score_rejects_bad_weights(self):
        with self.assertRaises(ValueError): additive_score(.8,[1,1],[.8,.8])

    def test_tau_units_and_non_approach(self):
        self.assertEqual(approach_tau(100,20),5)
        self.assertIsNone(approach_tau(100,0))
        self.assertIsNone(approach_tau(100,-20))

    def test_hysteresis_sequence_no_chatter(self):
        active=False; actual=[]
        for score in (.69,.7,.68,.5,.4,.41,.7):
            active=hysteresis(active,score,.4,.7); actual.append(active)
        self.assertEqual(actual,[False,True,True,True,False,False,True])

    def test_hysteresis_invalid(self):
        with self.assertRaises(ValueError): hysteresis(False,.5,.7,.4)

    def test_kappa_known_and_degenerate(self):
        self.assertAlmostEqual(kappa(.8,.5), .6)
        with self.assertRaises(ValueError): kappa(1,1)

    def test_sus_endpoints(self):
        self.assertEqual(sus([5,1]*5),100)
        self.assertEqual(sus([1,5]*5),0)
        self.assertEqual(sus([3]*10),50)

    def test_sus_rejects_incomplete(self):
        with self.assertRaises(ValueError): sus([3]*9)


if __name__ == '__main__': unittest.main()

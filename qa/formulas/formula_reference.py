"""Proposed mathematical contract for review; not connected to the Flutter app."""
import math


def finite(*values):
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Inputs must be finite')


def direction(center_x):
    finite(center_x)
    if not 0 <= center_x <= 1:
        raise ValueError('Expected oriented preview coordinate in [0, 1]')
    return 'left' if center_x < 1 / 3 else 'center' if center_x < 2 / 3 else 'right'


def iou(a, b):
    for box in (a, b):
        finite(*box)
        if len(box) != 4 or box[2] < box[0] or box[3] < box[1]:
            raise ValueError('Expected ordered xyxy box')
    area = lambda q: (q[2] - q[0]) * (q[3] - q[1])
    overlap = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = area(a) + area(b) - overlap
    return overlap / union if union > 0 else 0.0


def quantize(value, scale, zero_point):
    finite(value, scale)
    if scale <= 0 or not isinstance(zero_point, int) or not -128 <= zero_point <= 127:
        raise ValueError('Invalid int8 activation parameters')
    # Nearest, ties away from zero: explicitly defined reference convention.
    raw = value / scale
    rounded = math.floor(raw + .5) if raw >= 0 else math.ceil(raw - .5)
    return max(-128, min(127, rounded + zero_point))


def dequantize(value, scale, zero_point):
    finite(scale)
    if scale <= 0 or not isinstance(value, int) or not -128 <= value <= 127 or not isinstance(zero_point, int) or not -128 <= zero_point <= 127:
        raise ValueError('Invalid int8 activation parameters')
    return scale * (value - zero_point)


def normalize_inverse_depth(value, low, high, eps=1e-6):
    """Relative feature only. Invalid/constant maps are unknown, never safe."""
    if not all(math.isfinite(x) for x in (value, low, high)) or high - low <= eps:
        return None
    return max(0., min(1., (value - low) / (high - low)))


def zone(value, caution, danger):
    finite(caution, danger)
    if not 0 <= caution < danger <= 1:
        raise ValueError('Expected 0 <= caution < danger <= 1')
    if value is None or not math.isfinite(value) or not 0 <= value <= 1:
        return 'unknown'
    return 'danger' if value >= danger else 'caution' if value >= caution else 'farther'


def ema(value, previous, beta):
    finite(value, beta)
    if not 0 < beta <= 1:
        raise ValueError('Expected 0 < beta <= 1')
    if previous is None:
        return value
    finite(previous)
    return beta * value + (1 - beta) * previous


def additive_score(confidence, factors, weights, alpha=1):
    finite(confidence, alpha, *factors, *weights)
    if len(factors) != len(weights) or not factors or any(not 0 <= x <= 1 for x in factors) or any(w < 0 for w in weights) or not math.isclose(sum(weights), 1.) or not 0 <= confidence <= 1 or alpha <= 0:
        raise ValueError('Invalid score inputs')
    return confidence ** alpha * sum(x * w for x, w in zip(factors, weights))


def approach_tau(height, height_rate, eps=1e-6):
    finite(height, height_rate)
    if height <= 0 or height_rate <= eps:
        return None
    return height / height_rate


def hysteresis(active, score, off, on):
    finite(score, off, on)
    if not 0 <= off < on <= 1 or not 0 <= score <= 1:
        raise ValueError('Invalid hysteresis inputs')
    return score > off if active else score >= on


def kappa(observed, expected):
    finite(observed, expected)
    if not 0 <= observed <= 1 or not 0 <= expected < 1:
        raise ValueError('Undefined or invalid kappa inputs')
    return (observed - expected) / (1 - expected)


def sus(responses):
    if len(responses) != 10 or any(type(x) is not int or not 1 <= x <= 5 for x in responses):
        raise ValueError('SUS requires ten integer responses in [1, 5]')
    return 2.5 * sum(x - 1 if i % 2 == 0 else 5 - x for i, x in enumerate(responses))

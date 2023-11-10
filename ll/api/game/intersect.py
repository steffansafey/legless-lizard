from math import sqrt
from typing import List, Tuple

EPS = 0.000001


def point_inside_circle(
    point: Tuple[float], center: Tuple[float], radius: float
) -> bool:
    """Check if a point is inside a circle."""
    return _distance(point, center) <= radius


def lines_intersect(
    a1: Tuple[float], a2: Tuple[float], b1: Tuple[float], b2: Tuple[float]
) -> bool:
    """Check if two line segments intersect."""
    denom = ((a2[0] - a1[0]) * (b2[1] - b1[1])) - ((a2[1] - a1[1]) * (b2[0] - b1[0]))
    num1 = ((a1[1] - b1[1]) * (b2[0] - b1[0])) - ((a1[0] - b1[0]) * (b2[1] - b1[1]))
    num2 = ((a1[1] - b1[1]) * (a2[0] - a1[0])) - ((a1[0] - b1[0]) * (a2[1] - a1[1]))

    # Infinite lines intersect somewhere
    if not (-EPS < denom < EPS):
        r = num1 / denom
        s = num2 / denom
        return (r > 0 and r < 1) and (s > 0 and s < 1)
    else:  # Parallel or same line
        if (-EPS < num1 < EPS) or (-EPS < num2 < EPS):
            return _oneD_intersect(a1, a2, b1, b2)
        else:
            return False


def _distance(a: Tuple[float], b: Tuple[float]) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _oneD_intersect(a, b, c, d) -> bool:
    denom_x = b[0] - a[0]
    denom_y = b[1] - a[1]

    if abs(denom_x) > abs(denom_y):
        ub1 = (c[0] - a[0]) / denom_x
        ub2 = (d[0] - a[0]) / denom_x
    else:
        ub1 = (c[1] - a[1]) / denom_y
        ub2 = (d[1] - a[1]) / denom_y

    intervals = _overlap_intervals(ub1, ub2)
    return len(intervals) == 2


def _overlap_intervals(ub1: float, ub2: float) -> List[float]:
    l, r = sorted([ub1, ub2])
    A = max(0, l)
    B = min(1, r)

    if A > B:
        return []
    elif A == B:
        return [A]
    else:
        return [A, B]

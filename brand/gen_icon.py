"""Generate the simplified square app/favicon icon (``icon.svg``).

A bold wound mandrel reduced so it survives 16-32 px: the same cylinder geometry
as the full mark, but with a few heavy wraps and no binary / tail / feet. Mono
``#090909`` on a transparent background.

Run:  python gen_icon.py   ->  writes icon.svg next to this script.
"""

from __future__ import annotations

import math
import pathlib

# --- canvas / style ---------------------------------------------------------
W = H = 512
INK = "#090909"
SAMPLES = 200

# --- cylinder (a fat, near-centred tube that fills the square) ---------------
C0 = (170.0, 322.0)   # near-end centre
C1 = (372.0, 250.0)   # far-end centre
R_NEAR = 150.0
R_FAR = 122.0
K = 0.42              # cross-section foreshortening
TURNS = 1.5
STRANDS = 3
FRONT_SIGN = 1        # which half of the surface faces the viewer
SW_RAIL = 19.0        # rails / rims
SW_HELIX = 16.0       # wraps

# Centre the drawing in the square with ~10% margin (from the measured bbox).
SC, TX, TY = 1.16, -49.93, -91.23


def _unit(x: float, y: float) -> tuple[float, float]:
    m = math.hypot(x, y)
    return (x / m, y / m)


AX = (C1[0] - C0[0], C1[1] - C0[1])
A_DIR = _unit(*AX)
RING = (-A_DIR[1], A_DIR[0])   # ellipse major-axis screen direction


def radius(t: float) -> float:
    return R_NEAR + (R_FAR - R_NEAR) * t


def surface_point(t: float, theta: float) -> tuple[float, float]:
    """A point on the tube surface at axial fraction ``t`` and angle ``theta``."""
    cx, cy, r = C0[0] + t * AX[0], C0[1] + t * AX[1], radius(t)
    return (cx + r * math.cos(theta) * RING[0] + r * K * math.sin(theta) * A_DIR[0],
            cy + r * math.cos(theta) * RING[1] + r * K * math.sin(theta) * A_DIR[1])


def ring_point(centre: tuple[float, float], r: float, theta: float) -> tuple[float, float]:
    """A point on the end-circle of radius ``r`` about ``centre``."""
    return (centre[0] + r * math.cos(theta) * RING[0] + r * K * math.sin(theta) * A_DIR[0],
            centre[1] + r * math.cos(theta) * RING[1] + r * K * math.sin(theta) * A_DIR[1])


def polyline(points: list[tuple[float, float]], close: bool = False) -> str:
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points)
    return d + (" Z" if close else "")


def ellipse(centre: tuple[float, float], r: float) -> str:
    pts = [ring_point(centre, r, 2 * math.pi * i / SAMPLES) for i in range(SAMPLES + 1)]
    return polyline(pts, close=True)


def far_arc(centre: tuple[float, float], r: float) -> str:
    """Only the visible (away-bulging) half of the far rim."""
    pts = [ring_point(centre, r, 2 * math.pi * i / SAMPLES)
           for i in range(SAMPLES + 1)
           if math.sin(2 * math.pi * i / SAMPLES) * FRONT_SIGN > 0]
    return polyline(pts)


def helix_runs(theta0: float, direction: int) -> list[list[tuple[float, float]]]:
    """Front-facing arcs of one helix line (hidden-line removal)."""
    runs: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    for i in range(SAMPLES + 1):
        t = i / SAMPLES
        theta = theta0 + direction * TURNS * 2 * math.pi * t
        if math.sin(theta) * FRONT_SIGN > 0:
            cur.append(surface_point(t, theta))
        elif len(cur) > 1:
            runs.append(cur)
            cur = []
    if len(cur) > 1:
        runs.append(cur)
    return runs


def _stroke(d: str, width: float, extra: str = "") -> str:
    return (f'<path d="{d}" stroke="{INK}" stroke-width="{width}" fill="none" '
            f'stroke-linecap="round"{extra}/>')


def svg() -> str:
    top0 = (C0[0] + R_NEAR * RING[0], C0[1] + R_NEAR * RING[1])
    top1 = (C1[0] + R_FAR * RING[0], C1[1] + R_FAR * RING[1])
    bot0 = (C0[0] - R_NEAR * RING[0], C0[1] - R_NEAR * RING[1])
    bot1 = (C1[0] - R_FAR * RING[0], C1[1] - R_FAR * RING[1])

    el: list[str] = []
    for a, b in ((top0, top1), (bot0, bot1)):
        el.append(_stroke(f"M {a[0]:.2f} {a[1]:.2f} L {b[0]:.2f} {b[1]:.2f}", SW_RAIL))
    el.append(_stroke(far_arc(C1, R_FAR), SW_RAIL))
    for direction in (+1, -1):
        for s in range(STRANDS):
            for run in helix_runs(2 * math.pi * s / STRANDS, direction):
                el.append(_stroke(polyline(run), SW_HELIX, ' stroke-linejoin="round"'))
    el.append(f'<path d="{ellipse(C0, R_NEAR)}" stroke="{INK}" '
              f'stroke-width="{SW_RAIL}" fill="none"/>')

    body = "\n    ".join(el)
    group = f'<g transform="translate({TX},{TY}) scale({SC})">\n    {body}\n  </g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">\n  {group}\n</svg>\n')


if __name__ == "__main__":
    out = pathlib.Path(__file__).with_name("icon.svg")
    out.write_text(svg(), encoding="utf-8")
    print(f"wrote {out.name}")

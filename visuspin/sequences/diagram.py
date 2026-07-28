"""
Pulse-sequence timing-diagram renderer: draws a Block list (see
visuspin.sequences.blocks) as a schematic timeline, in the same left-to-right
convention used throughout the solid-state NMR literature (e.g. any pulse
sequence figure in Duer, "Introduction to Solid-State NMR Spectroscopy," or
Levitt, "Spin Dynamics"). Deliberately NOT drawn to a real time scale: pulse
(us), delay (ms), and acquisition (ms-s) durations differ by orders of
magnitude, so -- exactly like real pulse-program diagrams -- every block type
gets a fixed icon width and the real parameter values are reported as text
labels instead of a proportional time axis.
"""
from __future__ import annotations
import numpy as np

from .blocks import Pulse, Delay, Loop, SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep

_WIDTH = {
    Pulse: 0.6, Delay: 1.4, SpinLock: 1.8, Acquire: 2.2,
    Recouple: 2.0, CrossPolarize: 2.0, DFSSweep: 1.6,
}
_GAP = 0.25


def _block_width(b) -> float:
    for cls, w in _WIDTH.items():
        if isinstance(b, cls):
            return w
    return 1.0


def _flatten(blocks):
    """Yields (block, depth); Loop bodies are flattened inline (depth+1) with
    an "__loop_end__" sentinel so the renderer can draw a bracket around
    them, matching how a real pulse program shows a repeated block train."""
    for b in blocks:
        if isinstance(b, Loop):
            yield (b, 0)
            for sub in b.body:
                for item in _flatten([sub]):
                    yield (item[0], item[1] + 1)
            yield ("__loop_end__", 0)
        else:
            yield (b, 0)


def render_sequence_diagram(blocks: list, ax=None):
    """Draws onto `ax` (creating a new matplotlib Figure/Axes if None) and
    returns the Figure."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    created = ax is None
    if created:
        fig, ax = plt.subplots(figsize=(max(6, 1.2 * len(blocks) + 2), 2.4))
    else:
        fig = ax.figure

    x = 0.0
    y0, h = 0.0, 1.0
    loop_stack = []

    for b, depth in _flatten(blocks):
        if b == "__loop_end__":
            start_x, n = loop_stack.pop()
            end_x = x
            bracket_y = y0 + h + 0.55
            ax.plot([start_x, start_x, end_x - _GAP, end_x - _GAP],
                     [bracket_y - 0.08, bracket_y, bracket_y, bracket_y - 0.08], color="black", lw=1.2)
            ax.text((start_x + end_x - _GAP) / 2, bracket_y + 0.1, f"x{n}", ha="center", va="bottom", fontsize=9)
            continue
        if isinstance(b, Loop):
            loop_stack.append((x, int(b.values["n_repeats"])))
            continue

        w = _block_width(b)
        cx = x + w / 2
        if isinstance(b, Pulse):
            rect = mpatches.Rectangle((x, y0), w, h, facecolor="#2b6cb0", edgecolor="black")
            ax.add_patch(rect)
            ax.text(cx, y0 + h + 0.08, f"{b.values['flip_deg']:.0f}°", ha="center", va="bottom", fontsize=9)
            axis_deg = b.values["axis_deg"]
            axis_lbl = "x" if abs(axis_deg) < 1 else ("y" if abs(axis_deg - 90) < 1 else f"{axis_deg:.0f}°")
            ax.text(cx, y0 - 0.12, axis_lbl, ha="center", va="top", fontsize=8, style="italic")
        elif isinstance(b, Delay):
            ax.plot([x, x + w], [y0 + h / 2, y0 + h / 2], color="black", lw=1.5)
            ax.text(cx, y0 + h / 2 + 0.15, f"{b.values['duration_ms']:g} ms", ha="center", va="bottom", fontsize=8)
        elif isinstance(b, Acquire):
            t = np.linspace(0, 3 * np.pi, 60)
            yy = y0 + h / 2 + 0.35 * np.sin(t) * np.exp(-t / 4)
            xx = x + w * t / t.max()
            ax.plot(xx, yy, color="#2f855a", lw=1.3)
            ax.text(cx, y0 + h + 0.08, "Acquire", ha="center", va="bottom", fontsize=9)
        elif isinstance(b, SpinLock):
            rect = mpatches.Rectangle((x, y0), w, h, facecolor="#d69e2e", edgecolor="black", alpha=0.85)
            ax.add_patch(rect)
            ax.text(cx, y0 + h + 0.08, "Spin-lock", ha="center", va="bottom", fontsize=9)
        elif isinstance(b, Recouple):
            rect = mpatches.Rectangle((x, y0), w, h, facecolor="none", edgecolor="black", hatch="///")
            ax.add_patch(rect)
            ax.text(cx, y0 + h + 0.08, "Recouple", ha="center", va="bottom", fontsize=9)
        elif isinstance(b, CrossPolarize):
            poly = mpatches.Polygon([[x, y0], [x + w, y0], [x + w, y0 + h], [x, y0 + h * 0.15]],
                                      facecolor="#c05621", edgecolor="black")
            ax.add_patch(poly)
            ax.text(cx, y0 + h + 0.08, "CP", ha="center", va="bottom", fontsize=9)
        elif isinstance(b, DFSSweep):
            t = np.linspace(0, 1, 40)
            yy = y0 + h / 2 + 0.35 * np.sin(2 * np.pi * (2 + 8 * t) * t)
            ax.plot(x + w * t, yy, color="#805ad5", lw=1.3)
            ax.text(cx, y0 + h + 0.08, "DFS", ha="center", va="bottom", fontsize=9)
        x += w + _GAP

    ax.set_xlim(-0.3, x + 0.3)
    ax.set_ylim(-0.6, 1.9)
    ax.axis("off")
    if created:
        fig.tight_layout()
    return fig

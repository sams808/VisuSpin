"""Smoke tests for the pulse-sequence timing-diagram renderer: since this is
a visualization (not a physics-correctness) module, "correct" here means it
runs cleanly for every shipped preset and actually draws something for every
block type used, rather than a numerically-verified physical claim."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
from visuspin.sequences.presets import PRESETS
from visuspin.sequences.diagram import render_sequence_diagram


def test_every_shipped_preset_renders_without_error():
    for name, builder in PRESETS.items():
        fig = render_sequence_diagram(builder())
        n_artists = len(fig.axes[0].patches) + len(fig.axes[0].lines) + len(fig.axes[0].texts)
        assert n_artists > 0, f"preset '{name}' produced an empty diagram"
        matplotlib.pyplot.close(fig)
    print(f"PASS all {len(PRESETS)} presets ({', '.join(PRESETS.keys())}) render without error")


def test_loop_bracket_is_drawn_for_cpmg():
    from visuspin.sequences.presets import cpmg
    fig = render_sequence_diagram(cpmg(n_echoes=4))
    ax = fig.axes[0]
    bracket_texts = [t.get_text() for t in ax.texts if t.get_text().startswith("x")]
    assert "x4" in bracket_texts, f"expected an 'x4' loop-count label, got texts: {[t.get_text() for t in ax.texts]}"
    matplotlib.pyplot.close(fig)
    print("PASS CPMG diagram draws an 'x4' loop-repeat bracket label")


if __name__ == "__main__":
    test_every_shipped_preset_renders_without_error()
    test_loop_bracket_is_drawn_for_cpmg()
    print("\nALL DIAGRAM RENDERER TESTS PASSED")

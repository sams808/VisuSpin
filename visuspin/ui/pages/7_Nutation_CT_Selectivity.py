import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES
from visuspin.physics.quadrupole import ct_selective_enhancement, nutation_curve
from visuspin.physics import bloch

st.set_page_config(page_title="VisuSpin — Nutation & CT-Selectivity", page_icon="🧪", layout="wide")
page_header("Lesson 7: Nutation & CT-Selectivity")
lesson_header(
    "Lesson 7 of 11",
    "A quadrupolar nucleus has several transitions. Does a pulse excite them all equally?",
    "Lesson 0's flip-angle demo assumed one clean transition. Lesson 4 showed quadrupolar "
    "nuclei have several. When you fire an RF pulse, what actually happens to the central "
    "transition specifically?",
)

quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5]
st.markdown(
    """
Naively, you might expect the central transition to tip at whatever rate the
RF field (ν1) dictates — same as any spin-1/2. It doesn't. If the pulse is
weak enough that it can't reach the far-away satellite transitions at all
(**CT-selective**), the central transition nutates *faster* than that naive
rate — by a clean, exact factor of (I + 1/2). This is a genuine efficiency
gift, not a loss.
"""
)

c1, c2 = st.columns([1, 1.6])
with c1:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    sat_half_width_khz = st.slider("Satellite manifold half-width (kHz, ~ set by Cq)", 10.0, 2000.0, 300.0, 10.0)
    nu1_khz = st.slider("RF field ν1 (kHz)", 1.0, 150.0, 40.0, 1.0)
    max_pulse_us = st.slider("Max pulse duration (µs)", 5.0, 200.0, 60.0, 1.0)
    enh_selective = ct_selective_enhancement(nuc.spin, sat_half_width_khz * 1000, nu1_khz * 1000)
    st.metric("CT-selective enhancement", f"{enh_selective:.1f}× = I+1/2")

with c2:
    with predict_then_reveal("If the pulse is strong enough to also reach the satellites (non-selective), does the enhancement still apply?"):
        curve_sel = nutation_curve(nuc.spin, nu1_khz, enh_selective, max_pulse_us)
        curve_non = nutation_curve(nuc.spin, nu1_khz, 1.0, max_pulse_us)
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.plot(curve_sel["t_us"], curve_sel["signal"], color="#5b46e5", label=f"CT-selective ({enh_selective:.1f}×)")
        ax.plot(curve_non["t_us"], curve_non["signal"], color="#c05621", label="Non-selective (1×)")
        ax.set_xlabel("Pulse duration (µs)"); ax.set_ylabel("CT signal |Mxy|"); ax.legend()
        st.pyplot(fig); plt.close(fig)
        st.markdown(
            f"""
            No — it drops back toward the plain (non-enhanced) rate, and the curve stops being a
            clean sinusoid. Once the pulse starts reaching the satellites too, signal genuinely
            "bleeds" between transitions, distorting the nutation curve. That distortion isn't
            just noise to ignore: real experiments deliberately record a full nutation curve like
            this one and fit its exact non-sinusoidal shape to extract {term("Cq and η", "the quadrupolar coupling constant and asymmetry parameter — see Lesson 4")}.
            """
        )

key_takeaway(
    "For a quadrupolar central transition, weaker/more-selective pulses aren't just gentler — "
    "they're genuinely more efficient, nutating (I+1/2) times faster. Push into the non-selective "
    "regime and you lose that boost and gain distortion instead."
)

st.subheader("DFS: borrowing signal from the satellites")
st.markdown(
    """
Even with the CT-selective boost, the central transition's signal is
inherently limited. **Double frequency sweeps (DFS)** offer another lever:
an adiabatic RF sweep through the satellite manifold that genuinely
transfers population *from* the satellites *into* the central transition —
boosting CT signal beyond what a simple pulse alone could ever reach.
"""
)
dfs1, dfs2, dfs3 = st.columns(3)
with dfs1:
    dfs_nu1_khz = st.slider("DFS ν1 (kHz)", 0.1, 50.0, 2.0, 0.1)
with dfs2:
    dfs_sweep_khz = st.slider("Sweep range (kHz)", 1.0, 500.0, 50.0, 1.0)
with dfs3:
    dfs_duration_ms = st.slider("Sweep duration (ms)", 0.1, 10.0, 2.0, 0.1)

with predict_then_reveal("'Adiabatic' passage requires the sweep to move slowly compared to ν1. If ν1 is nearly as large as the sweep range itself, does the transfer still work?"):
    adiabaticity = dfs_sweep_khz / max(dfs_nu1_khz, 1e-6)
    ens = bloch.Ensemble.from_gaussian_offsets(1, 0.0, seed=1)
    bloch.apply_dfs_sweep(ens, dfs_duration_ms, dfs_nu1_khz, dfs_sweep_khz)
    mz_final = float(ens.mz[0])
    st.markdown(
        f"Adiabaticity ratio (sweep range / ν1) = **{adiabaticity:.1f}** "
        f"({'well inside' if adiabaticity > 10 else 'NOT in'} the adiabatic regime, which needs ν1 ≪ sweep range) "
        f" → final Mz = **{mz_final:.3f}** (starts at +1; true adiabatic passage inverts it toward −1)"
    )
    fig3, ax3 = plt.subplots(figsize=(7, 1.2))
    ax3.barh([0], [1], color="#e2e8f0")
    ax3.barh([0], [max(min(mz_final, 1), -1)], color="#5b46e5" if mz_final < 0 else "#c05621", left=0)
    ax3.set_xlim(-1, 1); ax3.set_yticks([]); ax3.set_xlabel("Mz after DFS sweep")
    st.pyplot(fig3); plt.close(fig3)
    st.write(
        "No — push ν1 up toward the sweep range and the transfer fails: instead of a clean "
        "inversion, Mz stalls partway. Adiabaticity isn't a formality, it's the entire mechanism."
    )

key_takeaway(
    "Both tricks in this lesson exploit the SAME fact from Lesson 4 — quadrupolar nuclei have "
    "extra transitions beyond the one we observe. CT-selectivity avoids wasting pulse power on "
    "them; DFS actively steals population from them. Neither has any analogue for a plain "
    "spin-1/2 nucleus."
)

next_lesson("Lesson 8 — J-Coupling & Decoupling", "pages/8_J_Coupling_Decoupling.py")

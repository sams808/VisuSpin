import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.dqsq import dqsq_spectrum
from visuspin.physics.hmqc import optimal_tau_ms

st.set_page_config(page_title="VisuSpin — DQ-SQ Correlation", page_icon="🔗", layout="wide")
page_header("Lesson 16: DQ-SQ Homonuclear Correlation")
lesson_header(
    "Lesson 16 of 24",
    "Lesson 14 asked: which sites are next to which, not just how many of each?",
    "Two glasses can have identical Qn populations but totally different network topology. "
    "What experiment actually distinguishes a well-mixed network from a clustered one?",
)

st.markdown(
    f"""
{term("DQ-SQ", "double-quantum/single-quantum correlation: a homonuclear dipolar-recoupling experiment (BABA, POST-C7, SPC5...) that excites a shared coherence between two nearby spins of the SAME nucleus")}
directly answers this. It correlates a pair's combined double-quantum shift
(F1 = shift_a + shift_b) with each partner's own single-quantum shift (F2)
— giving a genuine map of *which sites sit next to which*, not just how much
of each is present.
"""
)

st.subheader("Two very different network structures, read off the map")
d_hz = st.slider("Recoupled dipolar coupling D (Hz)", 200.0, 5000.0, 1500.0, 50.0)
tau_opt = optimal_tau_ms(d_hz)
tau_ms = st.slider("Recoupling time τ (ms)", 0.0, 2 * tau_opt, tau_opt, max(tau_opt / 50, 1e-4), format="%.4f")

q_shifts = {"Q2": -88.0, "Q3": -98.0, "Q4": -110.0}

with predict_then_reveal("A site coupled to a chemically-identical neighbor (Q4 next to Q4) — where does its peak land relative to the diagonal?"):
    pairs_clustered = [
        {"shift_a_hz": q_shifts["Q4"], "shift_b_hz": q_shifts["Q4"], "amplitude": 1.0},
        {"shift_a_hz": q_shifts["Q2"], "shift_b_hz": q_shifts["Q2"], "amplitude": 1.0},
    ]
    spec_clustered = dqsq_spectrum(pairs_clustered, d_hz, tau_ms, f2_range_hz=(-130, -70), linewidth_hz=2.0, n_points=300)
    fig1, ax1 = plt.subplots(figsize=(6, 5.5))
    cf1 = ax1.contourf(spec_clustered["f2_hz"], spec_clustered["f1_hz"], spec_clustered["intensity"], levels=20, cmap="viridis")
    diag = np.linspace(-130, -70, 50)
    ax1.plot(diag, 2 * diag, color="white", linestyle="--", linewidth=1, alpha=0.6)
    ax1.set_xlabel("F2 (ppm)"); ax1.set_ylabel("F1 = DQ sum (ppm)")
    ax1.set_title("Clustered network: Q4 next to Q4, Q2 next to Q2")
    st.pyplot(fig1); plt.close(fig1)
    st.write("Right on the diagonal (dashed line, F1=2×F2) — the signature of a site next to a chemically identical neighbor.")

st.markdown("Now compare a **well-mixed** network, where Q4 and Q2 sit next to each other instead of clustering with their own kind:")
pairs_mixed = [
    {"shift_a_hz": q_shifts["Q4"], "shift_b_hz": q_shifts["Q2"], "amplitude": 1.0},
]
spec_mixed = dqsq_spectrum(pairs_mixed, d_hz, tau_ms, f2_range_hz=(-130, -70), linewidth_hz=2.0, n_points=300)
fig2, ax2 = plt.subplots(figsize=(6, 5.5))
cf2 = ax2.contourf(spec_mixed["f2_hz"], spec_mixed["f1_hz"], spec_mixed["intensity"], levels=20, cmap="viridis")
ax2.plot(diag, 2 * diag, color="white", linestyle="--", linewidth=1, alpha=0.6)
ax2.set_xlabel("F2 (ppm)"); ax2.set_ylabel("F1 = DQ sum (ppm)")
ax2.set_title("Mixed network: Q4 directly bonded to Q2")
st.pyplot(fig2); plt.close(fig2)

key_takeaway(
    "Both networks can have identical Q4:Q2 populations (Lesson 14's 1D spectrum would look "
    "identical), but DQ-SQ tells them apart immediately: diagonal auto-peaks mean clustering "
    "(like next to like), off-diagonal cross-peaks mean genuine mixing (different sites bonded "
    "directly). This is the connectivity information a population count alone can never give you."
)

next_lesson("Lesson 17 — STMAS vs. MQMAS", "pages/17_STMAS.py")

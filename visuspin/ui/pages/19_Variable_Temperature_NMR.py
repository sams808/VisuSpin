import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.dynamics import two_site_exchange_spectrum, arrhenius_rate_hz

st.set_page_config(page_title="VisuSpin — Variable-Temperature NMR", page_icon="🌡️", layout="wide")
page_header("Lesson 19: Variable-Temperature NMR & Motional Narrowing")
lesson_header(
    "Lesson 19 of 24",
    "Heat a sample through a phase transition and a sharp doublet can merge, then sharpen again. Why?",
    "Above some temperature, ions or molecules start hopping between sites fast enough to matter "
    "on the NMR timescale. What does that do to the spectrum, and why isn't it a simple, gradual blur?",
)

st.markdown(
    f"""
When a nucleus {term("exchanges", "hops between two or more distinct sites, e.g. via ionic diffusion, molecular reorientation, or a structural phase transition")}
faster than the frequency separation between its sites, NMR can no longer
resolve them as separate peaks — it sees only their **population-weighted
average**. How fast is "fast enough" depends entirely on the exchange rate
*relative to* the frequency separation, not on any absolute speed.
"""
)

st.subheader("Two regimes, same two sites")
c1, c2 = st.columns([1, 1.5])
with c1:
    sep_hz = st.slider("Frequency separation between sites (Hz)", 100.0, 2000.0, 800.0, 50.0)
    k_hz = st.slider("Exchange rate k (Hz, log-ish scale via slider steps)", 0.1, 20000.0, 1.0, 0.1)
    T2_ms = st.slider("Intrinsic T2 (ms)", 10.0, 300.0, 100.0, 5.0)
with c2:
    with predict_then_reveal("As you push k from very slow to very fast, does the spectrum change gradually (peaks slowly drifting together), or suddenly (broadening, then collapsing to one peak)?"):
        out = two_site_exchange_spectrum(-sep_hz / 2, sep_hz / 2, k_hz, T2_ms, acquire_ms=250, n_isochromats=3000, n_steps=1200)
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.plot(out["freq_hz"], out["intensity"], color="#5b46e5")
        ax.set_xlim(-sep_hz, sep_hz)
        ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
        ax.set_title(f"k = {k_hz:.1f} Hz, separation = {sep_hz:.0f} Hz (ratio k/Δν = {k_hz/sep_hz:.3f})")
        st.pyplot(fig); plt.close(fig)
        st.write(
            "Suddenly, around k ≈ Δν (the classic **coalescence** point): well below it, two "
            "resolved peaks slowly broaden; well above it, a single peak rapidly sharpens back "
            "down toward the intrinsic T2 linewidth. The transition through coalescence itself is "
            "the broadest, messiest-looking part of the whole series — a real phase transition "
            "captured by VT-NMR often shows exactly this signature."
        )

st.subheader("Connecting exchange rate to temperature")
st.markdown("Exchange rates are almost always thermally activated, following an Arrhenius law.")
c3, c4 = st.columns([1, 1.5])
with c3:
    Ea = st.slider("Activation energy Ea (kJ/mol)", 5.0, 100.0, 30.0, 1.0)
    k0 = st.slider("Attempt frequency k0 (log10 Hz)", 8.0, 14.0, 12.0, 0.5)
    T_kelvin = st.slider("Temperature (K)", 200.0, 600.0, 350.0, 5.0)
with c4:
    k_at_T = arrhenius_rate_hz(10 ** k0, Ea, T_kelvin)
    st.metric("Exchange rate at this temperature", f"{k_at_T:.2e} Hz")
    T_range = np.linspace(200, 600, 200)
    k_range = arrhenius_rate_hz(10 ** k0, Ea, T_range)
    fig2, ax2 = plt.subplots(figsize=(6.5, 3.2))
    ax2.semilogy(T_range, k_range, color="#c05621")
    ax2.axvline(T_kelvin, color="gray", linestyle="--", linewidth=1)
    ax2.axhline(sep_hz, color="#5b46e5", linestyle=":", linewidth=1, label=f"coalescence (k=Δν={sep_hz:.0f} Hz)")
    ax2.set_xlabel("Temperature (K)"); ax2.set_ylabel("Exchange rate (Hz)"); ax2.legend()
    st.pyplot(fig2); plt.close(fig2)

key_takeaway(
    "Because exchange rate depends exponentially on temperature (Arrhenius), a VT-NMR series "
    "usually looks unremarkable over a wide temperature range and then changes dramatically over "
    "a comparatively narrow window centered on the coalescence temperature — the temperature "
    "where the thermally-activated hopping rate crosses the frequency separation being probed. "
    "That crossing point is itself a measurement: tracking coalescence at several different "
    "frequency separations (e.g. different B0 fields) lets you extract the activation energy directly."
)

next_lesson("Lesson 20 — Paramagnetic NMR", "pages/20_Paramagnetic_NMR.py")

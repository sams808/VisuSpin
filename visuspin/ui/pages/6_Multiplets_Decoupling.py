import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.decoupling import multiplet_spectrum, decoupled_spectrum

st.set_page_config(page_title="VisuSpin — Multiplets & Decoupling", page_icon="🔊", layout="wide")
page_header("Multiplets & Decoupling", "J-coupled multiplets collapsing under heteronuclear decoupling")

with st.sidebar:
    J = st.slider("J coupling (Hz)", 5.0, 300.0, 140.0, 1.0)
    n_coupled = st.slider("Number of equivalent coupled I=1/2 spins", 0, 6, 1, 1)
    linewidth = st.slider("Natural linewidth (Hz)", 0.5, 50.0, 8.0, 0.5)
    st.subheader("Decoupling quality")
    residual = st.slider("Residual coupling / imperfect decoupling (Hz)", 0.0, 150.0, 0.0, 1.0,
                           help="0 = ideal decoupling. Larger values model finite RF field / off-resonance / decoupling-sequence mismatch as an added broadening.")

coupled = multiplet_spectrum(J, n_coupled, linewidth_hz=linewidth) if n_coupled > 0 else None
decoupled = decoupled_spectrum(linewidth_hz=linewidth, residual_coupling_hz=residual)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Without decoupling** ({n_coupled} coupled spin(s), J={J:.0f} Hz)")
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    if coupled is not None:
        ax.plot(coupled["freq_hz"], coupled["intensity"], color="#c05621")
    else:
        ax.plot(decoupled["freq_hz"], decoupled["intensity"], color="#c05621")
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
    st.pyplot(fig); plt.close(fig)

with col2:
    st.markdown(f"**With decoupling** (effective linewidth {decoupled['effective_linewidth_hz']:.1f} Hz)")
    fig2, ax2 = plt.subplots(figsize=(5.5, 3.4))
    ax2.plot(decoupled["freq_hz"], decoupled["intensity"], color="#5b46e5")
    ax2.set_xlabel("Frequency (Hz)"); ax2.set_ylabel("Intensity")
    st.pyplot(fig2); plt.close(fig2)

st.caption(
    "Multiplet: first-order (weak-coupling) n+1 lines, binomial intensities. Decoupling collapses the "
    "multiplet to its centroid; a nonzero residual coupling models imperfect decoupling as broadening "
    "added in quadrature to the natural linewidth (a standard simplified picture, not a Floquet simulation "
    "of a specific sequence like TPPM/SPINAL-64 — see decoupling.py docstring)."
)

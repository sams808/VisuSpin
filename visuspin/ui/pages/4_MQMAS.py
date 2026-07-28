import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.mqmas import mqmas_shear_ratio, mqmas_spectrum

st.set_page_config(page_title="VisuSpin — MQMAS", page_icon="🌀", layout="wide")
page_header("MQMAS", "Why correlating a multiple-quantum dimension removes 2nd-order quadrupolar broadening")

quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5 and n.is_half_integer_quadrupolar]
with st.sidebar:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    Cq_mhz = st.slider("Cq (MHz)", 0.1, 15.0, 2.5, 0.1)
    eta = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01)
    max_p = int(2 * nuc.spin)
    p_options = [p for p in range(3, max_p + 1, 2)]
    p = st.selectbox("Multiple-quantum order", p_options, index=0) if p_options else None

if p is None:
    st.warning(f"{nuc.formatted_symbol()} (I={nuc.spin_label()}) has no multiple-quantum coherence beyond the central transition.")
else:
    nu0 = nu0_hz(nuc, b0)
    R = mqmas_shear_ratio(nuc.spin, p)
    st.markdown(f"**Shear ratio R(I={nuc.spin_label()}, {p}Q) = {R:.4f}**  (literature closed-form value; see mqmas.py docstring)")

    spec = mqmas_spectrum(nuc.spin, Cq_mhz * 1e6, eta, nu0, p=p, isotropic_shift_hz=0.0, n_samples=3000)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(5.5, 5))
        ax.scatter(spec["f2_hz"], spec["f1_raw_hz"], s=4, alpha=0.5, color="#c05621")
        ax.set_xlabel("F2 (CT, Hz)"); ax.set_ylabel(f"F1 raw ({p}Q, Hz)")
        ax.set_title("Before shearing: anisotropy correlated across both dimensions")
        st.pyplot(fig); plt.close(fig)
    with col2:
        fig2, ax2 = plt.subplots(figsize=(5.5, 5))
        ax2.scatter(spec["f2_hz"], spec["f1_sheared_hz"], s=4, alpha=0.5, color="#5b46e5")
        spread = np.std(spec["f1_sheared_hz"])
        pad = max(spread * 50, 1e-6)
        ax2.set_ylim(np.mean(spec["f1_sheared_hz"]) - pad, np.mean(spec["f1_sheared_hz"]) + pad)
        ax2.set_xlabel("F2 (CT, Hz)"); ax2.set_ylabel("F1 sheared (Hz)")
        ax2.set_title(f"After shearing (F1 - R·F2): isotropic ridge\n(spread = {spread:.2e} Hz, by construction)")
        st.pyplot(fig2); plt.close(fig2)

    st.markdown(
        """
        **What this schematic shows, and what it simplifies.** F2 (the CT dimension) uses
        VisuSpin's first-principles static 2nd-order quadrupolar shift. Rigorously deriving
        the true MAS-averaged multiple-quantum lineshape requires Floquet (average-Hamiltonian)
        theory — substituting the time-dependent crystallite orientation into the static formula
        and just time-averaging does *not* reproduce a single orientation-independent shear ratio
        (checked directly; see `tests/test_mqmas.py`). So F1(raw) here is *constructed* as the
        literature shear ratio R(I,p) times the same per-orientation CT shape, which correctly
        reproduces the one thing MQMAS is famous for teaching — a single shear collapses the
        anisotropic spread — without overclaiming a from-scratch derivation of the true pQ lineshape.
        """
    )

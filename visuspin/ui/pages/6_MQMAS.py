import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.mqmas import mqmas_shear_ratio, mqmas_spectrum

st.set_page_config(page_title="VisuSpin — MQMAS", page_icon="🌀", layout="wide")
page_header("Lesson 6: MQMAS")
lesson_header(
    "Lesson 6 of 11",
    "MAS can't remove second-order quadrupolar broadening. What can?",
    "Lesson 5 ended on a cliffhanger: quadrupolar central-transition broadening survives even "
    "arbitrarily fast spinning. If spinning faster can't fix it, what's left to try?",
)

st.markdown(
    f"""
The trick is to stop trying to fix it with *better hardware* and instead
fix it with **more dimensions**. Every half-integer quadrupolar nucleus has,
in addition to its usual single-quantum central transition (1Q, what every
previous lesson observed), higher-order **multiple-quantum coherences** (3Q,
5Q, ...) of that same transition. Both the 1Q and the 3Q coherence sit on the
*same* crystallite, so they experience the same orientation — but their
second-order broadenings scale by a different, fixed ratio {term("R(I,p)", "the MQMAS shear ratio, a known constant depending only on the spin I and coherence order p")}.

Run an experiment that lets both coherences evolve, one after the other, and
you get a genuinely 2D dataset where F2 (detected, 1Q) and F1 (indirect, 3Q)
are correlated point-for-point for every crystallite. Because that ratio R
is a single fixed number, a simple linear **shear** — subtract R times F2
from F1 — can undo the correlation completely.
"""
)

quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5 and n.is_half_integer_quadrupolar]
c1, c2 = st.columns([1, 2])
with c1:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    Cq_mhz = st.slider("Cq (MHz)", 0.1, 15.0, 2.5, 0.1)
    eta = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01)
    max_p = int(2 * nuc.spin)
    p_options = [p for p in range(3, max_p + 1, 2)]
    p = st.selectbox("Multiple-quantum order", p_options, index=0) if p_options else None
    if p is not None:
        R = mqmas_shear_ratio(nuc.spin, p)
        st.metric(f"Shear ratio R({nuc.spin_label()}, {p}Q)", f"{R:.4f}")

if p is None:
    st.warning(f"{nuc.formatted_symbol()} (I={nuc.spin_label()}) has no multiple-quantum coherence beyond the central transition.")
else:
    nu0 = nu0_hz(nuc, b0)
    spec = mqmas_spectrum(nuc.spin, Cq_mhz * 1e6, eta, nu0, p=p, isotropic_shift_hz=0.0, n_samples=3000)

    with predict_then_reveal(
        "F1 and F2 are correlated, but by a ratio R that usually isn't a simple round number "
        "(look at R above). Can a single fixed subtraction really squeeze out ALL of the spread, "
        "or would you expect some residual smear left over?"
    ):
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(5.5, 5))
            ax.scatter(spec["f2_hz"], spec["f1_raw_hz"], s=4, alpha=0.5, color="#c05621")
            ax.set_xlabel("F2 (CT, Hz)"); ax.set_ylabel(f"F1 raw ({p}Q, Hz)")
            ax.set_title("Before shearing: correlated anisotropy")
            st.pyplot(fig); plt.close(fig)
        with col2:
            fig2, ax2 = plt.subplots(figsize=(5.5, 5))
            ax2.scatter(spec["f2_hz"], spec["f1_sheared_hz"], s=4, alpha=0.5, color="#5b46e5")
            spread = np.std(spec["f1_sheared_hz"])
            pad = max(spread * 50, 1e-6)
            ax2.set_ylim(np.mean(spec["f1_sheared_hz"]) - pad, np.mean(spec["f1_sheared_hz"]) + pad)
            ax2.set_xlabel("F2 (CT, Hz)"); ax2.set_ylabel("F1 sheared (Hz)")
            ax2.set_title(f"After shearing: a single isotropic value\n(spread = {spread:.2e} Hz)")
            st.pyplot(fig2); plt.close(fig2)
        st.markdown(
            f"""
            Every point collapses onto one single value — because R is *exactly* the ratio between
            the two dimensions' broadenings for every crystallite, subtracting R×F2 from F1 cancels
            the orientation-dependent part completely, regardless of what that orientation was. F2
            still shows the full, ugly anisotropic lineshape from Lesson 4; the sheared F1 axis shows
            none of it — a genuinely isotropic line, resolved by chemical/quadrupolar environment.
            """
        )

    key_takeaway(
        "MQMAS trades a hardware problem (broadening that MAS alone can't remove) for a data-"
        "processing one (correlate two coherences that share the same orientation-dependence, "
        "then subtract them out). The same broadening is still physically present in F2 — MQMAS "
        "doesn't erase it, it just gives you a second axis where it isn't."
    )
    st.info(
        "**Scope note:** F2 uses VisuSpin's first-principles static 2nd-order quadrupolar shift. "
        "The true *MAS-averaged* multiple-quantum lineshape needs Floquet (average-Hamiltonian) "
        "theory to derive rigorously — a naive time-average of the static formula was checked "
        "directly and does *not* reproduce a single fixed ratio (see `tests/test_mqmas.py`). So "
        "F1(raw) here is constructed using the standard literature shear ratio R(I,p), which "
        "correctly demonstrates the shearing principle without overclaiming a from-scratch "
        "derivation of the exact pQ lineshape."
    )

next_lesson("Lesson 7 — Nutation & CT-Selectivity", "pages/7_Nutation_CT_Selectivity.py")

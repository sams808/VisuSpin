import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES
from visuspin.physics.stmas import satellite_first_order_shift_hz, satellite_residual_vs_angle_error, MAGIC_ANGLE_DEG

st.set_page_config(page_title="VisuSpin — STMAS", page_icon="🌀", layout="wide")
page_header("Lesson 17: STMAS vs. MQMAS")
lesson_header(
    "Lesson 17 of 24",
    "MQMAS isn't the only way to remove residual quadrupolar broadening. What's the alternative, and its catch?",
    "Multiple-quantum excitation (Lesson 6) is inherently inefficient. Is there a way to get the "
    "same isotropic resolution without exciting a multiple-quantum coherence at all?",
)

st.markdown(
    f"""
{term("STMAS", "Satellite-Transition Magic-Angle Spinning: correlates a satellite transition (e.g. +1/2<->+3/2 for I=3/2) with the central transition, instead of a multiple-quantum coherence")}
(Gan, 2000) does exactly that — correlating a **satellite** transition with
the CT instead of a multiple-quantum coherence. No lossy MQ excitation step
means genuinely higher intrinsic sensitivity. So why isn't it used
everywhere instead of MQMAS?
"""
)

st.subheader("The central transition's one special property")
st.markdown(
    "Recall from Lesson 4: the central transition has **exactly zero first-order quadrupolar "
    "shift**, at *any* crystal orientation. A satellite transition doesn't share that property."
)
quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5 and n.is_half_integer_quadrupolar]
c1, c2 = st.columns([1, 1.4])
with c1:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    Cq_mhz = st.slider("Cq (MHz)", 0.5, 10.0, 3.0, 0.1)
    theta_deg = st.slider("Crystal orientation θ (deg)", 0, 90, 30, 1)
with c2:
    cos_t = np.cos(np.radians(theta_deg))
    ct_shift = satellite_first_order_shift_hz(nuc.spin, Cq_mhz * 1e6, m_upper=0.5, cos_theta=cos_t)
    sat_shift = satellite_first_order_shift_hz(nuc.spin, Cq_mhz * 1e6, m_upper=nuc.spin, cos_theta=cos_t)
    st.metric("CT first-order shift", f"{ct_shift:.1f} Hz")
    st.metric(f"Outermost satellite (m={nuc.spin:.1f}) first-order shift", f"{sat_shift:.0f} Hz")

st.subheader("What happens when the spinning angle isn't perfect")
with predict_then_reveal("If the spinning axis is off by a fraction of a degree from 54.74°, does this matter more for MQMAS (built on the CT) or STMAS (built on satellites)?"):
    errors = np.linspace(0, 0.3, 60)
    residual_sat = satellite_residual_vs_angle_error(nuc.spin, Cq_mhz * 1e6, cos_t, errors, m_upper=nuc.spin)
    residual_ct = satellite_residual_vs_angle_error(nuc.spin, Cq_mhz * 1e6, cos_t, errors, m_upper=0.5)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.plot(errors, np.abs(residual_sat), color="#c05621", label="STMAS (satellite transition)")
    ax.plot(errors, np.abs(residual_ct), color="#5b46e5", label="MQMAS (central transition)")
    ax.set_xlabel("Spinning-angle error from 54.7356° (deg)"); ax.set_ylabel("Residual shift (Hz)")
    ax.legend()
    st.pyplot(fig); plt.close(fig)
    st.write(
        f"Much more for STMAS. Its residual grows essentially linearly with angle error, reaching "
        f"{abs(residual_sat[-1]):.0f} Hz at just {errors[-1]:.2f}° off — while MQMAS's CT-based "
        f"coherence stays at exactly zero regardless of the angle. This is the entire reason STMAS "
        f"demands the most precisely set magic angle of any common MAS experiment."
    )

key_takeaway(
    "STMAS and MQMAS solve the same problem (residual 2nd-order quadrupolar broadening) with "
    "opposite tradeoffs: STMAS skips lossy multiple-quantum excitation for better raw sensitivity, "
    "at the cost of extreme sensitivity to the spinning angle itself; MQMAS accepts the MQ "
    "excitation penalty in exchange for total immunity to angle-setting error, since both "
    "coherences it uses have zero first-order shift by construction."
)

next_lesson("Lesson 18 — PASS/TOSS Sideband Separation", "pages/18_PASS_TOSS.py")

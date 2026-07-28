import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.quadrupole import satellite_pattern, ct_powder_pattern, ct_second_order_shift_hz

st.set_page_config(page_title="VisuSpin — Quadrupolar Interactions", page_icon="📈", layout="wide")
page_header("Lesson 4: Quadrupolar Interactions")
lesson_header(
    "Lesson 4 of 11",
    "Why do spectra of 23Na, 27Al, 11B and friends look so much messier than 1H or 13C?",
    "1H and 13C are spin-1/2. But most of the periodic table's NMR-active nuclei — including "
    "some of the most chemically important ones — aren't. What's actually different about them?",
)

quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5]
st.markdown(
    """
A spin-1/2 nucleus is a perfect little sphere of charge — no matter which
way you look at it, it looks the same. Nuclei with spin **greater than 1/2**
aren't: their charge distribution is slightly egg-shaped (a nonzero
**electric quadrupole moment**), and that shape interacts with the electric
field gradient created by surrounding electrons and atoms. That's an
entirely new interaction, with no analogue at all for 1H or 13C — and it
makes a spin-I nucleus have not one transition to observe, but 2I of them.
"""
)

st.subheader("1. First order: satellite transitions appear — but what about the one we usually observe?")
c1, c2 = st.columns([1, 1.5])
with c1:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    Cq_mhz = st.slider("Cq (MHz)", 0.1, 15.0, 2.0, 0.1)
    st.caption(f"{nuc.formatted_symbol()}: I = {nuc.spin_label()} → {int(2*nuc.spin)} allowed transitions")
with c2:
    sat = satellite_pattern(nuc.spin, Cq_mhz * 1e6)
    fig0, ax0 = plt.subplots(figsize=(6.5, 3))
    ax0.plot(sat["freq_hz"] / 1000, sat["intensity"], color="#805ad5")
    ax0.axvline(0, color="#5b46e5", linewidth=2, label="central transition (+1/2 ↔ -1/2)")
    ax0.set_xlabel("Frequency (kHz, relative to the central transition)"); ax0.set_ylabel("Intensity"); ax0.legend()
    st.pyplot(fig0); plt.close(fig0)

with predict_then_reveal("The satellite transitions clearly spread out over hundreds of kHz. Does that same first-order broadening affect the central (+1/2↔-1/2) transition too?"):
    b0_check = st.slider("B0 for this check (T)", 1.0, 20.0, 9.4, 0.1, key="b0_check")
    nu0_check = nu0_hz(nuc, b0_check)
    shift_0 = ct_second_order_shift_hz(nuc.spin, Cq_mhz * 1e6, 0.0, 0.0, 0.0, nu0_check)
    shift_90 = ct_second_order_shift_hz(nuc.spin, Cq_mhz * 1e6, 0.0, np.pi / 2, 0.0, nu0_check)
    st.markdown(
        f"""
        No — remarkably, the central transition has **exactly zero first-order shift**, at
        every orientation. All that first-order broadening you see above only ever affects the
        satellites. If quadrupolar coupling only had a first-order effect, ²³Na and ²⁷Al spectra
        would look just as sharp as ¹H's, once you only look at the central line.

        So why are quadrupolar central-transition spectra still broad in practice? A **second-order**
        effect: at θ=0° the shift is {shift_0:.1f} Hz, at θ=90° it's {shift_90:.1f} Hz — small,
        but *not zero*, and it depends on orientation just like CSA.
        """
    )

st.subheader("2. Second order: the central transition's real lineshape")
c3, c4 = st.columns([1, 1.5])
with c3:
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    eta_q = st.slider("Asymmetry η", 0.0, 1.0, 0.2, 0.01)
    nu0 = nu0_hz(nuc, b0)
with c4:
    ctpat = ct_powder_pattern(nuc.spin, Cq_mhz * 1e6, eta_q, nu0)
    fig1, ax1 = plt.subplots(figsize=(6.5, 3.2))
    ax1.plot(ctpat["freq_hz"], ctpat["intensity"], color="#2f855a")
    ax1.set_xlabel("Frequency (Hz, from the unperturbed CT)"); ax1.set_ylabel("Intensity")
    st.pyplot(fig1); plt.close(fig1)

with predict_then_reveal("Try dragging B0 up. Does the second-order pattern get narrower or wider at higher field?"):
    ctpat_2x = ct_powder_pattern(nuc.spin, Cq_mhz * 1e6, eta_q, nu0_hz(nuc, b0 * 2))
    span_1x = np.ptp(ctpat["freq_hz"][ctpat["intensity"] > 0.05]) if (ctpat["intensity"] > 0.05).any() else 0
    span_2x = np.ptp(ctpat_2x["freq_hz"][ctpat_2x["intensity"] > 0.05]) if (ctpat_2x["intensity"] > 0.05).any() else 0
    fig2, ax2 = plt.subplots(figsize=(6.5, 3))
    ax2.plot(ctpat["freq_hz"], ctpat["intensity"], color="#2f855a", label=f"{b0:.1f} T")
    ax2.plot(ctpat_2x["freq_hz"], ctpat_2x["intensity"], color="#c05621", label=f"{2*b0:.1f} T")
    ax2.set_xlabel("Frequency (Hz)"); ax2.legend()
    st.pyplot(fig2); plt.close(fig2)
    st.write(
        f"**Narrower** — roughly half the width ({span_1x:.0f} Hz → {span_2x:.0f} Hz). "
        "The second-order shift scales as Cq²/ν0, so doubling the field halves it. This is the "
        "opposite of CSA (whose *fractional*, ppm-based shift gives a *larger* absolute linewidth "
        "at higher field) — it's exactly why quadrupolar nuclei are often studied at the highest "
        "field magnets available."
    )

key_takeaway(
    "Quadrupolar nuclei have TWO separate complications: a first-order effect that spreads "
    "satellite transitions over a huge range but leaves the central transition untouched, and a "
    "second-order effect that broadens the central transition itself and — unusually — shrinks "
    "at higher magnetic field. Both survive fast MAS (unlike CSA), which is exactly the problem "
    "the next two lessons take on."
)

next_lesson("Lesson 5 — Magic-Angle Spinning", "pages/5_Magic_Angle_Spinning.py")

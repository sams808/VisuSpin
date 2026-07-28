import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES
from visuspin.physics.dipolar import dipolar_coupling_hz, dipolar_splitting_hz, pake_pattern

st.set_page_config(page_title="VisuSpin — Dipolar Coupling", page_icon="📈", layout="wide")
page_header("Lesson 3: Dipolar Coupling")
lesson_header(
    "Lesson 3 of 11",
    "Two nearby nuclei act like tiny bar magnets. What does that do to each other's spectrum?",
    "A bonded ¹H and ¹³C sit only ~1 Å apart. Each is a tiny magnet, and each one sits inside "
    "the magnetic field its neighbor creates — on top of B0. What effect does that have?",
)

st.markdown(
    f"""
Every nucleus with spin generates its own small magnetic field, exactly like
a bar magnet. A neighboring nucleus feels both B0 *and* this extra field from
its partner — and just like CSA, the size of that extra field depends on
**orientation**: specifically, the angle θ between the I-S internuclear
vector and B0. This is the {term("dipolar coupling", "direct, through-space magnetic coupling between two nuclei")},
and unlike CSA it needs *two* nuclei to talk about at all.
"""
)

st.subheader("1. One orientation, one pair, one splitting")
st.markdown("A single I-S pair at a fixed orientation gives not one line, but a **doublet** — the S spin's frequency shifts one way if its I partner is 'up', the other way if 'down'.")
c1, c2 = st.columns([1, 1.5])
with c1:
    symbol_i = st.selectbox("Spin I", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("1H"), key="dip_i")
    symbol_s = st.selectbox("Spin S", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("13C"), key="dip_s")
    r_ang = st.slider("I-S distance (Å)", 0.9, 5.0, 1.1, 0.05)
    theta_deg = st.slider("Orientation θ (deg, I-S vector to B0)", 0, 180, 0, 1)
    d_hz = dipolar_coupling_hz(NUCLIDES[symbol_i].gamma, NUCLIDES[symbol_s].gamma, r_ang)
    st.metric("Dipolar coupling D", f"{d_hz:.0f} Hz")
with c2:
    split = dipolar_splitting_hz(np.array([np.cos(np.radians(theta_deg))]), d_hz)[0]
    freqs = np.linspace(-abs(d_hz) * 1.3 - 5, abs(d_hz) * 1.3 + 5, 400)
    doublet = np.exp(-((freqs - split) ** 2) / (2 * (d_hz * 0.01 + 3) ** 2)) + \
              np.exp(-((freqs + split) ** 2) / (2 * (d_hz * 0.01 + 3) ** 2))
    fig0, ax0 = plt.subplots(figsize=(6, 3))
    ax0.plot(freqs, doublet, color="#f0a83c")
    ax0.set_xlabel("Frequency (Hz)"); ax0.set_ylabel("Intensity")
    ax0.set_title(f"Doublet at ±{abs(split):.0f} Hz, θ={theta_deg}°")
    st.pyplot(fig0); plt.close(fig0)

with predict_then_reveal("Distance matters a lot for a direct dipole-dipole interaction. If you double the I-S distance, does the coupling halve, quarter, or drop to 1/8?"):
    d_half_r = dipolar_coupling_hz(NUCLIDES[symbol_i].gamma, NUCLIDES[symbol_s].gamma, r_ang * 2)
    st.write(
        f"At {r_ang:.2f} Å, D = {d_hz:.0f} Hz. At {2*r_ang:.2f} Å, D = {d_half_r:.0f} Hz — "
        f"exactly **1/8**, because D scales as 1/r³. This is why dipolar couplings are such a "
        f"sensitive, precise ruler for measuring atomic distances in solids: a small distance "
        f"change gives a large, easily measured coupling change."
    )

st.subheader("2. The powder average: the Pake pattern")
st.markdown("Average over every crystallite orientation, and the doublets from every θ overlap into the classic **Pake pattern**.")
pat = pake_pattern(d_hz)
fig1, ax1 = plt.subplots(figsize=(7, 3.2))
ax1.plot(pat["freq_hz"], pat["intensity"], color="#5b46e5")
ax1.axvline(d_hz / 2, color="gray", linestyle="--", linewidth=1)
ax1.axvline(-d_hz / 2, color="gray", linestyle="--", linewidth=1)
ax1.set_xlabel("Frequency (Hz)"); ax1.set_ylabel("Intensity")
ax1.set_title("Pake pattern: horns at ±D/2 (θ=90°), shoulders at ±D (θ=0°)")
st.pyplot(fig1); plt.close(fig1)

key_takeaway(
    "The tall 'horns' come from θ=90° orientations — not because they have the largest "
    "splitting, but because (just like in the CSA lesson) far more of the sphere's area sits "
    "near the equator. There's a special angle, θ=54.74° (cos²θ=1/3), where the splitting "
    "vanishes completely — the same 'magic angle' that shows up for CSA too. That's not a "
    "coincidence, and it's exactly what the next two lessons build on."
)

next_lesson("Lesson 4 — Quadrupolar Interactions", "pages/4_Quadrupolar_Interactions.py")

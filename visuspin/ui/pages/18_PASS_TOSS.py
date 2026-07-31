import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.sidebands import mas_sideband_spectrum

st.set_page_config(page_title="VisuSpin — PASS/TOSS", page_icon="🧹", layout="wide")
page_header("Lesson 18: PASS/TOSS Sideband Separation")
lesson_header(
    "Lesson 18 of 24",
    "Several overlapping sites, each with its own sidebands. How do you untangle which sideband belongs to which site?",
    "Spinning faster always works in principle (Lesson 5), but for a large anisotropy that can "
    "mean speeds beyond what the probe or sample can handle. Is there another way?",
)

st.markdown(
    f"""
{term("TOSS", "Total Suppression Of Spinning sidebands: a rotor-synchronized pulse sequence whose net effect is to fold every sideband's intensity back into the centreband")}
and its more general cousin {term("PASS", "Phase-Adjusted Spinning Sidebands: separates each sideband order into its own sub-spectrum instead of collapsing them")}
solve exactly this problem — not by spinning faster, but by using rotor-
synchronized pulses that manipulate sideband phase. This lesson shows the
practical **outcome** (before vs. after), not a simulation of the pulse-timing
mechanism itself.
"""
)

st.subheader("Two overlapping sites, moderate spinning speed")
c1, c2 = st.columns(2)
with c1:
    aniso_a = st.slider("Site A anisotropy (Hz)", 500.0, 10000.0, 3000.0, 100.0)
    shift_a = st.slider("Site A isotropic shift (Hz)", -3000.0, 3000.0, -1500.0, 50.0)
with c2:
    aniso_b = st.slider("Site B anisotropy (Hz)", 500.0, 10000.0, 6000.0, 100.0)
    shift_b = st.slider("Site B isotropic shift (Hz)", -3000.0, 3000.0, 1500.0, 50.0)
mas_khz = st.slider("MAS rate (kHz)", 1.0, 15.0, 4.0, 0.5)

with predict_then_reveal("With two sites of different anisotropy spinning at a moderate rate, will their sidebands overlap in a confusing way?"):
    spec_a = mas_sideband_spectrum(aniso_a, eta=0.2, nu_rot_hz=mas_khz * 1000, n_powder=250, n_periods=32, n_time_per_period=32)
    spec_b = mas_sideband_spectrum(aniso_b, eta=0.2, nu_rot_hz=mas_khz * 1000, n_powder=250, n_periods=32, n_time_per_period=32)
    freq = spec_a["freq_hz"]
    raw = np.interp(freq, spec_a["freq_hz"] + shift_a, spec_a["intensity"], left=0, right=0) + \
          np.interp(freq, spec_b["freq_hz"] + shift_b, spec_b["intensity"], left=0, right=0)
    fig1, ax1 = plt.subplots(figsize=(8, 3.4))
    ax1.plot(freq, raw, color="#c05621")
    ax1.axvline(shift_a, color="#5b46e5", linestyle=":", linewidth=1)
    ax1.axvline(shift_b, color="#2f855a", linestyle=":", linewidth=1)
    ax1.set_xlabel("Frequency (Hz)"); ax1.set_ylabel("Intensity")
    ax1.set_title("Raw MAS spectrum: which peaks are sidebands, and of which site?")
    st.pyplot(fig1); plt.close(fig1)
    st.write(
        "Very often, yes — a sideband of the broader site can sit right on top of the narrower "
        "site's isotropic peak, or on one of its own sidebands, with no way to tell from a single "
        "spectrum which is which."
    )

st.subheader("After TOSS: only the true isotropic peaks remain")
total_area_a = spec_a["intensity"].sum()
total_area_b = spec_b["intensity"].sum()
fig2, ax2 = plt.subplots(figsize=(8, 3.0))
narrow = 15.0
gauss_a = total_area_a * np.exp(-((freq - shift_a) ** 2) / (2 * narrow ** 2))
gauss_b = total_area_b * np.exp(-((freq - shift_b) ** 2) / (2 * narrow ** 2))
combined = gauss_a + gauss_b
ax2.plot(freq, combined / combined.max(), color="#5b46e5")
ax2.set_xlabel("Frequency (Hz)"); ax2.set_ylabel("Intensity")
ax2.set_title("TOSS-processed: same total area per site, all folded into the centreband")
st.pyplot(fig2); plt.close(fig2)

key_takeaway(
    "PASS/TOSS trade extra experiment time (a rotor-synchronized pulse train, or several summed "
    "acquisitions) for a spectrum where every peak is a genuine isotropic shift — removing the "
    "'is this a sideband, and whose?' ambiguity that gets worse the more overlapping sites and "
    "the more different their anisotropies are."
)

next_lesson("Lesson 19 — Variable-Temperature NMR", "pages/19_Variable_Temperature_NMR.py")

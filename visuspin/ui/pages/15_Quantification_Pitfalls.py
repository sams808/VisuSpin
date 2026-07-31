import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.cp import cp_buildup_curve
from visuspin.physics.sidebands import mas_sideband_spectrum
from visuspin.physics.quantification import saturation_recovery_signal

st.set_page_config(page_title="VisuSpin — Quantification Pitfalls", page_icon="⚖️", layout="wide")
page_header("Lesson 15: Quantification Pitfalls")
lesson_header(
    "Lesson 15 of 24",
    "One peak is twice as tall as another. Is there twice as much of that site?",
    "Not necessarily. Three completely different, everyday experimental choices can each make "
    "peak height/area disagree with true population — and all three are easy to miss.",
)

st.subheader("1. Cross-polarization is not quantitative")
st.markdown(
    f"""
{term("CP", "cross-polarization: transferring magnetization from an abundant spin (1H) to a dilute one (13C, 29Si...) to boost signal")}
builds up at a rate set by each site's own T_IS (transfer time) and T1ρ —
which differ between chemically distinct sites. Two sites with **equal true
population** can show very different CP-enhanced intensity at the same
contact time.
"""
)
c1, c2 = st.columns([1, 1.6])
with c1:
    t_is_a = st.slider("Site A: T_IS (ms)", 0.1, 10.0, 0.5, 0.1)
    t1rho_a = st.slider("Site A: T1ρ_I (ms)", 1.0, 30.0, 12.0, 0.5)
    t_is_b = st.slider("Site B: T_IS (ms)", 0.1, 10.0, 4.0, 0.1)
    t1rho_b = st.slider("Site B: T1ρ_I (ms)", 1.0, 30.0, 8.0, 0.5)
    contact = st.slider("Contact time used (ms)", 0.1, 15.0, 2.0, 0.1)
with c2:
    curve_a = cp_buildup_curve(t_is_a, t1rho_a, contact_max_ms=15, n_points=300)
    curve_b = cp_buildup_curve(t_is_b, t1rho_b, contact_max_ms=15, n_points=300)
    sig_a = np.interp(contact, curve_a["t_ms"], curve_a["m_s"])
    sig_b = np.interp(contact, curve_b["t_ms"], curve_b["m_s"])
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(curve_a["t_ms"], curve_a["m_s"], color="#5b46e5", label=f"Site A (T_IS={t_is_a} ms)")
    ax.plot(curve_b["t_ms"], curve_b["m_s"], color="#c05621", label=f"Site B (T_IS={t_is_b} ms)")
    ax.axvline(contact, color="gray", linestyle="--", linewidth=1)
    ax.scatter([contact, contact], [sig_a, sig_b], color=["#5b46e5", "#c05621"], zorder=5)
    ax.set_xlabel("Contact time (ms)"); ax.set_ylabel("CP signal"); ax.legend()
    st.pyplot(fig); plt.close(fig)
    st.metric("Apparent A:B ratio at this contact time (true ratio is 1:1)", f"{sig_a/max(sig_b,1e-6):.2f} : 1")

with predict_then_reveal("Is there a single contact time that would make both sites read out correctly, regardless of their T_IS/T1rho?"):
    st.write(
        "No single contact time works in general — each site's buildup curve peaks at its own "
        "optimum, and a delay that's optimal for one site is rarely optimal for another. This is "
        "exactly why CP-MAS is treated as **qualitative/semi-quantitative** unless independently "
        "calibrated (e.g. against direct-excitation spectra) for the specific sites involved."
    )

st.subheader("2. Recycle delays: T1 saturation")
st.markdown(
    "Between scans, magnetization only recovers by 1 − exp(−recycle_delay / T1). Two sites with "
    "**equal true population** but different T1 will show different signal if the recycle delay "
    "isn't long enough for both."
)
c3, c4 = st.columns([1, 1.6])
with c3:
    t1_fast = st.slider("Site A: T1 (ms)", 10.0, 2000.0, 200.0, 10.0)
    t1_slow = st.slider("Site B: T1 (ms)", 10.0, 5000.0, 3000.0, 10.0)
    recycle = st.slider("Recycle delay used (ms)", 10.0, 5000.0, 500.0, 10.0)
with c4:
    delays = np.linspace(0, max(t1_fast, t1_slow) * 5, 300)
    rec_a = saturation_recovery_signal(delays, t1_fast)
    rec_b = saturation_recovery_signal(delays, t1_slow)
    sig_rec_a = saturation_recovery_signal(recycle, t1_fast)
    sig_rec_b = saturation_recovery_signal(recycle, t1_slow)
    fig2, ax2 = plt.subplots(figsize=(6.5, 3.6))
    ax2.plot(delays, rec_a, color="#5b46e5", label=f"Site A (T1={t1_fast:.0f} ms)")
    ax2.plot(delays, rec_b, color="#c05621", label=f"Site B (T1={t1_slow:.0f} ms)")
    ax2.axvline(recycle, color="gray", linestyle="--", linewidth=1)
    ax2.scatter([recycle, recycle], [sig_rec_a, sig_rec_b], color=["#5b46e5", "#c05621"], zorder=5)
    ax2.set_xlabel("Recycle delay (ms)"); ax2.set_ylabel("Available signal fraction"); ax2.legend()
    st.pyplot(fig2); plt.close(fig2)
    st.metric("Apparent A:B ratio at this recycle delay (true ratio is 1:1)", f"{sig_rec_a/max(sig_rec_b,1e-6):.2f} : 1")

with predict_then_reveal("What rule of thumb for recycle delay (in terms of T1) keeps this bias below ~1%?"):
    st.write(
        f"Recycle delay ≥ 5×T1 gives 1-exp(-5) = {1-np.exp(-5):.4f} ≈ 99.3% recovery — the standard "
        "'5×T1' rule. For a sample with several sites, that means 5× the **longest** T1 among them, "
        "which for some quadrupolar nuclei in crystalline (non-glassy) environments can be minutes long."
    )

st.subheader("3. Spinning sidebands: don't just look at the centreband")
st.markdown(
    "At a finite MAS rate, some intensity moves from the centreband into sidebands (Lesson 5). "
    "Two sites with **equal true population** but different anisotropy redistribute a different "
    "fraction of their intensity — so comparing centreband heights alone is biased."
)
c5, c6 = st.columns([1, 1.6])
with c5:
    aniso_a = st.slider("Site A: anisotropy (Hz)", 200.0, 15000.0, 1000.0, 100.0)
    aniso_b = st.slider("Site B: anisotropy (Hz)", 200.0, 15000.0, 8000.0, 100.0)
    mas_rate = st.slider("MAS rate (kHz)", 1.0, 30.0, 5.0, 0.5)
with c6:
    spec_a = mas_sideband_spectrum(aniso_a, eta=0.0, nu_rot_hz=mas_rate * 1000, normalize=False,
                                      n_powder=250, n_periods=32, n_time_per_period=32)
    spec_b = mas_sideband_spectrum(aniso_b, eta=0.0, nu_rot_hz=mas_rate * 1000, normalize=False,
                                      n_powder=250, n_periods=32, n_time_per_period=32)
    fig3, ax3 = plt.subplots(figsize=(6.5, 3.6))
    ax3.plot(spec_a["freq_hz"], spec_a["intensity"], color="#5b46e5", label=f"Site A (Δδ={aniso_a:.0f} Hz)")
    ax3.plot(spec_b["freq_hz"], spec_b["intensity"], color="#c05621", label=f"Site B (Δδ={aniso_b:.0f} Hz)")
    ax3.set_xlabel("Frequency (Hz)"); ax3.set_ylabel("Raw intensity (equal population)"); ax3.legend()
    st.pyplot(fig3); plt.close(fig3)
    peak_a, peak_b = spec_a["intensity"].max(), spec_b["intensity"].max()
    total_a, total_b = spec_a["intensity"].sum(), spec_b["intensity"].sum()
    st.metric("Centreband-only A:B ratio (true ratio is 1:1)", f"{peak_a/max(peak_b,1e-9):.2f} : 1")
    st.metric("Total-integrated-area A:B ratio", f"{total_a/max(total_b,1e-9):.2f} : 1")

with predict_then_reveal("Which of the two ratios above should be much closer to the true 1:1?"):
    st.write(
        "The **total-integrated-area** ratio — summing the centreband and every sideband recovers "
        "the true population ratio (up to simulation noise), while comparing centreband heights "
        "alone is exactly as biased as the raw spectra above look."
    )

key_takeaway(
    "All three pitfalls share the same root cause: some step between 'true population' and "
    "'observed intensity' depends on a site-specific physical constant (T_IS/T1ρ, T1, or "
    "anisotropy) rather than population alone. The fix is always the same in spirit — either "
    "remove the dependence experimentally (long recycle delays, direct excitation, full sideband "
    "integration) or calibrate it out with independent measurements or fitting (Lesson 23)."
)

next_lesson("Lesson 16 — DQ-SQ Homonuclear Correlation", "pages/16_DQ_SQ_Correlation.py")

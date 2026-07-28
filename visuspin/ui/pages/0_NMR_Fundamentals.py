import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics import bloch

st.set_page_config(page_title="VisuSpin — NMR Fundamentals", page_icon="🧲", layout="wide")
page_header("Lesson 0: NMR Fundamentals")
lesson_header(
    "Lesson 0 of 11 — start here",
    "How does NMR 'see' inside matter without touching it?",
    "A magnet, a radio pulse, and a receiver coil are the entire hardware. "
    "What is physically happening to the atoms in between?",
)

st.markdown(
    """
Many atomic nuclei — ¹H, ¹³C, ¹⁹F, ²⁷Al, and dozens more — carry a quantum
property called **spin**, which makes each one behave like an
infinitesimally small bar magnet. In an ordinary sample, billions of these
tiny magnets point in every random direction and cancel out completely: no
net magnetism, nothing to detect.

Put the sample inside a strong magnet, though, and something changes.
"""
)

st.subheader("1. Equilibrium magnetization")
st.markdown(
    f"""
A tiny excess of the nuclear magnets — a fraction of a percent — settles
into alignment with the external field, which every NMR paper calls
{term("B0", "the static external magnetic field, conventionally drawn along the vertical z-axis")}.
That tiny excess adds up, over the ~10²⁰ nuclei in even a small sample, to a
measurable net **magnetization vector**, M — the single arrow every plot in
VisuSpin is built around. At equilibrium, M just sits there, pointing along
B0. Nothing detectable happens yet; a receiver coil only picks up a
*changing* magnetic field, and a static arrow doesn't change.
"""
)
fig0, ax0 = plt.subplots(figsize=(3.2, 3.2), subplot_kw={"projection": "3d"})
ax0.plot([0, 0], [0, 0], [-1, 1], color="lightgray", linestyle="--", linewidth=1)
ax0.plot([0, 0], [0, 0], [0, 1], color="#5b46e5", linewidth=3.5)
ax0.text(0.05, 0, 1.05, "M (= B0 direction)", fontsize=8)
ax0.set_xlim(-1, 1); ax0.set_ylim(-1, 1); ax0.set_zlim(-1, 1)
ax0.set_xlabel("x"); ax0.set_ylabel("y"); ax0.set_zlabel("z")
st.pyplot(fig0); plt.close(fig0)

st.subheader("2. Precession: tip it, and it spins")
st.markdown(
    f"""
Nudge M away from the z-axis — we'll see exactly how in a moment — and it
doesn't simply relax back along the shortest path. It **precesses**: it
sweeps around B0 like a spinning top wobbling around the direction of
gravity instead of just tipping over. The rate of this precession is the
{term("Larmor frequency", "ν0 = γB0 / 2π, where γ (gamma) is a fixed constant of the nucleus, its gyromagnetic ratio")} —
different for every nuclide, and proportional to how strong B0 is.
"""
)

col1, col2 = st.columns([1, 1.4])
with col1:
    symbol = st.selectbox("Nuclide", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("1H"))
    nuc = NUCLIDES[symbol]
    b0 = st.slider("B0 (T) — for reference, hospital MRI scanners use 1.5-3 T", 1.0, 20.0, 9.4, 0.1)
    nu0 = nu0_hz(nuc, b0)
    st.metric(f"{nuc.formatted_symbol()} Larmor frequency", f"{nu0/1e6:.1f} MHz")
    t_snap = st.slider("Time (arbitrary units — watch M sweep around)", 0.0, 1.0, 0.0, 0.02)

with col2:
    ens = bloch.Ensemble.from_gaussian_offsets(1, 0.0, seed=1)
    bloch.apply_pulse(ens, 90, 0.0, 500, "hard")
    demo_omega = 2 * np.pi * 3  # 3 full turns over the slider's [0,1] range, purely illustrative
    theta = demo_omega * t_snap
    mx, my, mz = np.cos(theta), -np.sin(theta), 0.0
    fig1, ax1 = plt.subplots(figsize=(4, 4), subplot_kw={"projection": "3d"})
    ax1.plot([0, 0], [0, 0], [-1, 1], color="lightgray", linestyle="--", linewidth=1)
    u, v = np.linspace(0, 2 * np.pi, 40), 0
    ax1.plot(np.cos(u), np.sin(u), np.zeros_like(u), color="lightgray", linewidth=0.6)
    ax1.plot([0, mx], [0, my], [0, mz], color="#5b46e5", linewidth=3.5)
    ax1.set_xlim(-1, 1); ax1.set_ylim(-1, 1); ax1.set_zlim(-1, 1)
    ax1.set_title(f"M precessing in the transverse plane\n(illustrative rate, not {nu0/1e6:.0f} MHz — that's far too fast to animate with a slider!)", fontsize=8)
    st.pyplot(fig1); plt.close(fig1)

with predict_then_reveal("If you double B0, does the precession *rate* double, halve, or stay the same?"):
    nu0_double = nu0_hz(nuc, b0 * 2)
    st.write(
        f"At {b0:.1f} T, {nuc.formatted_symbol()} precesses at {nu0/1e6:.1f} MHz. "
        f"At {2*b0:.1f} T, it precesses at {nu0_double/1e6:.1f} MHz — **exactly double**, "
        f"because ν0 = γB0/2π is directly proportional to B0. This is the entire reason MRI "
        f"and NMR labs chase higher-field magnets: more signal, more resolution, all from a "
        f"straightforwardly linear relationship."
    )

key_takeaway(
    "Every nucleus precesses around B0 at its own fixed rate (the Larmor frequency), "
    "set only by which nuclide it is and how strong B0 is. Nothing about the sample's "
    "chemistry has entered yet — that comes later, as tiny *shifts* away from this base rate."
)

st.subheader("3. RF pulses: how we tip M in the first place")
st.markdown(
    """
To tip M away from equilibrium, we broadcast a short burst of radio-frequency
energy at exactly the Larmor frequency — resonance, the same principle as
pushing a swing in time with its natural rhythm to build up amplitude
efficiently. A brief, precisely-timed pulse tips M by a chosen **flip
angle**: a *90° pulse* rotates M fully into the transverse (xy) plane, where
it produces the maximum possible signal; a *180° pulse* inverts it
completely, from +z to −z.
"""
)
flip = st.slider("Flip angle (degrees)", 0, 360, 90, 15)
ens2 = bloch.Ensemble.from_gaussian_offsets(1, 0.0, seed=2)
bloch.apply_pulse(ens2, flip, 0.0, 500, "hard")
fig2, ax2 = plt.subplots(figsize=(3.5, 3.5), subplot_kw={"projection": "3d"})
ax2.plot([0, 0], [0, 0], [-1, 1], color="lightgray", linestyle="--", linewidth=1)
ax2.plot([0, 0], [0, 1], [0, 0], color="lightgray", linewidth=0.6)
ax2.plot([0, ens2.mx[0]], [0, ens2.my[0]], [0, ens2.mz[0]], color="#5b46e5", linewidth=3.5)
ax2.set_xlim(-1, 1); ax2.set_ylim(-1, 1); ax2.set_zlim(-1, 1)
ax2.set_title(f"M after a {flip}° pulse")
st.pyplot(fig2); plt.close(fig2)

st.subheader("4. Relaxation and the FID")
st.markdown(
    f"""
Once M is tipped into the transverse plane, two things happen at once, on
their own separate timescales:

- It keeps precessing, inducing a real, measurable oscillating voltage in a
  receiver coil — this raw, decaying oscillation is the
  {term("FID", "Free Induction Decay — the raw time-domain NMR signal, before any processing")}.
- It decays: the transverse component shrinks with time constant
  {term("T2", "the transverse relaxation time — how fast the observable signal decays")},
  while the z-component regrows toward equilibrium with time constant
  {term("T1", "the longitudinal relaxation time — how fast equilibrium magnetization returns")}.
  These are usually very different numbers because they come from different
  physics: T2 is spins in the sample losing phase coherence *with each
  other*; T1 is the spin system trading energy with its surroundings to
  fully re-equilibrate.
"""
)
t2_ms = st.slider("T2 (ms)", 1.0, 200.0, 40.0, 1.0)
t_fid = np.linspace(0, 5 * t2_ms, 400)
fid = np.exp(-t_fid / t2_ms) * np.cos(2 * np.pi * 0.15 * t_fid)
fig3, ax3 = plt.subplots(figsize=(7, 2.6))
ax3.plot(t_fid, fid, color="#5b46e5")
ax3.set_xlabel("Time (ms)"); ax3.set_ylabel("Signal"); ax3.set_title("The FID (illustrative frequency, real T2)")
st.pyplot(fig3); plt.close(fig3)

st.subheader("5. From FID to spectrum: the Fourier transform")
st.markdown(
    """
Chemists don't want a signal in *time* — they want a **spectrum**: signal
versus *frequency*, because different chemical environments precess at
subtly different frequencies (the whole basis of chemical shift, coming in
the next lessons). The **Fourier transform** is the mathematical machine
that converts an oscillating, decaying time signal into a frequency-domain
peak. Try it below.
"""
)
with predict_then_reveal("If T2 gets shorter (faster-decaying FID), does the resulting peak get narrower or broader?"):
    fid_fast = np.exp(-t_fid / (t2_ms / 4)) * np.cos(2 * np.pi * 0.15 * t_fid)
    spec_slow = np.abs(np.fft.fftshift(np.fft.fft(fid)))
    spec_fast = np.abs(np.fft.fftshift(np.fft.fft(fid_fast)))
    freq = np.fft.fftshift(np.fft.fftfreq(len(t_fid), d=(t_fid[1] - t_fid[0])))
    fig4, ax4 = plt.subplots(figsize=(7, 2.8))
    ax4.plot(freq, spec_slow / spec_slow.max(), color="#5b46e5", label=f"T2={t2_ms:.0f} ms (slow decay)")
    ax4.plot(freq, spec_fast / spec_fast.max(), color="#c05621", label=f"T2={t2_ms/4:.0f} ms (fast decay)")
    ax4.set_xlim(-1, 1); ax4.set_xlabel("Frequency (arb. units)"); ax4.set_ylabel("Intensity"); ax4.legend()
    st.pyplot(fig4); plt.close(fig4)
    st.write("A faster-decaying FID gives a **broader** peak. A signal that lasts longer in time is more sharply defined in frequency.")

key_takeaway(
    "Time and frequency are two views of the same signal, and they trade off: short-lived "
    "signals give broad peaks, long-lived signals give narrow peaks. This single idea explains "
    "why every broadening mechanism in the rest of these lessons — faster relaxation, "
    "orientation spread, coupling — makes NMR peaks wider."
)

st.divider()
st.markdown(
    """
**You now have the full vocabulary this app runs on:** magnetization,
precession, the Larmor frequency, RF pulses and flip angles, T1/T2
relaxation, the FID, and the Fourier transform.

Everything from here on is really about *one* additional complication.
In a liquid, molecules tumble fast and randomly, so each nucleus feels an
*averaged* local environment — clean, sharp peaks. In a **solid**, molecules
are frozen in place, so each nucleus's local magnetic environment depends on
its fixed **orientation** relative to B0. Different crystallites, different
orientations, different frequencies — and that's what the rest of VisuSpin
is about untangling.
"""
)
next_lesson("Lesson 1 — Relaxation Explorer", "pages/1_Relaxation_Explorer.py")

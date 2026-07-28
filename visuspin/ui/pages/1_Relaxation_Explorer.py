import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics import bloch
from visuspin.sequences.blocks import SequenceContext
from visuspin.sequences.presets import hahn_echo, free_induction_decay
from visuspin.sequences.engine import run_sequence

st.set_page_config(page_title="VisuSpin — Relaxation Explorer", page_icon="🧲", layout="wide")
page_header("Lesson 1: Relaxation Explorer")
lesson_header(
    "Lesson 1 of 11",
    "Why does the same sample decay two different ways?",
    "If you just record an FID, the signal disappears in a few tens of milliseconds. "
    "But a clever trick called an echo can bring some of that 'lost' signal back. How?",
)

st.markdown(
    f"""
Lesson 0 showed a single, perfectly coherent spin decaying with one clean
time constant, {term("T2", "the true, irreversible transverse relaxation time")}.
Real samples aren't that tidy: every molecule sits in a very slightly
different local magnetic environment, so billions of individual spins all
precess at *very slightly* different rates. Let's watch what that does.
"""
)

st.subheader("1. A perfectly uniform sample")
st.markdown("With **no** spread in local fields, the FID decays cleanly at the true T2 — exactly like Lesson 0.")
T2_demo = st.slider("T2 (ms)", 5.0, 300.0, 60.0, 1.0, key="t2_demo")
ctx_uniform = SequenceContext(T1_ms=5000, T2_ms=T2_demo, nu1_khz=25)
out_uniform = run_sequence(free_induction_decay(acquire_ms=4 * T2_demo), ctx_uniform, n_isochromats=200, sigma_rad_per_ms=0.0)

st.subheader("2. A realistic sample: many spins, slightly different fields")
with predict_then_reveal("If we add a spread of local fields (inhomogeneous broadening), will the FID decay faster, slower, or the same as before?"):
    sigma = st.slider("Spread of local fields (rad/ms)", 0.0, 1.0, 0.3, 0.02, key="sigma_demo")
    out_inhom = run_sequence(free_induction_decay(acquire_ms=4 * T2_demo), ctx_uniform, n_isochromats=400, sigma_rad_per_ms=sigma)
    fig1, ax1 = plt.subplots(figsize=(7, 3))
    ax1.plot(out_uniform["t_ms"], out_uniform["mxy"], color="#5b46e5", label=f"uniform sample (pure T2={T2_demo:.0f} ms)")
    ax1.plot(out_inhom["t_ms"], out_inhom["mxy"], color="#c05621", label="realistic sample (with field spread)")
    ax1.set_xlabel("Time (ms)"); ax1.set_ylabel("|Mxy|"); ax1.legend()
    st.pyplot(fig1); plt.close(fig1)
    st.markdown(
        f"""
        Faster. Much faster. Different spins precess at different rates and rapidly fall out of
        step with each other — even though *no individual spin has actually relaxed yet*. The
        signal we observe from the whole ensemble just looks like it decayed, because the
        vector sum of many slightly-out-of-sync arrows shrinks toward zero. This apparent,
        faster decay constant is called {term("T2*", "the observed FID decay time; always <= T2, since it also includes reversible dephasing from field inhomogeneity")}.
        """
    )

st.subheader("3. The echo: can we get the 'lost' signal back?")
st.markdown(
    """
Here's the key question this lesson is building to. The dephasing in step 2
isn't random noise — every spin is still precessing at its own perfectly
well-defined (if slightly different) rate. That means it's **reversible**: a
180° pulse partway through effectively runs time backward for the
inhomogeneous part only. This is the **Hahn echo** (90° — wait τ — 180° —
wait τ — signal reappears).
"""
)
tau = st.slider("Echo delay τ (ms)", 2.0, 60.0, 15.0, 1.0)
ctx_echo = SequenceContext(T1_ms=5000, T2_ms=T2_demo, nu1_khz=25)
out_echo = run_sequence(hahn_echo(tau_ms=tau, acquire_ms=2), ctx_echo, n_isochromats=300, sigma_rad_per_ms=sigma)

with predict_then_reveal("At the moment the echo forms (t = 2τ), will its height follow the fast T2* decay, or the slower true-T2 decay?"):
    t_echo = 2 * tau
    pred_t2 = np.exp(-t_echo / T2_demo)
    t2star = 1 / (1 / T2_demo + sigma / 2) if sigma > 0 else T2_demo
    pred_t2star = np.exp(-t_echo / t2star)
    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.plot(out_echo["t_ms"], out_echo["mxy"], color="#5b46e5", label="Hahn echo sequence signal")
    ax2.axvline(t_echo, color="gray", linestyle="--", linewidth=1, label=f"echo forms at t=2τ={t_echo:.0f} ms")
    ax2.set_xlabel("Time (ms)"); ax2.set_ylabel("|Mxy|"); ax2.legend()
    st.pyplot(fig2); plt.close(fig2)
    echo_height = out_echo["mxy"][(out_echo["t_ms"] > t_echo - 2) & (out_echo["t_ms"] < t_echo + 2)].max()
    st.markdown(
        f"""
        The echo height ({echo_height:.3f}) sits on the **slow, true-T2 curve**
        (exp(−2τ/T2) = {pred_t2:.3f}), not the fast T2* curve
        (exp(−2τ/T2*) = {pred_t2star:.4f}, far smaller). The 180° pulse perfectly undoes
        the reversible field-inhomogeneity dephasing — every spin refocuses back in
        step — but it **cannot** undo true T2 relaxation, because that's spins
        randomly and irreversibly losing energy/coherence to their surroundings.
        There's no "backward" for a genuinely random process.
        """
    )

key_takeaway(
    "T2* (what a plain FID shows you) mixes together true relaxation AND reversible "
    "field-inhomogeneity dephasing. An echo strips the reversible part back out, revealing "
    "the true T2. This is why virtually every real solid-state NMR pulse sequence — including "
    "everything in the Pulse Sequence Composer lesson — is built around echoes, not plain FIDs."
)

st.divider()
st.subheader("Explore it yourself")
st.markdown("Now with the full picture: real nuclides, real field strengths, finite pulses, and sample spinning.")

with st.sidebar:
    st.subheader("Spin & field")
    symbol = st.selectbox("Nuclide", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("1H"))
    nuc = NUCLIDES[symbol]
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    nu0 = nu0_hz(nuc, b0)
    st.caption(f"{nuc.formatted_symbol()}: I={nuc.spin_label()}, ν0 = {nu0/1e6:.2f} MHz")

    st.subheader("Relaxation")
    T1 = st.slider("T1 (ms)", 1.0, 5000.0, 500.0, 1.0)
    T2 = st.slider("T2 (ms)", 0.1, 2000.0, 50.0, 0.1)
    linewidth_ppm = st.slider("Inhomogeneous linewidth (ppm)", 0.0, 50.0, 5.0, 0.1)

    st.subheader("Pulse")
    flip_deg = st.slider("Flip angle (deg)", 0, 360, 90, 1)
    nu1_khz = st.slider("RF field ν1 (kHz)", 1.0, 200.0, 50.0, 1.0)

    st.subheader("Sample spinning")
    mas_on = st.checkbox("Magic-angle spinning", value=False)
    mas_rate_khz = st.slider("MAS rate (kHz)", 1.0, 100.0, 20.0, 1.0) if mas_on else 0.0

    st.subheader("Display")
    n_iso = st.slider("Isochromats simulated", 50, 2000, 400, 50)
    n_shown = st.slider("Spins shown in vector plot", 1, 30, 10, 1)
    acquire_ms = st.slider("Acquisition window (ms)", 1.0, 500.0, min(200.0, 8 * T2), 1.0)

sigma_rad_per_ms = 2 * np.pi * (linewidth_ppm * 1e-6 * nu0) / 1000.0

rng_seed = 1234
ens_trace = bloch.Ensemble.from_gaussian_offsets(n_iso, sigma_rad_per_ms, seed=rng_seed)
bloch.apply_pulse(ens_trace, flip_deg, 0.0, nu1_khz, "hard", 1.0)
trace = bloch.run_free_precession(ens_trace, acquire_ms, T1, T2, mas_rate_khz, n_samples=max(400, int(acquire_ms * 4)))

t_snap = st.slider("Vector-plot snapshot time (ms)", 0.0, float(acquire_ms), 0.0, float(acquire_ms) / 200 or 0.01)
ens_snap = bloch.Ensemble.from_gaussian_offsets(n_iso, sigma_rad_per_ms, seed=rng_seed)
bloch.apply_pulse(ens_snap, flip_deg, 0.0, nu1_khz, "hard", 1.0)
n_sub = max(1, int(t_snap / max(acquire_ms, 1e-9) * 400))
dt_sub = t_snap / n_sub if n_sub > 0 else 0.0
t_cursor = 0.0
for _ in range(n_sub):
    bloch.step(ens_snap, dt_sub, t_cursor, T1, T2, mas_rate_khz)
    t_cursor += dt_sub

col1, col2 = st.columns([1, 1.3])

with col1:
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    u, v = np.linspace(0, 2 * np.pi, 30), np.linspace(0, np.pi, 15)
    xs = np.outer(np.cos(u), np.sin(v)); ys = np.outer(np.sin(u), np.sin(v)); zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color="lightgray", linewidth=0.4, alpha=0.5)
    idx = np.linspace(0, n_iso - 1, n_shown).astype(int)
    for i in idx:
        ax.plot([0, ens_snap.mx[i]], [0, ens_snap.my[i]], [0, ens_snap.mz[i]], color="#9aa0b4", linewidth=1.0)
    mx0, my0, mz0 = ens_snap.sum_m()
    ax.plot([0, mx0], [0, my0], [0, mz0], color="#5b46e5", linewidth=3.5)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title(f"Isochromats at t = {t_snap:.2f} ms")
    st.pyplot(fig)
    plt.close(fig)

with col2:
    fig2, axs = plt.subplots(2, 1, figsize=(6, 5.2), sharex=True)
    axs[0].plot(trace["t"], trace["mxy"], color="#5b46e5", label="|Mxy|")
    axs[0].plot(trace["t"], trace["mz"], color="#f0a83c", label="Mz")
    axs[0].axvline(t_snap, color="gray", linestyle="--", linewidth=1)
    axs[0].set_ylabel("Magnetisation"); axs[0].legend(loc="upper right"); axs[0].set_title("FID")

    signal = trace["mx"] + 1j * trace["my"]
    dt = trace["t"][1] - trace["t"][0] if len(trace["t"]) > 1 else 1.0
    spec = np.fft.fftshift(np.fft.fft(signal))
    freq_hz = np.fft.fftshift(np.fft.fftfreq(len(signal), d=dt / 1000.0))
    axs[1].plot(freq_hz, np.abs(spec), color="#2f855a")
    axs[1].set_xlabel("Frequency (Hz, offset from carrier)"); axs[1].set_ylabel("|FT(FID)|")
    axs[1].set_title("Spectrum" + (" (MAS sidebands visible if MAS rate < linewidth)" if mas_on else ""))
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

st.caption(
    "Simulation: exact per-isochromat Bloch stepping (visuspin.physics.bloch), Gaussian-distributed static offsets "
    "for the inhomogeneous linewidth, finite-duration pulses via the Rodrigues rotation formula. "
    "MAS uses a single-harmonic offset-modulation model (disclosed simplification, see bloch.step docstring)."
)
next_lesson("Lesson 2 — Chemical Shift Anisotropy", "pages/2_Chemical_Shift_Anisotropy.py")

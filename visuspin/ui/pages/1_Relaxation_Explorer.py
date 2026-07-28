import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics import bloch
from visuspin.physics.quadrupole import ct_selective_enhancement

st.set_page_config(page_title="VisuSpin — Relaxation Explorer", page_icon="🧲", layout="wide")
page_header("Relaxation Explorer", "T1 / T2 / T2* Bloch simulation with real nuclides, finite pulses, MAS and CT-selective excitation")

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
    ct_selective = st.checkbox("CT-selective excitation", value=False,
                                 help="Half-integer quadrupolar nuclei nutate (I+1/2) faster when the pulse only excites the central transition.")
    enhancement = (nuc.spin + 0.5) if (ct_selective and nuc.is_half_integer_quadrupolar) else 1.0

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
bloch.apply_pulse(ens_trace, flip_deg, 0.0, nu1_khz, "hard", enhancement)
trace = bloch.run_free_precession(ens_trace, acquire_ms, T1, T2, mas_rate_khz, n_samples=max(400, int(acquire_ms * 4)))

t_snap = st.slider("Vector-plot snapshot time (ms)", 0.0, float(acquire_ms), 0.0, float(acquire_ms) / 200 or 0.01)
ens_snap = bloch.Ensemble.from_gaussian_offsets(n_iso, sigma_rad_per_ms, seed=rng_seed)
bloch.apply_pulse(ens_snap, flip_deg, 0.0, nu1_khz, "hard", enhancement)
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

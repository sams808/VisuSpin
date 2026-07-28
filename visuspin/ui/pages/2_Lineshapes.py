import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.csa import csa_powder_pattern, principal_values
from visuspin.physics.dipolar import dipolar_coupling_hz, pake_pattern
from visuspin.physics.quadrupole import satellite_pattern, ct_powder_pattern
from visuspin.physics.sidebands import mas_sideband_spectrum

st.set_page_config(page_title="VisuSpin — Lineshapes", page_icon="📈", layout="wide")
page_header("Lineshapes", "Static and MAS powder patterns for the four interactions that shape a solid-state NMR spectrum")

tab_csa, tab_dip, tab_quad, tab_mas = st.tabs(["CSA", "Dipolar (Pake)", "Quadrupolar (1st & 2nd order)", "MAS sidebands"])

with tab_csa:
    c1, c2 = st.columns([1, 2])
    with c1:
        delta_iso = st.slider("δ_iso (ppm)", -200.0, 200.0, 0.0, 1.0, key="csa_iso")
        delta_aniso = st.slider("Anisotropy Δδ (ppm)", -300.0, 300.0, 100.0, 1.0, key="csa_aniso")
        eta_csa = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01, key="csa_eta")
        dzz, dxx, dyy = principal_values(delta_iso, delta_aniso, eta_csa)
        st.caption(f"Principal values: δzz={dzz:.1f}, δxx={dxx:.1f}, δyy={dyy:.1f} ppm")
    with c2:
        pat = csa_powder_pattern(delta_iso, delta_aniso, eta_csa)
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.plot(pat["shift"], pat["intensity"], color="#5b46e5")
        ax.set_xlabel("Chemical shift (ppm)"); ax.set_ylabel("Intensity"); ax.invert_xaxis()
        st.pyplot(fig); plt.close(fig)

with tab_dip:
    c1, c2 = st.columns([1, 2])
    with c1:
        symbol_i = st.selectbox("Spin I", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("1H"), key="dip_i")
        symbol_s = st.selectbox("Spin S", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("13C"), key="dip_s")
        r_ang = st.slider("I-S distance (Å)", 0.9, 5.0, 1.1, 0.05)
        d_hz = dipolar_coupling_hz(NUCLIDES[symbol_i].gamma, NUCLIDES[symbol_s].gamma, r_ang)
        st.caption(f"D = {d_hz:.0f} Hz")
    with c2:
        pat = pake_pattern(d_hz)
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.plot(pat["freq_hz"], pat["intensity"], color="#f0a83c")
        ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
        st.pyplot(fig); plt.close(fig)

with tab_quad:
    c1, c2 = st.columns([1, 2])
    with c1:
        quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5]
        symbol_q = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
        nucq = NUCLIDES[symbol_q]
        b0_q = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1, key="quad_b0")
        Cq_mhz = st.slider("Cq (MHz)", 0.0, 15.0, 2.0, 0.1)
        eta_q = st.slider("Asymmetry η", 0.0, 1.0, 0.2, 0.01, key="quad_eta")
        nu0_q = nu0_hz(nucq, b0_q)
        st.caption(f"{nucq.formatted_symbol()}: I={nucq.spin_label()}, ν0={nu0_q/1e6:.2f} MHz")
    with c2:
        st.markdown("**First-order satellite manifold** (static)")
        sat = satellite_pattern(nucq.spin, Cq_mhz * 1e6)
        fig1, ax1 = plt.subplots(figsize=(6, 2.6))
        ax1.plot(sat["freq_hz"] / 1000, sat["intensity"], color="#805ad5")
        ax1.set_xlabel("Frequency (kHz, from CT)"); ax1.set_ylabel("Intensity")
        st.pyplot(fig1); plt.close(fig1)

        st.markdown("**Second-order central-transition lineshape** (static, from first-principles perturbation theory)")
        ctpat = ct_powder_pattern(nucq.spin, Cq_mhz * 1e6, eta_q, nu0_q)
        fig2, ax2 = plt.subplots(figsize=(6, 2.6))
        ax2.plot(ctpat["freq_hz"], ctpat["intensity"], color="#2f855a")
        ax2.axvline(ctpat["isotropic_shift_hz"], color="gray", linestyle="--", linewidth=1)
        ax2.set_xlabel("Frequency (Hz, from unperturbed CT)"); ax2.set_ylabel("Intensity")
        st.caption(f"Isotropic 2nd-order shift: {ctpat['isotropic_shift_hz']:.1f} Hz (dashed line)")
        st.pyplot(fig2); plt.close(fig2)

with tab_mas:
    c1, c2 = st.columns([1, 2])
    with c1:
        delta_aniso_mas = st.slider("Anisotropy (Hz)", 100.0, 20000.0, 4000.0, 100.0, key="mas_aniso")
        eta_mas = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01, key="mas_eta")
        nu_rot_khz = st.slider("MAS rate (kHz)", 1.0, 100.0, 10.0, 1.0, key="mas_rate")
        st.caption("Simulated by direct numerical rotor-period tensor rotation, not Herzfeld–Berger coefficients (see sidebands.py docstring).")
    with c2:
        spec = mas_sideband_spectrum(delta_aniso_mas, eta_mas, nu_rot_khz * 1000)
        fig, ax = plt.subplots(figsize=(6, 3.4))
        ax.plot(spec["freq_hz"], spec["intensity"], color="#c05621")
        ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
        ax.set_title(f"Sidebands spaced at the MAS rate ({nu_rot_khz:.0f} kHz)")
        st.pyplot(fig); plt.close(fig)

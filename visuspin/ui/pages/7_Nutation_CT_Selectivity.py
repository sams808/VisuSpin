import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.nuclides import NUCLIDES
from visuspin.physics.quadrupole import ct_selective_enhancement, nutation_curve, satellite_pattern
from visuspin.physics import bloch

st.set_page_config(page_title="VisuSpin — Nutation & CT-Selectivity", page_icon="🧪", layout="wide")
page_header("Nutation & CT-Selectivity", "Why quadrupolar central-transition nutation isn't a simple sinusoid, and how DFS boosts it")

quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5]
with st.sidebar:
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("23Na") if "23Na" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    Cq_mhz = st.slider("Cq (MHz)", 0.1, 15.0, 3.0, 0.1)
    sat_half_width_khz = st.slider("Satellite manifold half-width (kHz, ~ Cq-set)", 10.0, 2000.0, 300.0, 10.0)
    nu1_khz = st.slider("RF field ν1 (kHz)", 1.0, 150.0, 40.0, 1.0)
    max_pulse_us = st.slider("Max pulse duration (µs)", 5.0, 200.0, 60.0, 1.0)

enh_selective = ct_selective_enhancement(nuc.spin, sat_half_width_khz * 1000, nu1_khz * 1000)
enh_nonselective = 1.0

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**CT-selective nutation** (enhancement = I+1/2 = {enh_selective:.1f}×)")
    curve_sel = nutation_curve(nuc.spin, nu1_khz, enh_selective, max_pulse_us)
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    ax.plot(curve_sel["t_us"], curve_sel["signal"], color="#5b46e5")
    ax.set_xlabel("Pulse duration (µs)"); ax.set_ylabel("CT signal |Mxy|")
    st.pyplot(fig); plt.close(fig)

with col2:
    st.markdown("**Non-selective nutation** (enhancement = 1×, satellites also excited)")
    curve_non = nutation_curve(nuc.spin, nu1_khz, enh_nonselective, max_pulse_us)
    fig2, ax2 = plt.subplots(figsize=(5.5, 3.4))
    ax2.plot(curve_non["t_us"], curve_non["signal"], color="#c05621")
    ax2.set_xlabel("Pulse duration (µs)"); ax2.set_ylabel("CT signal |Mxy|")
    st.pyplot(fig2); plt.close(fig2)

st.divider()
st.subheader("DFS adiabatic sweep: satellite → central-transition population transfer")
dfs1, dfs2, dfs3 = st.columns(3)
with dfs1:
    dfs_nu1_khz = st.slider("DFS ν1 (kHz)", 0.1, 50.0, 2.0, 0.1)
with dfs2:
    dfs_sweep_khz = st.slider("Sweep range (kHz)", 1.0, 500.0, 50.0, 1.0)
with dfs3:
    dfs_duration_ms = st.slider("Sweep duration (ms)", 0.1, 10.0, 2.0, 0.1)

adiabaticity = dfs_sweep_khz / max(dfs_nu1_khz, 1e-6)
ens = bloch.Ensemble.from_gaussian_offsets(1, 0.0, seed=1)
bloch.apply_dfs_sweep(ens, dfs_duration_ms, dfs_nu1_khz, dfs_sweep_khz)
mz_final = float(ens.mz[0])

st.markdown(
    f"Adiabaticity ratio (sweep range / ν1) = **{adiabaticity:.1f}** "
    f"({'well inside' if adiabaticity > 10 else 'NOT in'} the adiabatic regime, which needs ν1 ≪ sweep range) "
    f" → final Mz = **{mz_final:.3f}** (starts at +1; adiabatic passage inverts it toward −1)"
)
fig3, ax3 = plt.subplots(figsize=(7, 1.2))
ax3.barh([0], [1], color="#e2e8f0")
ax3.barh([0], [max(min(mz_final, 1), -1)], color="#5b46e5" if mz_final < 0 else "#c05621", left=0)
ax3.set_xlim(-1, 1); ax3.set_yticks([]); ax3.set_xlabel("Mz after DFS sweep")
st.pyplot(fig3); plt.close(fig3)

st.caption(
    "Nutation curves: (I+1/2) CT-selective enhancement blended with a satellite-bleed-through non-ideality "
    "(visuspin.physics.quadrupole.nutation_curve). DFS: genuine adiabatic-passage simulation via Rodrigues-rotation "
    "stepping through a swept effective field (Iuga et al., J. Magn. Reson. 147, 192 (2000))."
)

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.hmqc import mq_transfer_efficiency, optimal_tau_ms, hmqc_spectrum

st.set_page_config(page_title="VisuSpin — HMQC", page_icon="🔀", layout="wide")
page_header("HMQC", "2D heteronuclear correlation via J- or D-mediated multiple-quantum coherence transfer")

with st.sidebar:
    coupling_type = st.radio("Coherence-transfer mechanism", ["J (through-bond, scalar)", "D (through-space, dipolar/recoupled)"])
    if coupling_type.startswith("J"):
        coupling_hz = st.slider("J coupling (Hz)", 1.0, 300.0, 140.0, 1.0)
    else:
        coupling_hz = st.slider("Recoupled D (Hz)", 50.0, 8000.0, 2000.0, 50.0)
    tau_opt = optimal_tau_ms(coupling_hz)
    tau_ms = st.slider("Fixed delay τ (ms)", 0.0, max(2 * tau_opt, 0.01), float(tau_opt), max(tau_opt / 100, 1e-4), format="%.4f")

    st.subheader("Correlated sites (edit as a table)")
    default_sites = [
        {"shift_i_hz": 500.0, "shift_s_hz": -1200.0, "amplitude": 1.0},
        {"shift_i_hz": -800.0, "shift_s_hz": 600.0, "amplitude": 0.7},
    ]
    sites_df = st.data_editor(default_sites, num_rows="dynamic", key="hmqc_sites")

eff = mq_transfer_efficiency(coupling_hz, tau_ms)
st.markdown(f"**Transfer efficiency at τ={tau_ms:.4f} ms: sin(πcτ) = {eff:.3f}**  (optimal τ = {tau_opt:.4f} ms)")

tau_axis = np.linspace(0, 2 * tau_opt, 300)
eff_axis = np.array([mq_transfer_efficiency(coupling_hz, t) for t in tau_axis])

col1, col2 = st.columns([1, 1.3])
with col1:
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.plot(tau_axis, eff_axis, color="#5b46e5")
    ax.axvline(tau_ms, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("τ (ms)"); ax.set_ylabel("Transfer efficiency sin(πcτ)")
    st.pyplot(fig); plt.close(fig)

with col2:
    sites = [s for s in sites_df if all(k in s and s[k] is not None for k in ("shift_i_hz", "shift_s_hz"))]
    for s in sites:
        s.setdefault("amplitude", 1.0)
    if sites:
        spec = hmqc_spectrum(sites, coupling_hz, tau_ms, linewidth_hz=60.0, n_points=250)
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        cf = ax2.contourf(spec["f2_hz"], spec["f1_hz"], spec["intensity"], levels=20, cmap="viridis")
        ax2.set_xlabel("F2 — I shift (Hz, direct)"); ax2.set_ylabel("F1 — S shift (Hz, indirect)")
        fig2.colorbar(cf, ax=ax2, label="Intensity")
        st.pyplot(fig2); plt.close(fig2)
    else:
        st.info("Add at least one correlated site in the sidebar table.")

st.caption(
    "Sequence: 90(I) – τ – 90(S) – t1 – 90(S) – τ – acquire(I) (Cavadini et al., J. Magn. Reson. 182, 168 (2006)). "
    "Transfer efficiency uses the standard INEPT-style sin(π·coupling·τ) function "
    "(Morris & Freeman, J. Am. Chem. Soc. 101, 760 (1979)); D-coupling uses the same formula with a "
    "rotor-recoupled dipolar constant in place of J."
)

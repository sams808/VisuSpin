import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.sequences.blocks import SequenceContext, Pulse, Delay, Loop, SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep
from visuspin.sequences.presets import PRESETS
from visuspin.sequences.engine import run_sequence
from visuspin.sequences.diagram import render_sequence_diagram

st.set_page_config(page_title="VisuSpin — Pulse Sequence Composer", page_icon="🧩", layout="wide")
page_header("Pulse Sequence Composer", "Build a pulse sequence block by block, Scratch-style, and see its timing diagram and simulated signal")

BLOCK_CLASSES = {cls.name: cls for cls in [Pulse, Delay, Loop, SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep]}

if "vs_sequence" not in st.session_state:
    st.session_state.vs_sequence = list(PRESETS["Hahn echo"]())

with st.sidebar:
    st.subheader("Load a preset")
    preset_name = st.selectbox("Preset", list(PRESETS.keys()), key="preset_name")
    if st.button("Load", use_container_width=True, key="load_button"):
        st.session_state.vs_sequence = list(PRESETS[preset_name]())
        st.rerun()

    st.subheader("Sequence context")
    T1_ms = st.slider("T1 (ms)", 1.0, 5000.0, 500.0, 1.0)
    T2_ms = st.slider("T2 (ms)", 0.1, 2000.0, 50.0, 0.1)
    nu1_khz = st.slider("Global RF field ν1 (kHz)", 1.0, 200.0, 25.0, 1.0)
    mas_rate_khz = st.slider("MAS rate (kHz, 0 = static)", 0.0, 100.0, 0.0, 1.0)
    n_iso = st.slider("Isochromats simulated", 20, 500, 100, 10)
    sigma = st.slider("Inhomogeneous broadening σ (rad/ms)", 0.0, 2.0, 0.1, 0.01)

ctx = SequenceContext(T1_ms=T1_ms, T2_ms=T2_ms, mas_rate_khz=mas_rate_khz, nu1_khz=nu1_khz)


def render_param_widgets(block, key_prefix):
    for key, default, lo, hi, step, unit in block.params:
        widget_key = f"{key_prefix}_{key}"
        current = block.values.get(key, default)
        new_val = st.number_input(f"{key} ({unit})", min_value=float(lo), max_value=float(hi),
                                     value=float(current), step=float(step), key=widget_key)
        block.values[key] = new_val


def render_block_list(blocks, prefix, depth=0):
    remove_idx = None
    for i, b in enumerate(blocks):
        indent = "&nbsp;" * (depth * 4)
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"{indent}**{i+1}. {b.name}**", unsafe_allow_html=True)
                cols = st.columns(max(len(b.params), 1))
                for col, (key, default, lo, hi, step, unit) in zip(cols, b.params):
                    with col:
                        widget_key = f"{prefix}_{i}_{key}"
                        current = b.values.get(key, default)
                        new_val = st.number_input(f"{key} ({unit})", min_value=float(lo), max_value=float(hi),
                                                     value=float(current), step=float(step), key=widget_key)
                        b.values[key] = new_val
                if isinstance(b, Loop):
                    st.caption("Loop body:")
                    render_block_list(b.body, f"{prefix}_{i}_body", depth + 1)
                    add_col, _ = st.columns([1, 3])
                    with add_col:
                        new_type = st.selectbox("Add to loop body", list(BLOCK_CLASSES.keys()),
                                                   key=f"{prefix}_{i}_addtype")
                        if st.button("+ Add", key=f"{prefix}_{i}_addbtn"):
                            b.body.append(BLOCK_CLASSES[new_type]())
                            st.rerun()
            with c2:
                if st.button("Remove", key=f"{prefix}_{i}_remove"):
                    remove_idx = i
    if remove_idx is not None:
        blocks.pop(remove_idx)
        st.rerun()


st.subheader("Sequence")
render_block_list(st.session_state.vs_sequence, "seq")

add_col1, add_col2 = st.columns([1, 3])
with add_col1:
    new_block_type = st.selectbox("Block type", list(BLOCK_CLASSES.keys()), key="new_block_type")
    if st.button("+ Add block", use_container_width=True):
        st.session_state.vs_sequence.append(BLOCK_CLASSES[new_block_type]())
        st.rerun()

st.divider()
st.subheader("Timing diagram")
if st.session_state.vs_sequence:
    fig = render_sequence_diagram(st.session_state.vs_sequence)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Simulated signal")
    try:
        out = run_sequence(st.session_state.vs_sequence, ctx, n_isochromats=n_iso, sigma_rad_per_ms=sigma)
        fig2, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot(out["t_ms"], out["mxy"], color="#5b46e5", label="|Mxy|")
        ax.plot(out["t_ms"], out["mz"], color="#f0a83c", label="Mz")
        ax.set_xlabel("Time (ms)"); ax.set_ylabel("Magnetisation"); ax.legend()
        st.pyplot(fig2)
        plt.close(fig2)
    except Exception as exc:
        st.error(f"Could not simulate this sequence: {exc}")
else:
    st.info("Add at least one block to build a sequence.")

st.caption(
    "Every named technique (Hahn echo, CPMG, REDOR, CP, spin-lock/T1rho, DFS) is just a specific ordering "
    "of these same primitive blocks (visuspin.sequences.blocks) acting on the same underlying isochromat "
    "ensemble (visuspin.physics.bloch) — remix any preset above to build your own."
)

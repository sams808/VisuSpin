import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, next_lesson

st.set_page_config(page_title="VisuSpin — Spectral Fitting Workshop", page_icon="📐", layout="wide")
page_header("Lesson 23: Spectral Fitting Workshop")
lesson_header(
    "Lesson 23 of 24",
    "You've built spectra from known components all through this app. Real data runs the other way.",
    "Given a spectrum with overlapping peaks, how do you actually extract the population, "
    "position, and width of each underlying component — rather than eyeballing peak heights, "
    "which Lesson 13 already showed can be misleading?",
)

st.markdown(
    """
Below is a **mystery spectrum** built from two hidden Gaussian components.
Adjust the two candidate components until your fit overlays the target as
closely as possible, watching the residual (goodness-of-fit) as you go —
exactly what fitting software does automatically, just one manual step at
a time.
"""
)


def gauss(x, center, width, amp):
    return amp * np.exp(-((x - center) ** 2) / (2 * width ** 2))


if "fit_truth" not in st.session_state:
    rng = np.random.default_rng()
    st.session_state.fit_truth = {
        "c1": rng.uniform(-60, -20), "w1": rng.uniform(4, 10), "a1": rng.uniform(0.4, 1.0),
        "c2": rng.uniform(20, 60), "w2": rng.uniform(4, 10), "a2": rng.uniform(0.4, 1.0),
    }

if st.button("🎲 New mystery spectrum"):
    rng = np.random.default_rng()
    st.session_state.fit_truth = {
        "c1": rng.uniform(-60, -20), "w1": rng.uniform(4, 10), "a1": rng.uniform(0.4, 1.0),
        "c2": rng.uniform(20, 60), "w2": rng.uniform(4, 10), "a2": rng.uniform(0.4, 1.0),
    }
    st.rerun()

truth = st.session_state.fit_truth
x = np.linspace(-100, 100, 600)
target = gauss(x, truth["c1"], truth["w1"], truth["a1"]) + gauss(x, truth["c2"], truth["w2"], truth["a2"])

st.subheader("Your fit")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Component 1**")
    fc1 = st.slider("Position 1 (ppm)", -100.0, 100.0, -40.0, 1.0, key="fc1")
    fw1 = st.slider("Width 1", 1.0, 20.0, 7.0, 0.5, key="fw1")
    fa1 = st.slider("Amplitude 1", 0.0, 1.5, 0.7, 0.05, key="fa1")
with c2:
    st.markdown("**Component 2**")
    fc2 = st.slider("Position 2 (ppm)", -100.0, 100.0, 40.0, 1.0, key="fc2")
    fw2 = st.slider("Width 2", 1.0, 20.0, 7.0, 0.5, key="fw2")
    fa2 = st.slider("Amplitude 2", 0.0, 1.5, 0.7, 0.05, key="fa2")

fit = gauss(x, fc1, fw1, fa1) + gauss(x, fc2, fw2, fa2)
residual = target - fit
sse = np.sum(residual ** 2)
ss_tot = np.sum((target - target.mean()) ** 2)
r2 = 1 - sse / ss_tot if ss_tot > 0 else 0

fig, (axa, axb) = plt.subplots(2, 1, figsize=(8, 5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
axa.plot(x, target, color="#5b46e5", linewidth=2, label="Mystery target")
axa.plot(x, fit, color="#c05621", linestyle="--", label="Your fit")
axa.set_ylabel("Intensity"); axa.legend(); axa.invert_xaxis()
axb.plot(x, residual, color="#2f855a")
axb.axhline(0, color="gray", linewidth=0.5)
axb.set_xlabel("Shift (ppm)"); axb.set_ylabel("Residual"); axb.invert_xaxis()
st.pyplot(fig); plt.close(fig)

st.metric("Goodness of fit (R²)", f"{r2:.4f}")
csv_data = "shift_ppm,target,your_fit\n" + "\n".join(
    f"{xi:.3f},{ti:.6f},{fi:.6f}" for xi, ti, fi in zip(x, target, fit)
)
st.download_button("Download target + fit as CSV", csv_data, file_name="fitting_workshop.csv", mime="text/csv")
if r2 > 0.98:
    st.success("Excellent fit — check the true parameters below.")
elif r2 > 0.9:
    st.info("Getting close — look at where the residual trace is still large.")
else:
    st.warning("Still far off — use the residual trace to see which region needs the most adjustment.")

with st.expander("Reveal the true parameters"):
    st.write(
        f"Component 1: position = {truth['c1']:.1f} ppm, width = {truth['w1']:.1f}, amplitude = {truth['a1']:.2f}\n\n"
        f"Component 2: position = {truth['c2']:.1f} ppm, width = {truth['w2']:.1f}, amplitude = {truth['a2']:.2f}"
    )
    st.caption(
        "Notice that a visually excellent fit doesn't guarantee your parameters exactly match the "
        "truth — width and amplitude often trade off against each other (a slightly wider, shorter "
        "peak can look almost identical to a slightly narrower, taller one). This parameter "
        "correlation is exactly why real fitting software reports uncertainties, not just best-fit "
        "values, and why independent constraints (known stoichiometry, DFT-predicted parameters "
        "from Lesson 21) matter so much in practice."
    )

key_takeaway(
    "Fitting is optimization: minimize the residual between a model (a sum of known-shape "
    "components) and the data. A good R² is necessary but not sufficient — the same target can "
    "often be matched almost equally well by more than one set of parameters, which is exactly "
    "why Lesson 15's quantification pitfalls and Lesson 21's DFT predictions matter as independent "
    "checks, not just decoration."
)

next_lesson("Lesson 24 — Reference & Glossary", "pages/24_Reference_and_Glossary.py")

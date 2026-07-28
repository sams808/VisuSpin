"""
Heteronuclear (e.g. 1H) decoupling: without decoupling, a rare spin (S) J-
coupled to n equivalent I=1/2 spins shows a first-order (weak-coupling-limit)
multiplet with binomial (Pascal's-triangle) intensities, spacing J and n+1
lines (Karplus, M. & Pople, J.A., "Theory of carbon NMR chemical shifts in
conjugated molecules." J. Chem. Phys. 38, 2803 (1963) for the general
multiplet-counting result; standard in any NMR text, e.g. Levitt, "Spin
Dynamics," 2nd ed., ch. 5). Continuous or multi-pulse (TPPM, SPINAL-64, ...)
decoupling collapses this to a single line at the multiplet centroid.

Imperfect decoupling (finite RF amplitude, off-resonance, decoupling-sequence
mismatch) leaves residual splitting/broadening. Modelling exactly which
residual lineshape a specific decoupling sequence (TPPM, SPINAL-64, XiX, ...)
leaves behind requires Floquet/average-Hamiltonian theory specific to that
sequence -- out of scope for a teaching tool. Instead we use the standard
simplified picture: an effective residual linewidth added in quadrature to
the natural linewidth, which correctly captures the qualitative lesson
(imperfect decoupling broadens, doesn't just attenuate, the line) without
claiming sequence-specific quantitative accuracy.
"""
from __future__ import annotations
from math import comb
import numpy as np


def multiplet_spectrum(j_hz: float, n_coupled_spins: int, center_hz: float = 0.0,
                          linewidth_hz: float = 20.0, n_points: int = 2000,
                          span_hz: float | None = None) -> dict:
    """First-order (weak-coupling) multiplet from n equivalent I=1/2 spins:
    n+1 lines at center + J*(k - n/2), k=0..n, intensities C(n,k)."""
    if span_hz is None:
        span_hz = j_hz * (n_coupled_spins + 2) + 10 * linewidth_hz
    freqs = np.linspace(center_hz - span_hz / 2, center_hz + span_hz / 2, n_points)
    spec = np.zeros_like(freqs)
    for k in range(n_coupled_spins + 1):
        offset = center_hz + j_hz * (k - n_coupled_spins / 2.0)
        weight = comb(n_coupled_spins, k)
        spec += weight * np.exp(-((freqs - offset) ** 2) / (2 * linewidth_hz ** 2))
    if spec.max() > 0:
        spec = spec / spec.max()
    return {"freq_hz": freqs, "intensity": spec}


def decoupled_spectrum(center_hz: float = 0.0, linewidth_hz: float = 20.0,
                          residual_coupling_hz: float = 0.0, n_points: int = 2000,
                          span_hz: float | None = None) -> dict:
    """Decoupled S-spin line: a single peak at the multiplet centroid. A
    nonzero `residual_coupling_hz` models imperfect decoupling as an extra
    broadening added in quadrature (not a literal residual J-splitting)."""
    if span_hz is None:
        span_hz = 20 * linewidth_hz + 10 * residual_coupling_hz
    freqs = np.linspace(center_hz - span_hz / 2, center_hz + span_hz / 2, n_points)
    eff_lw = np.sqrt(linewidth_hz ** 2 + residual_coupling_hz ** 2)
    spec = np.exp(-((freqs - center_hz) ** 2) / (2 * eff_lw ** 2))
    return {"freq_hz": freqs, "intensity": spec, "effective_linewidth_hz": eff_lw}

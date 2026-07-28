"""
Heteronuclear Multiple-Quantum Correlation (HMQC): correlates an I-spin shift
(F2, directly detected) with an S-spin shift (F1, indirectly detected) via a
short through-bond (J) or through-space (D, recoupled dipolar) coupling.

Sequence (Cavadini, S. et al. "Indirect detection of nitrogen-14 in
solid-state NMR spectroscopy." J. Magn. Reson. 182, 168 (2006); solution
analogue: Bax, A., Griffey, R.H. & Hawkins, B.L. J. Magn. Reson. 55, 301
(1983)):

    90(I) - tau - 90(S) - t1 - 90(S) - tau - acquire(I)

`tau` on each side lets I-S coherence interconvert with I-S multiple-quantum
coherence; S evolves at its own shift during t1 (indirect dimension), and the
signal is detected on I (direct dimension) -- giving a 2D peak at
(shift_S, shift_I) for every coupled pair, with an intensity set by the
coherence-transfer efficiency sin(pi*coupling*tau) (the same INEPT-style
transfer function used in solution HSQC/HMQC; Morris, G.A. & Freeman, R. J.
Am. Chem. Soc. 101, 760 (1979)). For J-coupling this is a scalar,
orientation-independent Hz value; for D-coupling it is the (rotor-averaged or
static) dipolar coupling constant, orientation-dependent in a real powder --
here we use its rotor-synchronised recoupled value as a single effective Hz
number, the same simplification REDOR's dephasing-curve module discloses.
"""
from __future__ import annotations
import numpy as np


def mq_transfer_efficiency(coupling_hz: float, tau_ms: float) -> float:
    """Coherence-transfer efficiency after a fixed delay tau on each side of
    the HMQC sandwich: sin(pi*coupling*tau), maximal at tau = 1/(2*coupling)
    and zero at tau = 0 or 1/coupling (ignoring relaxation)."""
    tau_s = tau_ms / 1000.0
    return float(np.sin(np.pi * coupling_hz * tau_s))


def optimal_tau_ms(coupling_hz: float) -> float:
    """tau that maximises the transfer efficiency for an isolated pair."""
    if coupling_hz <= 0:
        return 0.0
    return 1000.0 / (2.0 * coupling_hz)


def hmqc_spectrum(sites: list[dict], coupling_hz: float, tau_ms: float,
                    f1_range_hz: tuple = (-2000, 2000), f2_range_hz: tuple = (-2000, 2000),
                    linewidth_hz: float = 80.0, n_points: int = 200) -> dict:
    """2D correlation map. `sites`: list of {"shift_i_hz", "shift_s_hz",
    "amplitude"} -- one entry per correlated I-S pair (e.g. a bonded or
    dipolar-proximate pair). Returns a dict with 1D axes f1_hz/f2_hz and a 2D
    `intensity` array (F1 rows x F2 cols), each site rendered as a 2D
    Gaussian peak scaled by the shared coherence-transfer efficiency."""
    eff = mq_transfer_efficiency(coupling_hz, tau_ms)
    f1 = np.linspace(*f1_range_hz, n_points)
    f2 = np.linspace(*f2_range_hz, n_points)
    F1, F2 = np.meshgrid(f1, f2, indexing="ij")
    intensity = np.zeros_like(F1)
    for site in sites:
        amp = site.get("amplitude", 1.0) * abs(eff)
        g = amp * np.exp(-((F1 - site["shift_s_hz"]) ** 2 + (F2 - site["shift_i_hz"]) ** 2) / (2 * linewidth_hz ** 2))
        intensity += g
    return {"f1_hz": f1, "f2_hz": f2, "intensity": intensity, "efficiency": eff, "tau_ms": tau_ms}

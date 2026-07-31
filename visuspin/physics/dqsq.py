"""
Homonuclear double-quantum/single-quantum (DQ-SQ) correlation: reveals
spatial proximity between spins of the SAME nucleus (e.g. Si-O-Si, P-O-P
network connectivity) -- complementary to HMQC's heteronuclear correlation.

Reuses the identical coherence-transfer-efficiency function as HMQC
(visuspin.physics.hmqc.mq_transfer_efficiency), since both rely on the same
sin(pi*coupling*tau)-type recoupling-time dependence; here it drives a
homonuclear dipolar-recoupled DQ pathway (e.g. BABA, POST-C7, SPC5) instead
of a heteronuclear J/D transfer.

References: Feike, M. et al. "Broadband Multiple-Quantum NMR Spectroscopy."
J. Magn. Reson. A 122, 214 (1996) (BABA); Hohwy, M. et al. "Broadband
dipolar recoupling in the nuclear magnetic resonance of rotating solids: A
compensated C7 pulse sequence." J. Chem. Phys. 108, 2686 (1998) (POST-C7).
"""
from __future__ import annotations
import numpy as np

from .hmqc import mq_transfer_efficiency, optimal_tau_ms  # noqa: F401 (re-exported for convenience)


def dqsq_spectrum(pairs: list[dict], d_hz: float, tau_ms: float,
                    f2_range_hz: tuple = (-2000, 2000), linewidth_hz: float = 80.0,
                    n_points: int = 250) -> dict:
    """2D DQ-SQ correlation map. `pairs`: list of {"shift_a_hz",
    "shift_b_hz", "amplitude"} -- one entry per dipolar-coupled spin pair.
    shift_a may equal shift_b (an "auto-peak" pair: a spin coupled to a
    chemically-identical neighbor, landing exactly on the F1=2*F2
    diagonal); distinct shifts give two symmetric cross-peaks at
    (F2=shift_a, F1=shift_a+shift_b) and (F2=shift_b, F1=shift_a+shift_b)."""
    eff = mq_transfer_efficiency(d_hz, tau_ms)
    f1_range_hz = (2 * f2_range_hz[0], 2 * f2_range_hz[1])
    f1 = np.linspace(*f1_range_hz, n_points)
    f2 = np.linspace(*f2_range_hz, n_points)
    F1, F2 = np.meshgrid(f1, f2, indexing="ij")
    intensity = np.zeros_like(F1)
    for p in pairs:
        amp = p.get("amplitude", 1.0) * abs(eff)
        dq = p["shift_a_hz"] + p["shift_b_hz"]
        for sq in {p["shift_a_hz"], p["shift_b_hz"]}:
            intensity += amp * np.exp(-((F1 - dq) ** 2 + (F2 - sq) ** 2) / (2 * linewidth_hz ** 2))
    return {"f1_hz": f1, "f2_hz": f2, "intensity": intensity, "efficiency": eff, "tau_ms": tau_ms}

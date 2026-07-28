"""
Chemical shift anisotropy (CSA) powder patterns.

Standard Haeberlen-convention orientation dependence of the chemical shift
(a well-established, single-convention result -- unlike the second-order
quadrupolar case, there isn't the same risk of conflicting literature
prefactors here):

    delta(theta, phi) = delta_iso + (1/2)*Delta_delta*[3cos^2(theta) - 1
                          - eta_csa*sin^2(theta)*cos(2*phi)]

where Delta_delta = delta_zz - delta_iso (the anisotropy) and
eta_csa = (delta_yy - delta_xx)/Delta_delta (the asymmetry), with the
Haeberlen ordering |delta_zz - delta_iso| >= |delta_xx - delta_iso| >=
|delta_yy - delta_iso|.
"""
from __future__ import annotations
import numpy as np


def csa_shift(cos_theta: np.ndarray, phi: np.ndarray, delta_iso: float,
                delta_aniso: float, eta_csa: float) -> np.ndarray:
    """Per-orientation CSA shift (see module docstring for the formula);
    vectorized over cos_theta/phi so it can drive both the powder-pattern
    histogram below and the 3D powder-averaging visualizer
    (visuspin.physics.powder.powder_visualization_data)."""
    sin2_theta = 1 - cos_theta ** 2
    return delta_iso + 0.5 * delta_aniso * (3 * cos_theta ** 2 - 1 - eta_csa * sin2_theta * np.cos(2 * phi))


def csa_powder_pattern(delta_iso: float, delta_aniso: float, eta_csa: float,
                          n_samples: int = 8000, n_bins: int = 500) -> dict:
    """Static CSA powder lineshape. delta_iso/delta_aniso in the same units
    (e.g. ppm, or Hz if pre-converted); eta_csa in [0, 1]."""
    rng = np.random.default_rng(11)
    cos_t = rng.uniform(-1, 1, n_samples)
    phi = rng.uniform(0, 2 * np.pi, n_samples)
    shift = csa_shift(cos_t, phi, delta_iso, delta_aniso, eta_csa)
    lo, hi = shift.min(), shift.max()
    pad = 0.05 * max(hi - lo, 1e-9)
    counts, edges = np.histogram(shift, bins=n_bins, range=(lo - pad, hi + pad))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"shift": centers, "intensity": counts.astype(float)}


def principal_values(delta_iso: float, delta_aniso: float, eta_csa: float) -> tuple[float, float, float]:
    """Haeberlen-convention principal values (delta_zz, delta_xx, delta_yy)
    such that |zz-iso| >= |xx-iso| >= |yy-iso|."""
    dzz = delta_iso + delta_aniso
    dxx = delta_iso - delta_aniso / 2 * (1 + eta_csa)
    dyy = delta_iso - delta_aniso / 2 * (1 - eta_csa)
    return dzz, dxx, dyy

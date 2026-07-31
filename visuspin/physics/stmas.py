"""
STMAS (Satellite-Transition Magic-Angle Spinning): an alternative to MQMAS
for high-resolution quadrupolar-nucleus spectra (Gan, Z. "Isotropic NMR
spectra of half-integer quadrupolar nuclei using satellite transitions and
magic-angle spinning." J. Am. Chem. Soc. 122, 3242 (2000)). Instead of
correlating a symmetric multiple-quantum coherence with the central
transition (MQMAS), STMAS correlates a SATELLITE transition (e.g. the
+1/2<->+3/2 transition for I=3/2) with the CT.

The key practical contrast with MQMAS: the central transition (and every
symmetric multiple-quantum coherence MQMAS uses) has EXACTLY zero
first-order quadrupolar shift at any crystal orientation (see
quadrupole.py's docstring/tests) -- so it is completely insensitive to the
spinning axis being set even slightly off the true magic angle. A satellite
transition does NOT share that immunity: it has a genuine first-order
shift, which under MAS is scaled by the standard rank-2 tensor averaging
factor P2(cos(spin_angle)) -- exactly zero only at the true magic angle
(54.7356 deg), and growing for any small missetting. This is precisely why
STMAS, unlike MQMAS, demands an extremely precisely set spinning angle --
its chief practical drawback despite better inherent sensitivity (no
multiple-quantum excitation needed).
"""
from __future__ import annotations
import numpy as np

MAGIC_ANGLE_DEG = 54.7356


def satellite_first_order_shift_hz(I: float, Cq_hz: float, m_upper: float, cos_theta: float) -> float:
    """Static first-order shift of the (m_upper <-> m_upper-1) transition at
    a single crystallite orientation (axially symmetric EFG, eta=0 -- the
    same convention/formula as quadrupole.satellite_pattern, exposed here
    per-orientation). Exactly zero for the central transition (m_upper=0.5)
    at every orientation, by construction -- reproduced directly rather than
    assumed, since it's the same expression already verified in
    tests/test_quadrupole.py."""
    wq = 3 * Cq_hz / (2 * I * (2 * I - 1))
    coeff = m_upper - 0.5
    ang = (3 * cos_theta ** 2 - 1) / 2
    return -wq * coeff * ang


def rank2_mas_averaging_factor(spin_angle_deg) -> float:
    """P2(cos(spin_angle)) = (3cos^2(spin_angle)-1)/2 -- the standard rank-2
    tensor MAS time-averaging factor (zero exactly at the magic angle; the
    same mathematical fact already used and verified for the dipolar case
    in tests/test_dipolar.py's magic-angle test)."""
    theta = np.radians(spin_angle_deg)
    return (3 * np.cos(theta) ** 2 - 1) / 2


def satellite_residual_vs_angle_error(I: float, Cq_hz: float, cos_theta: float,
                                         angle_errors_deg: np.ndarray, m_upper: float | None = None) -> np.ndarray:
    """MAS-averaged residual satellite shift vs. spinning-angle error away
    from the true magic angle, for a fixed crystallite orientation.
    `m_upper` defaults to the outermost satellite (m=I) for maximum
    sensitivity."""
    if m_upper is None:
        m_upper = I
    static_shift = satellite_first_order_shift_hz(I, Cq_hz, m_upper, cos_theta)
    spin_angles = MAGIC_ANGLE_DEG + np.asarray(angle_errors_deg)
    factors = rank2_mas_averaging_factor(spin_angles)
    return static_shift * factors

"""
Dipolar-coupling physics: the classic Pake powder pattern for an isolated
two-spin system, and the REDOR dephasing curve (Gullion, T. & Schaefer, J.
"Rotational-Echo Double-Resonance NMR." J. Magn. Reson. 81, 196 (1989)).

Dipolar coupling constant convention: D (Hz) = (mu0/4pi)*(gamma_I*gamma_S*hbar)/(2*pi*r^3)
for a heteronuclear I-S pair at internuclear distance r.
"""
from __future__ import annotations
import numpy as np

MU0_OVER_4PI = 1e-7  # SI, T*m/A
HBAR = 1.054571817e-34  # J*s


def dipolar_coupling_hz(gamma_i: float, gamma_s: float, r_angstrom: float) -> float:
    """Dipolar coupling constant D (Hz) for a heteronuclear I-S pair at
    distance r (Angstrom). gamma_i, gamma_s in rad s^-1 T^-1."""
    r_m = r_angstrom * 1e-10
    d_rad_s = MU0_OVER_4PI * gamma_i * gamma_s * HBAR / (r_m ** 3)
    return d_rad_s / (2 * np.pi)


def dipolar_splitting_hz(cos_theta: np.ndarray, d_hz: float) -> np.ndarray:
    """Per-orientation dipolar splitting +D*(3cos^2(theta)-1)/2 (the standard
    secular heteronuclear dipolar term), vectorized over cos_theta so it can
    drive both the Pake-pattern histogram below and a 3D powder-averaging
    visualization (visuspin.physics.powder.powder_visualization_data)."""
    return d_hz * (3 * cos_theta ** 2 - 1) / 2


def pake_pattern(d_hz: float, n_samples: int = 20000, n_bins: int = 400) -> dict:
    """Powder-averaged dipolar splitting: each crystallite gives a doublet at
    +/- D*(3cos^2(theta)-1)/2 (the standard heteronuclear dipolar Hamiltonian
    secular term); powder averaging over theta produces the classic Pake
    doublet, with horns at +/- D/2 (theta=90 deg) and shoulders at +/- D
    (theta=0 deg)."""
    rng = np.random.default_rng(21)
    cos_t = rng.uniform(-1, 1, n_samples)
    split = dipolar_splitting_hz(cos_t, d_hz)
    freqs = np.concatenate([split, -split])
    max_f = d_hz * 1.15
    counts, edges = np.histogram(freqs, bins=n_bins, range=(-max_f, max_f))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"freq_hz": centers, "intensity": counts.astype(float), "d_hz": d_hz}


def redor_dephasing_curve(d_hz: float, rotor_period_us: float, n_cycles_max: int,
                             n_orientations: int = 2000) -> dict:
    """Powder-averaged REDOR dephasing (delta-S/S0) vs. number of rotor
    cycles, for an isolated, ideally-recoupled heteronuclear spin pair.

    Dephasing angle for a crystallite (theta, phi) after Nc rotor cycles of
    duration Tr: Delta-Phi = sqrt(2)*D*Nc*Tr*sin(2*theta)*cos(phi) (the
    standard REDOR dimensionless dephasing parametrisation; Gullion & Schaefer
    1989). Single-crystallite normalised signal = cos(Delta-Phi); delta-S/S0
    is the powder average of 1 - cos(Delta-Phi).
    """
    rng = np.random.default_rng(31)
    cos_t = rng.uniform(-1, 1, n_orientations)
    theta = np.arccos(cos_t)
    phi = rng.uniform(0, 2 * np.pi, n_orientations)
    nc = np.arange(0, n_cycles_max + 1)
    tr_s = rotor_period_us * 1e-6
    dephasing = np.empty(len(nc))
    for i, ncyc in enumerate(nc):
        dphi = np.sqrt(2) * d_hz * ncyc * tr_s * np.sin(2 * theta) * np.cos(phi)
        s_over_s0 = np.mean(np.cos(dphi))
        dephasing[i] = 1 - s_over_s0
    dephasing_time_ms = nc * rotor_period_us / 1000.0
    return {"n_cycles": nc, "dephasing_time_ms": dephasing_time_ms, "delta_s_over_s0": dephasing}

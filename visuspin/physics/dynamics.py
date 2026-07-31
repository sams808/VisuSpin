"""
Variable-temperature NMR / motional narrowing: two-site dynamic exchange
(e.g. ionic hopping, molecular reorientation, a phase transition) simulated
by direct Monte Carlo -- each isochromat starts on one of two sites and
stochastically jumps between them at a Poisson rate k while precessing and
relaxing under the ordinary Bloch equations -- rather than quoting the
classical Gutowsky-Holm/McConnell closed-form exchange lineshape from
memory. This is the same "simulate the physical process directly" choice
made for MAS sidebands (sidebands.py) and applied here to chemical/dynamic
exchange instead of mechanical rotor spinning.

References: Gutowsky, H.S. & Holm, C.H. "Rate Processes and Nuclear Magnetic
Resonance Spectra. II. Hindered Internal Rotation of Amides." J. Chem. Phys.
25, 1228 (1956); McConnell, H.M. "Reaction Rates by Nuclear Magnetic
Resonance." J. Chem. Phys. 28, 430 (1958).
"""
from __future__ import annotations
import numpy as np


def arrhenius_rate_hz(k0_hz: float, Ea_kJ_mol: float, T_kelvin) -> np.ndarray:
    """k(T) = k0 * exp(-Ea / (R*T)), R the gas constant in kJ/(mol*K)."""
    R = 8.314462618e-3  # kJ/(mol*K)
    T = np.asarray(T_kelvin, dtype=float)
    return k0_hz * np.exp(-Ea_kJ_mol / (R * T))


def two_site_exchange_spectrum(nu_a_hz: float, nu_b_hz: float, k_hz: float, T2_ms: float,
                                  acquire_ms: float = 200.0, n_isochromats: int = 4000,
                                  n_steps: int = 2000, seed: int = 99) -> dict:
    """Direct Monte Carlo simulation of 2-site (equal population) dynamic
    exchange: each isochromat starts on site A or B with 50/50 probability
    and jumps between them as a Poisson process at rate k_hz, precessing at
    that site's own frequency and relaxing with T2 throughout. Returns the
    FID and its FFT spectrum."""
    rng = np.random.default_rng(seed)
    site = rng.integers(0, 2, n_isochromats)
    mx = np.ones(n_isochromats)
    my = np.zeros(n_isochromats)
    dt_ms = acquire_ms / n_steps
    dt_s = dt_ms / 1000.0
    p_jump = min(k_hz * dt_s, 1.0)
    decay = np.exp(-dt_ms / T2_ms)
    fid = np.zeros(n_steps, dtype=complex)
    t_ms = np.arange(n_steps) * dt_ms
    for step in range(n_steps):
        jump = rng.random(n_isochromats) < p_jump
        site = np.where(jump, 1 - site, site)
        nu = np.where(site == 0, nu_a_hz, nu_b_hz)
        theta = 2 * np.pi * nu * dt_s
        c, s = np.cos(theta), np.sin(theta)
        mx, my = (mx * c + my * s) * decay, (my * c - mx * s) * decay
        fid[step] = np.mean(mx) + 1j * np.mean(my)
    freq_hz = np.fft.fftshift(np.fft.fftfreq(n_steps, d=dt_s))
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(fid)))
    if spectrum.max() > 0:
        spectrum = spectrum / spectrum.max()
    return {"t_ms": t_ms, "fid": fid, "freq_hz": freq_hz, "intensity": spectrum}

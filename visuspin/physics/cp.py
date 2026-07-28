"""
Cross-polarization (CP) buildup/decay kinetics under the Hartmann-Hahn match
condition (Pines, A., Gibby, M.G. & Waugh, J.S. "Proton-enhanced NMR of dilute
spins in solids." J. Chem. Phys. 59, 569 (1973); Hartmann, S.R. & Hahn, E.L.
Phys. Rev. 128, 2042 (1962)).

Classic two-time-constant I->S transfer formula: the abundant spin (I, e.g.
1H) is spin-locked and decays with T1rho_I while simultaneously feeding the
dilute spin (S, e.g. 13C) via the flip-flop term; S itself decays under its
own spin-lock with T1rho_S. For T_IS << T1rho_I (the useful CP regime), this
gives the classic buildup-then-decay ("hump") curve.
"""
from __future__ import annotations
import numpy as np


def cp_buildup_curve(t_is_ms: float, t1rho_i_ms: float, t1rho_s_ms: float = 1e9,
                       contact_max_ms: float = 20.0, n_points: int = 400) -> dict:
    """S-spin signal vs. contact time under CP.

    M_S(t)/M_S0 = [1/(1 - T_IS/T1rho_I)] * (exp(-t/T1rho_I) - exp(-t/T_IS)) * exp(-t/T1rho_S)

    The bracketed factor is the classic Pines-Gibby-Waugh result for transfer
    from a spin-locked I reservoir; the extra exp(-t/T1rho_S) factor accounts
    for the S magnetization's own spin-lock decay once transferred (dropped,
    i.e. T1rho_S -> infinity, in the simplest textbook treatment). Requires
    T_IS < T1rho_I for the well-behaved regime real CP experiments are run in;
    outside that regime the two exponentials no longer describe a transfer
    with a positive initial slope and the curve is flagged as unphysical.
    """
    t = np.linspace(0, contact_max_ms, n_points)
    if t_is_ms >= t1rho_i_ms:
        # Outside the standard CP regime (transfer slower than the I-spin lock
        # decays away) -- still evaluate the formula but flag it, rather than
        # silently returning a curve that looks fine but isn't physically the
        # intended CP regime.
        valid_regime = False
    else:
        valid_regime = True
    prefactor = 1.0 / (1.0 - t_is_ms / t1rho_i_ms)
    m_s = prefactor * (np.exp(-t / t1rho_i_ms) - np.exp(-t / t_is_ms)) * np.exp(-t / t1rho_s_ms)
    peak_idx = int(np.argmax(m_s))
    return {
        "t_ms": t,
        "m_s": m_s,
        "valid_regime": valid_regime,
        "optimal_contact_ms": float(t[peak_idx]),
        "peak_signal": float(m_s[peak_idx]),
    }

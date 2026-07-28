"""Named pulse sequences, each just a list of blocks.Block instances --
loading a preset gives students a working starting point to then remix block
by block, rather than a fixed, opaque "canned" experiment."""
from __future__ import annotations
from .blocks import Pulse, Delay, Loop, SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep


def free_induction_decay(acquire_ms: float = 60.0) -> list:
    return [Pulse(flip_deg=90, axis_deg=0), Acquire(duration_ms=acquire_ms)]


def hahn_echo(tau_ms: float = 10.0, acquire_ms: float = 40.0) -> list:
    """90x - tau - 180y - tau - echo. The refocusing pulse's phase (y, 90 deg
    from the excitation) is the conventional choice: the echo then reforms
    along the same axis the magnetisation started on after the 90, which is
    the easiest case to follow (Hahn, Phys. Rev. 80, 580 (1950))."""
    return [
        Pulse(flip_deg=90, axis_deg=0),
        Delay(duration_ms=tau_ms),
        Pulse(flip_deg=180, axis_deg=90),
        Delay(duration_ms=tau_ms),
        Acquire(duration_ms=acquire_ms),
    ]


def cpmg(tau_ms: float = 5.0, n_echoes: int = 8, acquire_ms: float = 5.0) -> list:
    """90x - [tau - 180y - tau - acquire-window]xN (Carr & Purcell, Phys. Rev.
    94, 630 (1954); Meiboom & Gill, Rev. Sci. Instrum. 29, 688 (1958))."""
    return [
        Pulse(flip_deg=90, axis_deg=0),
        Loop(body=[Delay(duration_ms=tau_ms), Pulse(flip_deg=180, axis_deg=90),
                     Delay(duration_ms=tau_ms), Acquire(duration_ms=acquire_ms)],
              n_repeats=n_echoes),
    ]


def inversion_recovery(tau_ms: float = 50.0, acquire_ms: float = 20.0) -> list:
    return [
        Pulse(flip_deg=180, axis_deg=0),
        Delay(duration_ms=tau_ms),
        Pulse(flip_deg=90, axis_deg=0),
        Acquire(duration_ms=acquire_ms),
    ]


def spin_lock_t1rho(lock_ms: float = 20.0, t1rho_ms: float = 15.0, acquire_ms: float = 20.0) -> list:
    return [
        Pulse(flip_deg=90, axis_deg=0),
        SpinLock(duration_ms=lock_ms, T1rho_ms=t1rho_ms),
        Acquire(duration_ms=acquire_ms),
    ]


def redor(d_hz: float = 200.0, rotor_period_us: float = 50.0, n_cycles: int = 32,
           acquire_ms: float = 1.0) -> list:
    """90x - [rotor-synchronised dipolar recoupling] - echo/acquire (Gullion &
    Schaefer, J. Magn. Reson. 81, 196 (1989)). The dephasing block reports
    S/S0 vs. dephasing time for the chosen coupling and spin rate."""
    return [
        Pulse(flip_deg=90, axis_deg=0),
        Recouple(d_hz=d_hz, rotor_period_us=rotor_period_us, n_cycles=n_cycles),
        Acquire(duration_ms=acquire_ms),
    ]


def cross_polarization(t_is_ms: float = 1.0, t1rho_i_ms: float = 10.0,
                         contact_ms: float = 5.0, acquire_ms: float = 20.0) -> list:
    """Hartmann-Hahn CP contact, then acquire on the dilute (S) channel
    (Pines, Gibby & Waugh, J. Chem. Phys. 59, 569 (1973))."""
    return [
        CrossPolarize(t_is_ms=t_is_ms, t1rho_i_ms=t1rho_i_ms, contact_ms=contact_ms),
        Acquire(duration_ms=acquire_ms),
    ]


def dfs_enhanced_ct(sweep_ms: float = 2.0, nu1_khz: float = 15.0, sweep_range_khz: float = 100.0,
                      acquire_ms: float = 20.0) -> list:
    """DFS adiabatic sweep (satellite -> central-transition population
    transfer) followed by a CT-selective 90 and acquisition (Iuga et al., J.
    Magn. Reson. 147, 192 (2000))."""
    return [
        DFSSweep(duration_ms=sweep_ms, nu1_khz=nu1_khz, sweep_range_khz=sweep_range_khz),
        Pulse(flip_deg=90, axis_deg=0),
        Acquire(duration_ms=acquire_ms),
    ]


PRESETS = {
    "Free induction decay": free_induction_decay,
    "Hahn echo": hahn_echo,
    "CPMG": cpmg,
    "Inversion recovery": inversion_recovery,
    "Spin-lock / T1rho": spin_lock_t1rho,
    "REDOR": redor,
    "Cross-polarization": cross_polarization,
    "DFS-enhanced CT excitation": dfs_enhanced_ct,
}

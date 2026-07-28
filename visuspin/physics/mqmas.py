"""
MQMAS (Multiple-Quantum Magic-Angle Spinning): correlates a multiple-quantum
(pQ, p=3,5,7...) evolution period with the single-quantum central-transition
(1Q/CT) detection period so that, after an appropriate shear of the 2D
frequency axes, the resulting "isotropic" F1 projection is free of the
second-order quadrupolar anisotropic broadening that persists on the CT even
under fast MAS (Frydman, L. & Harwood, J.S., J. Am. Chem. Soc. 117, 5367
(1995); Amoureux, J.P., Fernandez, C. & Steuernagel, S., J. Magn. Reson. A
123, 116 (1996)).

SCOPE NOTE, and why the shear ratio here is cited rather than re-derived:
quadrupole.py's static second-order CT lineshape is computed from scratch
(explicit spin operators + non-degenerate perturbation theory) because that
calculation is "just" linear algebra on a time-INDEPENDENT Hamiltonian. The
MAS-averaged pQ/1Q shear ratio is a different kind of problem: under MAS the
first-order quadrupolar Hamiltonian is periodic in time, and the correct
second-order shift requires Floquet (average-Hamiltonian) theory -- cross
terms between different rotor-phase harmonics, not a plain time-average of
the instantaneous static formula. That was checked directly here: substituting
the time-dependent crystallite orientation into the (verified) static
per-transition formula and time-averaging over one rotor period does NOT
reproduce a single orientation-independent pQ/1Q ratio (empirically the
"ratio" varied by more than an order of magnitude across orientations) --
see tests/test_mqmas.py::test_naive_time_averaging_is_not_orientation_independent
for the regression check preserving this finding. A full from-scratch Floquet
treatment is out of scope for a teaching tool, so the standard closed-form
result is used instead:

    C2(I, p) = p * [18*I*(I+1) - 8.5*p**2 - 5]
    R(I, p)  = C2(I, p) / C2(I, 1)

(general formula for the MQMAS second-order shear coefficient; reduces to the
well-known R(3/2, 3) = -7/9 exactly, cross-checked against the literature
value before adopting it here). The 2D schematic below then CONSTRUCTS the F1
(pQ) anisotropic shape as R times the same static per-orientation CT shape
used for F2 -- this is not an independent physical simulation of the pQ
lineshape, it is a deliberate schematic that reproduces the one thing MQMAS
is famous for teaching (a single shear collapses the anisotropic spread),
without overclaiming a first-principles derivation of the true multi-harmonic
MAS pQ lineshape.
"""
from __future__ import annotations
import numpy as np

from .quadrupole import ct_second_order_shift_hz


def mqmas_shear_ratio(I: float, p: int) -> float:
    """Closed-form MQMAS shear ratio R(I,p) = C2(I,p)/C2(I,1), C2(I,p) =
    p*[18*I(I+1) - 8.5*p^2 - 5] (Amoureux, Fernandez & Steuernagel 1996).
    Reproduces R(3/2,3) = -7/9 exactly."""
    def c2(pp):
        return pp * (18 * I * (I + 1) - 8.5 * pp ** 2 - 5)
    denom = c2(1)
    if abs(denom) < 1e-12:
        raise ValueError(f"degenerate C2(I,1)=0 for I={I}")
    return c2(p) / denom


def mqmas_spectrum(I: float, Cq_hz: float, eta: float, nu0_hz: float, p: int = 3,
                     isotropic_shift_hz: float = 0.0, n_samples: int = 4000) -> dict:
    """Schematic 2D MQMAS map. F2 uses the first-principles static CT
    second-order shift (visuspin.physics.quadrupole); F1(raw) is CONSTRUCTED
    as R(I,p) times that same per-orientation shape (see module docstring for
    why) plus the p-fold-scaled isotropic offset. Shearing (F1_raw - R*F2)
    then collapses to a single isotropic value by construction, illustrating
    the MQMAS principle."""
    R = mqmas_shear_ratio(I, p)
    rng = np.random.default_rng(4242)
    cos_t = rng.uniform(-1, 1, n_samples)
    theta = np.arccos(cos_t)
    phi = rng.uniform(0, 2 * np.pi, n_samples)
    shift_1q = np.array([ct_second_order_shift_hz(I, Cq_hz, eta, th, ph, nu0_hz) for th, ph in zip(theta, phi)])
    f2_hz = isotropic_shift_hz + shift_1q
    f1_raw_hz = p * isotropic_shift_hz + R * shift_1q
    f1_sheared_hz = f1_raw_hz - R * f2_hz
    return {
        "f2_hz": f2_hz, "f1_raw_hz": f1_raw_hz, "f1_sheared_hz": f1_sheared_hz,
        "shear_ratio": R, "p": p,
    }

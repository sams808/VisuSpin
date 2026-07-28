"""Verification of the MQMAS module: the closed-form shear-ratio formula
against known literature values, the shearing arithmetic, and a regression
check preserving the finding that a naive time-average of the static
per-orientation quadrupolar shift does NOT give an orientation-independent
pQ/1Q ratio (the reason this module uses a literature shear ratio rather than
a from-scratch Floquet derivation -- see mqmas.py's module docstring)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.mqmas import mqmas_shear_ratio, mqmas_spectrum
from visuspin.physics.quadrupole import ct_second_order_shift_hz, quadrupolar_hamiltonian_hz

MAGIC_ANGLE_RAD = np.radians(54.7356)


def _rotmat(alpha, beta, gamma):
    ca, sa = np.cos(alpha), np.sin(alpha)
    cb, sb = np.cos(beta), np.sin(beta)
    cg, sg = np.cos(gamma), np.sin(gamma)
    Rz1 = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz2 = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]])
    return Rz2 @ Ry @ Rz1


def _mq_second_order_shift_hz(I, Cq_hz, eta, theta, phi, nu0_hz, p):
    from visuspin.physics.quadrupole import spin_operators
    dim = int(round(2 * I + 1))
    m_vals = np.array([I - k for k in range(dim)])
    H = quadrupolar_hamiltonian_hz(I, Cq_hz, eta, theta, phi)
    idx_p = int(np.argmin(np.abs(m_vals - p / 2)))
    idx_m = int(np.argmin(np.abs(m_vals + p / 2)))

    def second_order(idx):
        total = 0.0
        for k in range(dim):
            if k == idx:
                continue
            denom = nu0_hz * (m_vals[idx] - m_vals[k])
            total += abs(H[idx, k]) ** 2 / denom
        return total
    return second_order(idx_p) - second_order(idx_m)


def _mas_avg_shift(I, Cq_hz, eta, beta_pr, gamma_pr, nu0_hz, nu_rot_hz, fn, n_time=48):
    """Naive approach: substitute the time-dependent crystallite orientation
    into the static formula, average over one rotor period."""
    R = _rotmat(0.0, beta_pr, gamma_pr)
    t = np.linspace(0, 1.0 / nu_rot_hz, n_time, endpoint=False)
    rotor_phase = 2 * np.pi * nu_rot_hz * t
    cb2, sb2 = np.cos(MAGIC_ANGLE_RAD), np.sin(MAGIC_ANGLE_RAD)
    cg2, sg2 = np.cos(rotor_phase), np.sin(rotor_phase)
    labz_rotor = np.stack([-cg2 * sb2, sg2 * sb2, np.full_like(t, cb2)], axis=-1)
    labz_pas = (R.T @ labz_rotor.T).T
    theta = np.arccos(np.clip(labz_pas[:, 2], -1, 1))
    phi = np.arctan2(labz_pas[:, 1], labz_pas[:, 0])
    vals = np.array([fn(I, Cq_hz, eta, th, ph, nu0_hz) for th, ph in zip(theta, phi)])
    return vals.mean()


def test_naive_time_averaging_is_not_orientation_independent():
    """Regression check for the reason mqmas.py cites a literature shear
    ratio instead of deriving it from scratch: naive rotor-period averaging
    of the static per-transition formula gives wildly inconsistent pQ/1Q
    ratios across crystallite orientations (not a single constant), because
    genuine 2nd-order MAS averaging needs Floquet theory, not a pointwise
    time-average."""
    I, Cq_hz, eta, nu0_hz, nu_rot_hz = 1.5, 1200.0, 0.4, 150e6, 20000.0
    rng = np.random.default_rng(1)
    ratios = []
    for _ in range(12):
        beta = np.arccos(rng.uniform(-1, 1))
        gamma = rng.uniform(0, 2 * np.pi)
        s1 = _mas_avg_shift(I, Cq_hz, eta, beta, gamma, nu0_hz, nu_rot_hz, ct_second_order_shift_hz)
        s3 = _mas_avg_shift(I, Cq_hz, eta, beta, gamma, nu0_hz, nu_rot_hz,
                              lambda *a: _mq_second_order_shift_hz(*a, 3))
        if abs(s1) > 1e-9:
            ratios.append(s3 / s1)
    ratios = np.array(ratios)
    assert ratios.std() > 2.0, \
        f"expected wildly inconsistent ratios (std>2), got std={ratios.std():.3f} -- naive averaging may now be valid, revisit mqmas.py's scope note"
    print(f"PASS naive time-averaged ratio is NOT orientation-independent (std={ratios.std():.2f}, "
          f"range [{ratios.min():.2f}, {ratios.max():.2f}]) -- confirms the literature-ratio approach is necessary")


def test_shear_ratio_matches_known_literature_value_I32_3Q():
    R = mqmas_shear_ratio(1.5, 3)
    assert abs(R - (-7 / 9)) < 1e-9, f"expected exactly -7/9, got {R}"
    print(f"PASS I=3/2, 3Q shear ratio = {R:.6f} = -7/9 exactly (standard literature value)")


def test_shear_ratio_trivial_for_p_equals_1():
    for I in [1.5, 2.5, 3.5, 4.5]:
        R = mqmas_shear_ratio(I, 1)
        assert abs(R - 1.0) < 1e-9
    print("PASS R(I,1)=1 exactly for all tested I (1Q correlated with itself)")


def test_shear_ratio_I52_matches_commonly_tabulated_values():
    # I=5/2 (23Na, 27Al-adjacent spins): commonly tabulated 3Q ratio is 19/12
    R3 = mqmas_shear_ratio(2.5, 3)
    assert abs(R3 - 19 / 12) < 1e-9, f"got {R3}"
    R5 = mqmas_shear_ratio(2.5, 5)
    assert abs(R5 - (-25 / 12)) < 1e-9, f"got {R5}"
    print(f"PASS I=5/2: R(3Q)={R3:.5f}=19/12, R(5Q)={R5:.5f}=-25/12 (standard tabulated values)")


def test_shearing_collapses_by_construction():
    I, p, Cq_hz, eta, nu0_hz = 1.5, 3, 1500.0, 0.3, 100e6
    spec = mqmas_spectrum(I, Cq_hz, eta, nu0_hz, p=p, isotropic_shift_hz=250.0, n_samples=2000)
    raw_spread = np.std(spec["f1_raw_hz"])
    sheared_spread = np.std(spec["f1_sheared_hz"])
    f2_spread = np.std(spec["f2_hz"])
    assert sheared_spread < 1e-6, f"sheared F1 should be a single value by construction, got spread {sheared_spread}"
    assert f2_spread > raw_spread * 0.1, "F2 should retain the genuine anisotropic CT spread"
    mean_sheared = np.mean(spec["f1_sheared_hz"])
    expected = (p - spec["shear_ratio"]) * 250.0
    assert abs(mean_sheared - expected) < 1e-6
    print(f"PASS sheared F1 collapses to a single value {mean_sheared:.2f} Hz (spread={sheared_spread:.2e} Hz), "
          f"matching (p-R)*isotropic_shift={expected:.2f} Hz, while F2 keeps {f2_spread:.1f} Hz of spread")


if __name__ == "__main__":
    test_naive_time_averaging_is_not_orientation_independent()
    test_shear_ratio_matches_known_literature_value_I32_3Q()
    test_shear_ratio_trivial_for_p_equals_1()
    test_shear_ratio_I52_matches_commonly_tabulated_values()
    test_shearing_collapses_by_construction()
    print("\nALL MQMAS TESTS PASSED")

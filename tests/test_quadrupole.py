"""Rigorous verification of the quadrupolar physics module -- especially the
first-principles second-order CT Hamiltonian, since that's the piece built
from scratch rather than a literature closed-form (see quadrupole.py docstring
for why)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.quadrupole import (
    spin_operators, quadrupolar_hamiltonian_hz, ct_second_order_shift_hz,
    ct_powder_pattern, satellite_pattern, ct_selective_enhancement,
)

def test_spin_operator_algebra():
    for I in [0.5, 1.0, 1.5, 2.5, 3.0]:
        Ix, Iy, Iz = spin_operators(I)
        dim = int(round(2*I+1))
        # [Ix,Iy] = i*Iz (standard angular momentum commutation relation)
        comm = Ix@Iy - Iy@Ix
        assert np.allclose(comm, 1j*Iz, atol=1e-10), f"I={I}: [Ix,Iy]!=iIz"
        # Ix^2+Iy^2+Iz^2 = I(I+1)*identity
        total = Ix@Ix + Iy@Iy + Iz@Iz
        assert np.allclose(total, I*(I+1)*np.eye(dim), atol=1e-10), f"I={I}: I^2 != I(I+1)"
    print("PASS spin operators satisfy standard angular momentum algebra for all tested I")

def test_hamiltonian_matches_textbook_form_at_theta0():
    # At theta=phi=0, H_Q should equal the textbook (omega_Q/6)*(3Iz^2-I(I+1)+eta(Ix^2-Iy^2))
    for I in [1.5, 2.5, 3.0]:
        for eta in [0.0, 0.3, 0.7]:
            Cq = 2.0e6  # Hz
            H = quadrupolar_hamiltonian_hz(I, Cq, eta, 0.0, 0.0)
            Ix, Iy, Iz = spin_operators(I)
            wq = 3*Cq/(2*I*(2*I-1))
            H_textbook = (wq/6)*(3*(Iz@Iz) - I*(I+1)*np.eye(Ix.shape[0]) + eta*(Ix@Ix-Iy@Iy))
            assert np.allclose(H, H_textbook, atol=1e-6), f"I={I} eta={eta}: mismatch"
    print("PASS constructed H_Q exactly matches textbook form at theta=phi=0 for several I, eta")

def test_ct_zero_first_order_shift():
    # Well-known result: the CT (+1/2<->-1/2) is unaffected by first-order
    # quadrupolar coupling -- i.e. the *diagonal* H_Q elements for m=+1/2 and
    # m=-1/2 must be equal (so their difference, the 1st-order CT shift, is
    # exactly zero) at any orientation.
    I = 2.5
    dim = int(round(2*I+1))
    m_vals = np.array([I-k for k in range(dim)])
    idx_p = int(np.argmin(np.abs(m_vals-0.5)))
    idx_m = int(np.argmin(np.abs(m_vals+0.5)))
    rng = np.random.default_rng(0)
    for _ in range(20):
        theta, phi, eta = rng.uniform(0,np.pi), rng.uniform(0,2*np.pi), rng.uniform(0,1)
        H = quadrupolar_hamiltonian_hz(I, 3.0e6, eta, theta, phi)
        assert abs(H[idx_p,idx_p].real - H[idx_m,idx_m].real) < 1e-6, (theta,phi,eta,H[idx_p,idx_p],H[idx_m,idx_m])
    print("PASS CT has exactly zero first-order quadrupolar shift at all tested orientations (as expected)")

def test_second_order_scales_as_Cq_squared_and_inverse_nu0():
    I, eta, theta, phi = 2.5, 0.2, 1.0, 0.5
    s1 = ct_second_order_shift_hz(I, 1.0e6, eta, theta, phi, nu0_hz=100e6)
    s2 = ct_second_order_shift_hz(I, 2.0e6, eta, theta, phi, nu0_hz=100e6)
    assert abs(s2/s1 - 4.0) < 1e-6, f"expected Cq^2 scaling (4x), got ratio {s2/s1}"
    s3 = ct_second_order_shift_hz(I, 1.0e6, eta, theta, phi, nu0_hz=200e6)
    assert abs(s3/s1 - 0.5) < 1e-6, f"expected 1/nu0 scaling (0.5x at double field), got ratio {s3/s1}"
    print(f"PASS second-order CT shift scales exactly as Cq^2 (ratio={s2/s1:.4f}) "
          f"and 1/nu0 (ratio={s3/s1:.4f}) -- higher field genuinely narrows the pattern")

def test_ct_isotropic_shift_is_nonzero_unlike_first_order_satellites():
    # The famous, practically-important fact that motivated MQMAS/DAS: the
    # second-order CT shift does NOT powder-average to zero (unlike every
    # first-order satellite transition, which does).
    pat = ct_powder_pattern(I=2.5, Cq_hz=3.0e6, eta=0.0, nu0_hz=104.37e6, n_samples=2000)
    assert abs(pat["isotropic_shift_hz"]) > 100, f"expected a substantial nonzero isotropic shift, got {pat['isotropic_shift_hz']} Hz"
    print(f"PASS second-order CT isotropic shift = {pat['isotropic_shift_hz']:.1f} Hz (nonzero, as it must be)")

def test_satellite_pattern_powder_averages_to_zero():
    pat = satellite_pattern(I=2.5, Cq_hz=2.0e6, n_samples=20000)
    mean_shift = np.average(pat["freq_hz"], weights=pat["intensity"])
    assert abs(mean_shift) < pat["max_shift_hz"]*0.02, f"expected ~zero mean, got {mean_shift}"
    print(f"PASS first-order satellite pattern powder-averages to ~0 (mean={mean_shift:.2f} Hz, "
          f"vs max shift {pat['max_shift_hz']:.0f} Hz)")

def test_ct_selective_enhancement_thresholds():
    assert ct_selective_enhancement(2.5, satellite_half_width_hz=600e3, nu1_hz=25e3) == 3.0
    assert ct_selective_enhancement(2.5, satellite_half_width_hz=100e3, nu1_hz=95e3) == 1.0
    assert ct_selective_enhancement(0.5, satellite_half_width_hz=600e3, nu1_hz=25e3) == 1.0
    print("PASS CT-selective enhancement factor switches correctly with pulse bandwidth and spin")

if __name__ == "__main__":
    test_spin_operator_algebra()
    test_hamiltonian_matches_textbook_form_at_theta0()
    test_ct_zero_first_order_shift()
    test_second_order_scales_as_Cq_squared_and_inverse_nu0()
    test_ct_isotropic_shift_is_nonzero_unlike_first_order_satellites()
    test_satellite_pattern_powder_averages_to_zero()
    test_ct_selective_enhancement_thresholds()
    print("\nALL QUADRUPOLE PHYSICS TESTS PASSED")

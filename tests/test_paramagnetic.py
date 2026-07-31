"""Verification of the paramagnetic NMR scaling laws against their own
exact defining properties."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.paramagnetic import (
    curie_law_factor, contact_shift_ppm, pseudocontact_shift_ppm, pre_rate_hz,
)

def test_curie_factor_is_one_at_reference_temperature():
    assert abs(curie_law_factor(298.15, 298.15) - 1.0) < 1e-9
    print("PASS Curie factor = 1 exactly at T = T_ref")

def test_curie_factor_halves_at_double_temperature():
    f = curie_law_factor(2 * 298.15, 298.15)
    assert abs(f - 0.5) < 1e-9
    print(f"PASS Curie factor at 2xT_ref = {f:.4f} (exactly 0.5, the defining 1/T law)")

def test_contact_shift_scales_as_1_over_T():
    s1 = contact_shift_ppm(100.0, T_kelvin=300.0)
    s2 = contact_shift_ppm(100.0, T_kelvin=600.0)
    assert abs(s1 / s2 - 2.0) < 1e-9
    print(f"PASS contact shift at 300K ({s1:.2f} ppm) is exactly 2x that at 600K ({s2:.2f} ppm)")

def test_pseudocontact_shift_zero_at_magic_angle():
    magic = np.radians(54.7356)
    shift = pseudocontact_shift_ppm(50.0, magic, T_kelvin=298.15)
    assert abs(shift) < 1e-4
    print(f"PASS pseudocontact shift is (numerically) zero at the magic angle, matching the same "
          f"(3cos^2(theta)-1) factor already verified for CSA and dipolar coupling: shift={shift:.6f} ppm")

def test_pseudocontact_shift_at_theta_zero_equals_reference():
    shift = pseudocontact_shift_ppm(50.0, 0.0, T_kelvin=298.15, T_ref_kelvin=298.15)
    assert abs(shift - 50.0) < 1e-9
    print(f"PASS pseudocontact shift at theta=0, T=T_ref reproduces the reference value exactly ({shift:.2f} ppm)")

def test_pre_rate_scales_as_inverse_sixth_power():
    r1 = pre_rate_hz(1000.0, r_angstrom=3.0, r_ref_angstrom=3.0)
    r2 = pre_rate_hz(1000.0, r_angstrom=6.0, r_ref_angstrom=3.0)
    assert abs(r1 - 1000.0) < 1e-9
    assert abs(r1 / r2 - 64.0) < 1e-6, f"expected exactly 2^6=64x, got {r1/r2}"
    print(f"PASS PRE rate at r_ref ({r1:.1f} Hz) is 64x (=2^6) the rate at 2xr_ref ({r2:.3f} Hz)")

if __name__ == "__main__":
    test_curie_factor_is_one_at_reference_temperature()
    test_curie_factor_halves_at_double_temperature()
    test_contact_shift_scales_as_1_over_T()
    test_pseudocontact_shift_zero_at_magic_angle()
    test_pseudocontact_shift_at_theta_zero_equals_reference()
    test_pre_rate_scales_as_inverse_sixth_power()
    print("\nALL PARAMAGNETIC NMR TESTS PASSED")

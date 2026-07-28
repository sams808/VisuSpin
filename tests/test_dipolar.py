"""Verification of the dipolar-coupling module against known special cases
(never had its own test until now)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.dipolar import dipolar_splitting_hz, pake_pattern, dipolar_coupling_hz

def test_splitting_at_theta_0_equals_d():
    split = dipolar_splitting_hz(np.array([1.0]), d_hz=1000.0)
    assert abs(split[0] - 1000.0) < 1e-9
    print(f"PASS theta=0 splitting = {split[0]:.1f} Hz = D exactly")

def test_splitting_at_theta_90_equals_minus_half_d():
    split = dipolar_splitting_hz(np.array([0.0]), d_hz=1000.0)
    assert abs(split[0] - (-500.0)) < 1e-9
    print(f"PASS theta=90 splitting = {split[0]:.1f} Hz = -D/2 exactly")

def test_splitting_zero_at_magic_angle():
    magic_cos = 1.0 / np.sqrt(3)
    split = dipolar_splitting_hz(np.array([magic_cos]), d_hz=1000.0)
    assert abs(split[0]) < 1e-9
    print(f"PASS splitting is exactly zero at the magic angle (cos(theta)=1/sqrt(3)), split={split[0]:.2e} Hz")

def test_pake_pattern_horns_and_shoulders():
    d_hz = 2000.0
    pat = pake_pattern(d_hz, n_samples=50000, n_bins=800)
    freqs, inten = pat["freq_hz"], pat["intensity"]
    # horns (theta=90, the most probable orientation-weighted region) should
    # be the tallest peaks, near +/- D/2
    horn_region = (np.abs(np.abs(freqs) - d_hz / 2) < d_hz * 0.05)
    assert inten[horn_region].max() > 0.8, "horns near +/-D/2 should be the most intense features"
    # shoulders near +/-D should have nonzero but much lower intensity
    shoulder_region = (np.abs(np.abs(freqs) - d_hz) < d_hz * 0.05)
    assert 0 < inten[shoulder_region].max() < inten[horn_region].max()
    print(f"PASS Pake pattern: horns near +/-D/2 are tallest ({inten[horn_region].max():.2f}), "
          f"shoulders near +/-D are lower ({inten[shoulder_region].max():.2f})")

def test_coupling_constant_scales_as_inverse_r_cubed():
    gamma_h = 267.522e6
    d_close = dipolar_coupling_hz(gamma_h, gamma_h, 1.0)
    d_far = dipolar_coupling_hz(gamma_h, gamma_h, 2.0)
    assert abs(d_close / d_far - 8.0) < 1e-6, f"expected exactly 2^3=8x, got {d_close/d_far}"
    print(f"PASS D(1 Angstrom)/D(2 Angstrom) = {d_close/d_far:.4f} = 2^3 exactly (1/r^3 scaling)")

if __name__ == "__main__":
    test_splitting_at_theta_0_equals_d()
    test_splitting_at_theta_90_equals_minus_half_d()
    test_splitting_zero_at_magic_angle()
    test_pake_pattern_horns_and_shoulders()
    test_coupling_constant_scales_as_inverse_r_cubed()
    print("\nALL DIPOLAR TESTS PASSED")

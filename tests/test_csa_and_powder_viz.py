"""Verification of the CSA orientation-dependence formula against known
special cases (never had its own test until now), and of the 3D
powder-averaging visualizer glue in powder.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.csa import csa_shift, csa_powder_pattern, principal_values
from visuspin.physics.powder import powder_visualization_data, sample_full_sphere, orientation_marker


def test_csa_shift_at_theta_zero_gives_delta_zz():
    delta_iso, delta_aniso, eta = 10.0, 100.0, 0.4
    shift = csa_shift(np.array([1.0]), np.array([0.0]), delta_iso, delta_aniso, eta)
    dzz, dxx, dyy = principal_values(delta_iso, delta_aniso, eta)
    assert abs(shift[0] - dzz) < 1e-9, f"theta=0 should give delta_zz={dzz}, got {shift[0]}"
    print(f"PASS CSA shift at theta=0 gives delta_zz exactly ({shift[0]:.2f} = {dzz:.2f})")


def test_csa_shift_at_theta_90_phi_0_and_90_give_dxx_dyy():
    delta_iso, delta_aniso, eta = 10.0, 100.0, 0.4
    dzz, dxx, dyy = principal_values(delta_iso, delta_aniso, eta)
    s_x = csa_shift(np.array([0.0]), np.array([0.0]), delta_iso, delta_aniso, eta)[0]
    s_y = csa_shift(np.array([0.0]), np.array([np.pi / 2]), delta_iso, delta_aniso, eta)[0]
    assert abs(s_x - dxx) < 1e-9, f"theta=90,phi=0 should give delta_xx={dxx}, got {s_x}"
    assert abs(s_y - dyy) < 1e-9, f"theta=90,phi=90 should give delta_yy={dyy}, got {s_y}"
    print(f"PASS CSA shift at (theta=90,phi=0)=delta_xx={s_x:.2f}, (theta=90,phi=90)=delta_yy={s_y:.2f}")


def test_powder_pattern_isotropic_average_matches_delta_iso():
    delta_iso, delta_aniso, eta = 50.0, 80.0, 0.6
    pat = csa_powder_pattern(delta_iso, delta_aniso, eta, n_samples=40000)
    mean_shift = np.sum(pat["shift"] * pat["intensity"]) / np.sum(pat["intensity"])
    assert abs(mean_shift - delta_iso) < 2.0, f"powder-average mean {mean_shift} should be close to delta_iso={delta_iso}"
    print(f"PASS CSA powder pattern mean shift = {mean_shift:.2f} (delta_iso = {delta_iso})")


def test_powder_visualization_coordinates_are_unit_vectors():
    data = powder_visualization_data(lambda ct, p: csa_shift(ct, p, 0.0, 100.0, 0.3), n_samples=500)
    r2 = data["x"] ** 2 + data["y"] ** 2 + data["z"] ** 2
    assert np.allclose(r2, 1.0, atol=1e-9), "all sampled orientation points should lie exactly on the unit sphere"
    print(f"PASS all {len(data['x'])} powder-visualizer orientation points lie exactly on the unit sphere")


def test_powder_visualization_shift_matches_direct_csa_call():
    delta_iso, delta_aniso, eta = 20.0, 60.0, 0.5
    data = powder_visualization_data(lambda ct, p: csa_shift(ct, p, delta_iso, delta_aniso, eta), n_samples=800, seed=13)
    rng = np.random.default_rng(13)
    cos_theta, phi = sample_full_sphere(800, rng)
    direct = csa_shift(cos_theta, phi, delta_iso, delta_aniso, eta)
    assert np.allclose(data["shift"], direct), "same seed should reproduce identical per-orientation shifts"
    print("PASS powder-visualizer shift values match a direct csa_shift call with the same sampled orientations")


def test_orientation_marker_matches_batched_coordinates():
    data = powder_visualization_data(lambda ct, p: csa_shift(ct, p, 0, 100, 0.2), n_samples=1, seed=99)
    rng = np.random.default_rng(99)
    cos_theta, phi = sample_full_sphere(1, rng)
    marker = orientation_marker(cos_theta[0], phi[0])
    assert np.allclose(marker, [data["x"][0], data["y"][0], data["z"][0]])
    print(f"PASS single-marker orientation_marker() matches the batched powder_visualization_data() coordinates")


if __name__ == "__main__":
    test_csa_shift_at_theta_zero_gives_delta_zz()
    test_csa_shift_at_theta_90_phi_0_and_90_give_dxx_dyy()
    test_powder_pattern_isotropic_average_matches_delta_iso()
    test_powder_visualization_coordinates_are_unit_vectors()
    test_powder_visualization_shift_matches_direct_csa_call()
    test_orientation_marker_matches_batched_coordinates()
    print("\nALL CSA + POWDER VISUALIZER TESTS PASSED")

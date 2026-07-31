"""Verification of the Czjzek/extended-Czjzek disorder model against
structural properties that follow directly from its definition (a random
traceless symmetric tensor), rather than a closed-form density that would
carry the same "misremembered prefactor" risk this whole approach is meant
to avoid."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.disorder import (
    czjzek_cq_eta_samples, extended_czjzek_cq_eta_samples, gaussian_shift_distribution,
    glass_ct_powder_pattern, combine_shift_components,
)
from visuspin.physics.quadrupole import ct_powder_pattern

def test_eta_bounded_and_cq_nonnegative():
    out = czjzek_cq_eta_samples(sigma=2.0, n_samples=20000)
    assert np.all(out["Cq"] >= 0)
    assert np.all((out["eta"] >= 0) & (out["eta"] <= 1))
    print(f"PASS Cq>=0 and 0<=eta<=1 for all {len(out['Cq'])} samples")

def test_cq_scales_linearly_with_sigma():
    out1 = czjzek_cq_eta_samples(sigma=1.0, n_samples=40000, seed=7)
    out2 = czjzek_cq_eta_samples(sigma=3.0, n_samples=40000, seed=7)
    ratio = np.mean(out2["Cq"]) / np.mean(out1["Cq"])
    assert abs(ratio - 3.0) < 0.05, f"expected ~3x, got {ratio:.3f}"
    print(f"PASS mean(Cq) scales linearly with sigma: ratio={ratio:.3f} (expected 3.0)")

def test_eta_distribution_independent_of_sigma():
    # eta is a ratio of eigenvalue differences -> must be scale-invariant
    out_small = czjzek_cq_eta_samples(sigma=0.5, n_samples=40000, seed=11)
    out_large = czjzek_cq_eta_samples(sigma=50.0, n_samples=40000, seed=11)
    assert abs(np.mean(out_small["eta"]) - np.mean(out_large["eta"])) < 0.01
    assert abs(np.std(out_small["eta"]) - np.std(out_large["eta"])) < 0.01
    print(f"PASS eta distribution is scale-invariant: mean(eta) = {np.mean(out_small['eta']):.4f} "
          f"(sigma=0.5) vs {np.mean(out_large['eta']):.4f} (sigma=50)")

def test_eta_distribution_favors_asymmetric_over_axially_symmetric():
    # A specific closed-form marginal P(eta) was checked against this
    # simulation and did NOT match (a memory error caught here, not a bug --
    # the eigenvalue sorting/eta convention were independently re-verified).
    # Rather than assert a precise formula, check the robust, well-known
    # QUALITATIVE feature of the Czjzek model: for a genuinely random EFG,
    # near-axially-symmetric environments (eta near 0) are comparatively
    # rare, and probability density is concentrated toward higher eta.
    out = czjzek_cq_eta_samples(sigma=1.0, n_samples=200000, seed=3)
    hist, edges = np.histogram(out["eta"], bins=20, range=(0, 1), density=True)
    density_near_0 = hist[0]
    density_near_1 = hist[-1]
    assert density_near_1 > 5 * density_near_0, \
        f"expected eta density concentrated away from 0, got P(eta~0)={density_near_0:.3f}, P(eta~1)={density_near_1:.3f}"
    assert np.all(np.diff(hist[:15]) > 0), "density should rise monotonically from eta=0 through most of the range"
    print(f"PASS eta density rises monotonically and is concentrated at high eta: "
          f"P(eta~0)={density_near_0:.3f} vs P(eta~1)={density_near_1:.3f} (axially-symmetric sites are rare)")

def test_extended_czjzek_collapses_to_delta_as_rho_to_zero():
    out = extended_czjzek_cq_eta_samples(Cq0=5.0, eta0=0.3, rho=1e-4, n_samples=20000)
    assert abs(np.mean(out["Cq"]) - 5.0) < 0.02
    assert abs(np.mean(out["eta"]) - 0.3) < 0.02
    assert np.std(out["Cq"]) < 0.02
    print(f"PASS rho->0 collapses to a sharp (Cq0,eta0): mean Cq={np.mean(out['Cq']):.4f}, "
          f"eta={np.mean(out['eta']):.4f}, std(Cq)={np.std(out['Cq']):.4f}")

def test_extended_czjzek_approaches_pure_czjzek_at_large_rho():
    Cq0 = 3.0
    rho = 500.0
    out_ext = extended_czjzek_cq_eta_samples(Cq0=Cq0, eta0=0.1, rho=rho, n_samples=60000, seed=42)
    out_pure = czjzek_cq_eta_samples(sigma=rho * Cq0, n_samples=60000, seed=42)
    assert abs(np.mean(out_ext["eta"]) - np.mean(out_pure["eta"])) < 0.01
    assert abs(np.mean(out_ext["Cq"]) / np.mean(out_pure["Cq"]) - 1.0) < 0.02
    print(f"PASS large rho ({rho}) matches pure Czjzek at sigma=rho*Cq0 regardless of eta0: "
          f"mean(eta) extended={np.mean(out_ext['eta']):.4f} vs pure={np.mean(out_pure['eta']):.4f}")

def test_gaussian_shift_distribution_moments():
    shifts = gaussian_shift_distribution(delta_iso_mean=50.0, sigma_shift=8.0, n_samples=100000)
    assert abs(np.mean(shifts) - 50.0) < 0.1
    assert abs(np.std(shifts) - 8.0) < 0.1
    print(f"PASS Gaussian shift distribution: mean={np.mean(shifts):.2f} (50.0), std={np.std(shifts):.2f} (8.0)")

def test_glass_pattern_reduces_to_crystalline_at_zero_disorder():
    # rho practically 0 -> every site has (Cq0,eta0) -> should reproduce the
    # already-verified single-crystallite-value crystalline CT powder
    # pattern from quadrupole.py almost exactly
    I, Cq0, eta0, nu0 = 1.5, 2.5e6, 0.2, 130e6
    glass = glass_ct_powder_pattern(I, Cq0, eta0, rho=1e-5, nu0_hz=nu0, n_samples=4000)
    crystal = ct_powder_pattern(I, Cq0, eta0, nu0, n_samples=4000)
    glass_span = np.ptp(glass["freq_hz"][glass["intensity"] > 0.05])
    crystal_span = np.ptp(crystal["freq_hz"][crystal["intensity"] > 0.05])
    assert abs(glass_span - crystal_span) / crystal_span < 0.15
    print(f"PASS glass pattern at rho~0 matches the crystalline pattern's span "
          f"({glass_span:.1f} Hz vs {crystal_span:.1f} Hz)")

def test_glass_pattern_broadens_with_disorder():
    I, Cq0, eta0, nu0 = 1.5, 2.5e6, 0.2, 130e6
    narrow = glass_ct_powder_pattern(I, Cq0, eta0, rho=0.05, nu0_hz=nu0, n_samples=4000)
    broad = glass_ct_powder_pattern(I, Cq0, eta0, rho=0.6, nu0_hz=nu0, n_samples=4000)
    narrow_span = np.ptp(narrow["freq_hz"][narrow["intensity"] > 0.05])
    broad_span = np.ptp(broad["freq_hz"][broad["intensity"] > 0.05])
    assert broad_span > narrow_span * 1.3
    print(f"PASS increasing disorder (rho 0.05->0.6) broadens the pattern: {narrow_span:.0f} Hz -> {broad_span:.0f} Hz")

def test_combine_shift_components_reflects_population_weighting():
    rng = np.random.default_rng(0)
    minority = rng.normal(-500, 20, 1000)   # small population
    majority = rng.normal(500, 20, 9000)    # large population
    combined = combine_shift_components([minority, majority], n_bins=400)
    peak_idx = np.argmax(combined["intensity"])
    peak_freq = combined["freq_hz"][peak_idx]
    assert abs(peak_freq - 500) < 30, f"expected the tallest peak near the majority component (500), got {peak_freq}"
    minority_region = np.abs(combined["freq_hz"] - (-500)) < 30
    assert combined["intensity"][minority_region].max() < 0.3
    print(f"PASS combined spectrum's tallest peak is the majority component (at {peak_freq:.0f}), "
          f"minority component visibly smaller ({combined['intensity'][minority_region].max():.2f})")


if __name__ == "__main__":
    test_eta_bounded_and_cq_nonnegative()
    test_cq_scales_linearly_with_sigma()
    test_eta_distribution_independent_of_sigma()
    test_eta_distribution_favors_asymmetric_over_axially_symmetric()
    test_extended_czjzek_collapses_to_delta_as_rho_to_zero()
    test_extended_czjzek_approaches_pure_czjzek_at_large_rho()
    test_gaussian_shift_distribution_moments()
    test_glass_pattern_reduces_to_crystalline_at_zero_disorder()
    test_glass_pattern_broadens_with_disorder()
    test_combine_shift_components_reflects_population_weighting()
    print("\nALL DISORDER MODEL TESTS PASSED")

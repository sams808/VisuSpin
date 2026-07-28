"""Verification of the multiplet/decoupling teaching module against exact
first-order multiplet counting rules."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.decoupling import multiplet_spectrum, decoupled_spectrum

def _find_peaks(freqs, spec, thresh=0.15, min_separation=5):
    raw = []
    for i in range(2, len(spec) - 2):
        if spec[i] > thresh and spec[i] >= spec[i-1] and spec[i] >= spec[i+1]:
            raw.append((freqs[i], spec[i]))
    # merge plateau/adjacent-grid-point ties (discretisation artifact, not
    # physically distinct peaks) into a single peak
    df = freqs[1] - freqs[0]
    merged = []
    for f, v in raw:
        if merged and abs(f - merged[-1][0]) < min_separation * df:
            if v > merged[-1][1]:
                merged[-1] = (f, v)
        else:
            merged.append((f, v))
    return merged

def test_doublet_from_one_coupled_spin():
    J = 140.0
    spec = multiplet_spectrum(J, n_coupled_spins=1, linewidth_hz=3.0, n_points=4000)
    peaks = _find_peaks(spec["freq_hz"], spec["intensity"])
    assert len(peaks) == 2, f"expected a doublet (2 lines), found {len(peaks)}"
    freqs = sorted(p[0] for p in peaks)
    assert abs((freqs[1] - freqs[0]) - J) < 1.0, f"doublet spacing {freqs[1]-freqs[0]} != J={J}"
    assert abs(peaks[0][1] - peaks[1][1]) < 0.05, "doublet lines should have equal (1:1) intensity"
    print(f"PASS n=1 coupled spin gives a 1:1 doublet spaced {freqs[1]-freqs[0]:.1f} Hz (J={J} Hz)")

def test_triplet_1_2_1_from_two_coupled_spins():
    J = 100.0
    spec = multiplet_spectrum(J, n_coupled_spins=2, linewidth_hz=2.0, n_points=6000)
    peaks = sorted(_find_peaks(spec["freq_hz"], spec["intensity"]), key=lambda p: p[0])
    assert len(peaks) == 3, f"expected a triplet, found {len(peaks)}"
    ratios = [p[1] for p in peaks]
    assert abs(ratios[0] - 0.5) < 0.03 and abs(ratios[1] - 1.0) < 0.03 and abs(ratios[2] - 0.5) < 0.03, \
        f"expected 1:2:1 (normalised 0.5:1:0.5), got {ratios}"
    print(f"PASS n=2 coupled spins give a 1:2:1 triplet, normalised intensities {[round(r,2) for r in ratios]}")

def test_quartet_1_3_3_1_from_three_coupled_spins():
    J = 80.0
    spec = multiplet_spectrum(J, n_coupled_spins=3, linewidth_hz=1.5, n_points=8000)
    peaks = sorted(_find_peaks(spec["freq_hz"], spec["intensity"]), key=lambda p: p[0])
    assert len(peaks) == 4, f"expected a quartet, found {len(peaks)}"
    ratios = [round(p[1] / peaks[0][1], 2) for p in peaks]
    assert ratios == [1.0, 3.0, 3.0, 1.0], f"expected 1:3:3:1 ratios, got {ratios}"
    print(f"PASS n=3 coupled spins give a 1:3:3:1 quartet, ratios {ratios}")

def test_decoupling_collapses_to_single_line_at_centroid():
    spec = decoupled_spectrum(center_hz=250.0, linewidth_hz=15.0, residual_coupling_hz=0.0, n_points=2000)
    peaks = _find_peaks(spec["freq_hz"], spec["intensity"])
    assert len(peaks) == 1, f"perfect decoupling should give a single line, found {len(peaks)}"
    assert abs(peaks[0][0] - 250.0) < 1.0
    assert abs(spec["effective_linewidth_hz"] - 15.0) < 1e-9
    print(f"PASS ideal decoupling: single line at centroid {peaks[0][0]:.1f} Hz, linewidth unchanged (15.0 Hz)")

def test_imperfect_decoupling_broadens_in_quadrature():
    natural_lw = 15.0
    residual = 40.0
    spec = decoupled_spectrum(linewidth_hz=natural_lw, residual_coupling_hz=residual)
    expected = np.sqrt(natural_lw**2 + residual**2)
    assert abs(spec["effective_linewidth_hz"] - expected) < 1e-9
    assert spec["effective_linewidth_hz"] > natural_lw
    print(f"PASS imperfect decoupling broadens linewidth to {spec['effective_linewidth_hz']:.1f} Hz "
          f"(quadrature sum of natural {natural_lw} Hz and residual {residual} Hz)")

if __name__ == "__main__":
    test_doublet_from_one_coupled_spin()
    test_triplet_1_2_1_from_two_coupled_spins()
    test_quartet_1_3_3_1_from_three_coupled_spins()
    test_decoupling_collapses_to_single_line_at_centroid()
    test_imperfect_decoupling_broadens_in_quadrature()
    print("\nALL DECOUPLING TESTS PASSED")

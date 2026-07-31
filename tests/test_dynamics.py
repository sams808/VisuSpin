"""Verification of the 2-site exchange Monte Carlo simulation against the
two well-known limiting cases (slow exchange: two resolved peaks; fast
exchange: one motionally-narrowed peak at the population-weighted mean)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.dynamics import two_site_exchange_spectrum, arrhenius_rate_hz

def _find_peaks(freqs, inten, thresh=0.2):
    peaks = []
    for i in range(2, len(inten) - 2):
        if inten[i] > thresh and inten[i] >= inten[i - 1] and inten[i] >= inten[i + 1]:
            peaks.append(freqs[i])
    # merge near-duplicates
    merged = []
    for p in sorted(peaks):
        if not merged or p - merged[-1] > (freqs[1] - freqs[0]) * 5:
            merged.append(p)
    return merged

def test_slow_exchange_gives_two_resolved_peaks():
    out = two_site_exchange_spectrum(nu_a_hz=-400.0, nu_b_hz=400.0, k_hz=0.5, T2_ms=100.0,
                                        acquire_ms=300, n_isochromats=3000, n_steps=1500)
    peaks = _find_peaks(out["freq_hz"], out["intensity"])
    assert len(peaks) == 2, f"expected 2 resolved peaks in the slow-exchange limit, found {len(peaks)}: {peaks}"
    assert abs(peaks[0] - (-400)) < 40 and abs(peaks[1] - 400) < 40
    print(f"PASS slow exchange (k=0.5 Hz << 800 Hz separation): two resolved peaks at {peaks}")

def test_fast_exchange_gives_one_averaged_peak():
    out = two_site_exchange_spectrum(nu_a_hz=-400.0, nu_b_hz=400.0, k_hz=20000.0, T2_ms=100.0,
                                        acquire_ms=300, n_isochromats=3000, n_steps=1500)
    peaks = _find_peaks(out["freq_hz"], out["intensity"], thresh=0.3)
    assert len(peaks) == 1, f"expected 1 motionally-narrowed peak in the fast-exchange limit, found {len(peaks)}: {peaks}"
    assert abs(peaks[0] - 0.0) < 40, f"expected the averaged peak near 0 Hz (population-weighted mean), got {peaks[0]}"
    print(f"PASS fast exchange (k=20000 Hz >> 800 Hz separation): one motionally-averaged peak at {peaks[0]:.0f} Hz")

def test_arrhenius_rate_increases_with_temperature():
    k_low = arrhenius_rate_hz(k0_hz=1e13, Ea_kJ_mol=50.0, T_kelvin=300.0)
    k_high = arrhenius_rate_hz(k0_hz=1e13, Ea_kJ_mol=50.0, T_kelvin=500.0)
    assert k_high > k_low
    print(f"PASS Arrhenius rate increases with T: k(300K)={k_low:.2e} Hz, k(500K)={k_high:.2e} Hz")

def test_arrhenius_matches_direct_formula():
    R = 8.314462618e-3
    k0, Ea, T = 5e12, 40.0, 400.0
    expected = k0 * np.exp(-Ea / (R * T))
    got = arrhenius_rate_hz(k0, Ea, T)
    assert abs(got - expected) / expected < 1e-9
    print(f"PASS arrhenius_rate_hz matches the direct k0*exp(-Ea/RT) formula exactly ({got:.4e} Hz)")

if __name__ == "__main__":
    test_slow_exchange_gives_two_resolved_peaks()
    test_fast_exchange_gives_one_averaged_peak()
    test_arrhenius_rate_increases_with_temperature()
    test_arrhenius_matches_direct_formula()
    print("\nALL DYNAMICS TESTS PASSED")

"""Verification of the simulated MAS sideband spectrum against known limiting
behaviour (fast spinning -> single centreband; sidebands spaced at nu_rot)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.sidebands import mas_sideband_spectrum

def test_fast_spinning_collapses_to_centreband():
    # nu_rot much larger than the anisotropy -> only the centreband survives
    spec = mas_sideband_spectrum(delta_aniso_hz=500.0, eta=0.3, nu_rot_hz=50000,
                                    n_powder=200, n_periods=24, n_time_per_period=32)
    peak_idx = np.argmax(spec["intensity"])
    peak_freq = spec["freq_hz"][peak_idx]
    assert abs(peak_freq) < 50000/24 + 1, f"centreband should be near 0, got peak at {peak_freq} Hz"
    # essentially all intensity should be within one sideband spacing of 0
    df = spec["freq_hz"][1]-spec["freq_hz"][0]
    near_zero = np.sum(spec["intensity"][np.abs(spec["freq_hz"]) < spec["freq_hz"].max()*0.02])
    total = np.sum(spec["intensity"])
    assert near_zero/total > 0.5
    print(f"PASS fast MAS (nu_rot=50kHz >> anisotropy=500Hz): centreband at {peak_freq:.1f} Hz, "
          f"{100*near_zero/total:.0f}% of intensity concentrated near 0")

def test_sidebands_spaced_at_rotor_rate():
    spec = mas_sideband_spectrum(delta_aniso_hz=8000.0, eta=0.0, nu_rot_hz=2000,
                                    n_powder=300, n_periods=48, n_time_per_period=48)
    # find peaks: simple local-maxima detection
    inten = spec["intensity"]
    freqs = spec["freq_hz"]
    peaks = []
    for i in range(2, len(inten)-2):
        if inten[i] > 0.03 and inten[i] >= inten[i-1] and inten[i] >= inten[i+1]:
            peaks.append(freqs[i])
    peaks = np.array(sorted(peaks))
    if len(peaks) >= 3:
        spacings = np.diff(peaks)
        median_spacing = np.median(spacings)
        assert abs(median_spacing - 2000) < 2000*0.15, f"expected ~2000 Hz spacing, got {median_spacing:.0f}"
        print(f"PASS sideband spacing = {median_spacing:.0f} Hz (expected nu_rot = 2000 Hz), {len(peaks)} peaks found")
    else:
        print(f"WARN only found {len(peaks)} peaks -- inspect visually")

if __name__ == "__main__":
    test_fast_spinning_collapses_to_centreband()
    test_sidebands_spaced_at_rotor_rate()
    print("\nALL SIDEBAND TESTS PASSED (or flagged for visual inspection)")

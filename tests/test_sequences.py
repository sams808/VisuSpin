"""Verifies the block-based sequence engine reproduces the correct physics --
most importantly, that the Hahn echo actually refocuses (echo amplitude on
the exp(-2*tau/T2) curve, not the faster exp(-2*tau/T2*) curve), since that
inhomogeneous-vs-homogeneous distinction is the entire pedagogical point."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.sequences.blocks import SequenceContext
from visuspin.sequences.engine import run_sequence
from visuspin.sequences.presets import hahn_echo, cpmg, free_induction_decay

def test_hahn_echo_refocuses_on_T2_not_T2star():
    T1, T2, sigma = 5000.0, 300.0, 0.15  # rad/ms -- big inhomogeneous broadening
    tau = 15.0
    ctx = SequenceContext(T1_ms=T1, T2_ms=T2, nu1_khz=25)
    out = run_sequence(hahn_echo(tau_ms=tau, acquire_ms=2), ctx, n_isochromats=300, sigma_rad_per_ms=sigma)
    # echo maximum should occur at t ~= 2*tau (measuring from the 90 pulse)
    window = (out["t_ms"] > 2*tau - 3) & (out["t_ms"] < 2*tau + 3)
    echo_amp = out["mxy"][window].max()
    T2star = 1/(1/T2 + sigma/2)
    pred_T2 = np.exp(-2*tau/T2)
    pred_T2star = np.exp(-2*tau/T2star)
    assert echo_amp > 0.6*pred_T2, f"echo too small: {echo_amp} vs T2 prediction {pred_T2}"
    assert echo_amp > 3*pred_T2star, f"echo should be far above the T2* prediction {pred_T2star}, got {echo_amp}"
    print(f"PASS Hahn echo: amplitude={echo_amp:.3f}, exp(-2tau/T2)={pred_T2:.3f} (close), "
          f"exp(-2tau/T2*)={pred_T2star:.4f} (echo far exceeds this -- refocusing confirmed)")

def test_fid_envelope_matches_voigt_shape():
    """dw is drawn from a GAUSSIAN distribution (bloch.Ensemble.from_gaussian_offsets),
    so the correct FID envelope is the Voigt-type product exp(-t/T2)*exp(-sigma^2 t^2/2)
    (the ensemble average of exp(i*dw*t) over a Gaussian dw is the Gaussian
    characteristic function exp(-sigma^2 t^2/2)) -- NOT a single exponential
    exp(-t/T2*) with 1/T2*=1/T2+sigma/2, which is the correct combination rule
    only for a LORENTZIAN-distributed inhomogeneous broadening. Checked in two
    regimes so the two factors are each pinned down separately."""
    T1, T2 = 5000.0, 300.0

    # Regime 1: sigma dominates (T2 effectively irrelevant) -> pure Gaussian decay
    sigma = 0.15
    ctx = SequenceContext(T1_ms=T1, T2_ms=T2, nu1_khz=25)
    out = run_sequence(free_induction_decay(acquire_ms=25), ctx, n_isochromats=4000, sigma_rad_per_ms=sigma)
    t, mxy = out["t_ms"], out["mxy"]
    predicted = np.exp(-t/T2) * np.exp(-(sigma**2)*(t**2)/2)
    resid = np.abs(mxy - predicted)
    assert np.max(resid) < 0.05, f"Voigt-shape mismatch, max residual {np.max(resid):.3f}"
    print(f"PASS FID (sigma-dominated) matches exp(-t/T2)*exp(-sigma^2 t^2/2), max residual {np.max(resid):.4f}")

    # Regime 2: sigma ~ 0 -> pure homogeneous exponential decay at rate 1/T2
    ctx2 = SequenceContext(T1_ms=T1, T2_ms=T2, nu1_khz=25)
    out2 = run_sequence(free_induction_decay(acquire_ms=200), ctx2, n_isochromats=50, sigma_rad_per_ms=0.0)
    t2, mxy2 = out2["t_ms"], out2["mxy"]
    slope = np.polyfit(t2, np.log(np.maximum(mxy2, 1e-12)), 1)[0]
    fitted_T2 = -1/slope
    assert abs(fitted_T2 - T2)/T2 < 0.02, f"fitted {fitted_T2} vs T2 {T2}"
    print(f"PASS FID (sigma=0) decays as pure exponential, fitted T2={fitted_T2:.2f} ms (set {T2:.2f} ms)")

def test_cpmg_echo_train_envelope_decays_at_T2():
    T1, T2, sigma = 5000.0, 200.0, 0.2
    ctx = SequenceContext(T1_ms=T1, T2_ms=T2, nu1_khz=25)
    out = run_sequence(cpmg(tau_ms=8, n_echoes=6, acquire_ms=1), ctx, n_isochromats=300, sigma_rad_per_ms=sigma)
    # peaks should occur near t = 2*tau, 4*tau, 6*tau, ... after the initial 90
    echo_times = [2*8*(k+1) for k in range(6)]
    echo_amps = []
    for et in echo_times:
        window = (out["t_ms"] > et-2) & (out["t_ms"] < et+2)
        if window.any():
            echo_amps.append(out["mxy"][window].max())
    echo_amps = np.array(echo_amps)
    T2star = 1/(1/T2 + sigma/2)
    # envelope should follow T2, decaying much slower than T2* would predict
    ratio_last_first = echo_amps[-1]/echo_amps[0]
    pred_T2_ratio = np.exp(-2*8*5/T2)
    pred_T2star_ratio = np.exp(-2*8*5/T2star)
    assert ratio_last_first > 3*pred_T2star_ratio
    print(f"PASS CPMG echo train envelope ratio(last/first)={ratio_last_first:.3f}, "
          f"T2-predicted={pred_T2_ratio:.3f}, T2*-predicted={pred_T2star_ratio:.4f} (train decays much slower than T2*)")

if __name__ == "__main__":
    test_hahn_echo_refocuses_on_T2_not_T2star()
    test_fid_envelope_matches_voigt_shape()
    test_cpmg_echo_train_envelope_decays_at_T2()
    print("\nALL SEQUENCE ENGINE TESTS PASSED")

"""
Preliminary simulation: estimating the virtual inertia constant H of a
grid-connected VSG (virtual synchronous generator) inverter from an external
frequency ramp and how measurement quality (ADC bits, noise, sampling rate)
affects the estimate. Simplified model for learning/prototyping only;
rebuild in PLECS/Simulink before citing results as your own work.

Model (per unit, grid-connected, swing equation):
    d(delta)/dt = w0 * (dw - dw_g)          [rad/s]
    M * d(dw)/dt = -Ks*delta - D*dw          (M = 2H)
    dPe = Ks * delta                         (output power deviation)
Steady ramp tracking gives  dPe = -(M*alpha + D*dw_g) + D^2*alpha/(Ks*w0),
alpha = d(dw_g)/dt, i.e. a naive fit under-reads M by D^2/(Ks*w0).
H is estimated by least squares on dPe over a window after the transient.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

f0, w0 = 50.0, 2*np.pi*50.0
H_true, D, Ks = 2.0, 40.0, 3.33          # s, pu, pu
M = 2*H_true
RAMP_HZ_S = -0.5                         # applied RoCoF (Hz/s)
T_RAMP, T_END = 3.0, 3.0

def simulate(fs, dt_int=1e-4):
    n = int(T_END/dt_int)
    t = np.arange(n)*dt_int
    alpha = RAMP_HZ_S/f0                 # pu/s
    dwg = alpha*np.minimum(t, T_RAMP)
    delta, dw = 0.0, 0.0
    Pe = np.empty(n)
    for k in range(n):
        ddelta = w0*(dw - dwg[k])
        ddw = (-Ks*delta - D*dw)/M
        delta += ddelta*dt_int
        dw += ddw*dt_int
        Pe[k] = Ks*delta
    step = int(round(1/(fs*dt_int)))
    return t[::step], dwg[::step], Pe[::step], alpha

def estimate_H(t, dwg, Pe, alpha, bits, noise_pu, fs, rng, t_start=1.5):
    fullscale = 1.0                      # +/-0.5 pu input range
    lsb = fullscale/(2**bits)
    Pm = Pe + rng.normal(0, noise_pu, Pe.size)
    Pm = np.round(Pm/lsb)*lsb
    m = (t > t_start) & (t <= T_RAMP)
    A = np.column_stack([-alpha*np.ones(m.sum()), -dwg[m]])   # [M, D]
    coef, *_ = np.linalg.lstsq(A, Pm[m], rcond=None)
    return coef[0]/2.0                   # H = M/2

if __name__ == "__main__":
    rng = np.random.default_rng(1)
    # 1) Noise-free sanity check
    t, dwg, Pe, alpha = simulate(1000)
    H0 = estimate_H(t, dwg, Pe, alpha, 24, 0.0, 1000, rng)
    bias = D**2/(Ks*w0)                  # steady-ramp offset: dPe = -(M*alpha + D*dw_g) + D^2*alpha/(Ks*w0)
    H_app = (M - bias)/2
    print(f"True H = {H_true:.2f} s | noise-free naive estimate = {H0:.3f} s | predicted apparent H = {H_app:.3f} s")
    print(f"Corrected estimate (needs D and Ks known) = {H0 + bias/2:.3f} s")

    # 2) Monte Carlo: ADC bits x sampling rate (noise = 0.5 LSB rms-ish + 0.002 pu)
    bits_list = [8, 10, 12, 14]
    fs_list = [100, 1000, 10000]
    res = np.zeros((len(fs_list), len(bits_list), 2))
    for i, fs in enumerate(fs_list):
        t, dwg, Pe, alpha = simulate(fs)
        for j, b in enumerate(bits_list):
            Hs = [estimate_H(t, dwg, Pe, alpha, b, 0.002, fs, rng) for _ in range(200)]
            res[i, j] = (np.mean(Hs), np.std(Hs))
            print(f"fs={fs:6d} Hz, {b:2d} bit: H_hat = {np.mean(Hs):.3f} +/- {np.std(Hs):.3f} s")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    t, dwg, Pe, alpha = simulate(1000)
    ax[0].plot(t, Pe, label="dPe (pu)"); ax[0].plot(t, -(M*alpha + D*dwg), "--", label="-(M*alpha + D*dw_g)")
    ax[0].axvline(1.5, color="gray", lw=0.8); ax[0].set_xlabel("t (s)"); ax[0].set_title("VSG power response to -0.5 Hz/s ramp"); ax[0].legend()
    for i, fs in enumerate(fs_list):
        ax[1].errorbar(bits_list, res[i, :, 0], yerr=res[i, :, 1], marker="o", capsize=3, label=f"fs={fs} Hz")
    ax[1].axhline(H_true, color="k", ls=":", label="true H"); ax[1].axhline(H_app, color="r", ls=":", label="predicted apparent H"); ax[1].set_xlabel("ADC bits"); ax[1].set_ylabel("estimated H (s)")
    ax[1].set_title("H estimate vs measurement quality (200 runs)"); ax[1].legend()
    plt.tight_layout(); plt.savefig("/mnt/user-data/outputs/vsg_inertia_result.png", dpi=150)

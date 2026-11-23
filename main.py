import scipy.signal
import numpy
import matplotlib

# File to experiment on

"""LMS adaptive line enhancer: ensemble-averaged learning curves.

x[n] = s[n] + i[n],  s = white Gaussian noise,  i = sinusoid (random phase per run)
ihat[n] = sum_k h[k,n] x[n-nD-k],   e[n] = x[n] - ihat[n]
h[k,n+1] = h[k,n] + mu e[n] x[n-nD-k]
"""
import numpy as np
import matplotlib.pyplot as plt


def lms_ale(x, M, nD, mu):
    """Run LMS on x. Returns e (length N) and h, a list of weight vectors:
    h[j] holds the weights h[:, n] at time n = nD + M + j; h[-1] is the final weight vector.
    """
    N = len(x)
    e = np.zeros(N)
    h = [np.zeros(M + 1)]  # weight history, h[0] = 0
    for n in range(nD + M, N):
        u = x[n - nD - np.arange(M + 1)]  # [x[n-nD], ..., x[n-nD-M]]
        e[n] = x[n] - h[-1] @ u  # e[n] = x[n] - ihat[n]
        h.append(h[-1] + mu * e[n] * u)  # LMS update -> h[:, n+1]
    return e, h


# ---------------- experiment parameters ----------------
rng = np.random.default_rng(412)
N, runs = 5000, 100  # samples per run, independent runs
M, nD = 15, 2  # 16 taps, delay (white-noise case)
SIR_dB = -10  # SIR = 10 log10(sigma_s^2 / (A^2/2))
A = np.sqrt(2 * 10 ** (-SIR_dB / 10))  # interference amplitude (~4.47)
w0 = 0.2 * np.pi  # interference frequency (rad/sample)
mus = [1e-4, 3e-4, 1e-3, 3e-3]  # all below 2/((M+1)*var(x)) ~ 0.0119
smooth = 50  # moving-average length for display only

n = np.arange(N)
mse = {mu: np.zeros(N) for mu in mus}  # E{e^2[n]}
res = {mu: np.zeros(N) for mu in mus}  # E{(e[n]-s[n])^2}, residual interference

for r in range(runs):
    s = rng.standard_normal(N)  # sigma_s^2 = 1
    i = A * np.cos(w0 * n + rng.uniform(0, 2 * np.pi))  # random phase each run
    x = s + i
    for mu in mus:  # same realization for every mu
        e, h = lms_ale(x, M, nD, mu)
        mse[mu] += e ** 2 / runs
        res[mu] += (e - s) ** 2 / runs

# ---------------- plot learning curves ----------------
start = nD + M  # e[n] is undefined before this
ma = lambda p: np.convolve(p, np.ones(smooth) / smooth, mode="valid")
db = lambda p: 10 * np.log10(ma(p[start:]))  # "valid": no edge artifacts
nplot = n[start + smooth // 2: start + smooth // 2 + N - start - smooth + 1]
fig, ax = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
for mu in mus:
    ax[0].plot(nplot, db(mse[mu]), lw=0.8, label=f"μ = {mu:g}")
    ax[1].plot(nplot, db(res[mu]), lw=0.8, label=f"μ = {mu:g}")
ax[0].axhline(0, color="k", ls="--", lw=0.8, label="σ_s² (ideal floor)")
ax[0].set_ylabel("E{e²[n]} (dB)")
ax[0].set_title(f"LMS ALE learning curves ({runs} runs, M+1 = {M + 1}, "
                f"nD = {nD}, SIR = {SIR_dB} dB, {smooth}-pt smoothing)")
ax[1].set_ylabel("E{(e[n] − s[n])²} (dB)")
ax[1].set_xlabel("n (samples)")
for a in ax:
    a.grid(alpha=0.3)
    a.legend(fontsize=8)
#fig.tight_layout()
plt.show()

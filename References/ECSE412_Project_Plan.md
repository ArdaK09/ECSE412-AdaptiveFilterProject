# ECSE 412/512 Term Project: Adaptive Narrowband Interference Suppression
**Project plan: concepts, materials, tool choice, timeline**
Prepared Sunday, Nov 15, 2026. **Due: Friday, Dec 4, 2026, before 11:59 pm** (printed report + uploaded folder).
You have **20 days**, and they overlap with end-of-term problem sets and final exam prep.

---

## 1. What you are building

Observation: `x[n] = s[n] + i[n]`, where `s` is wideband (the signal you want) and `i` is narrowband (the interference).

This structure is the **Adaptive Line Enhancer (ALE)** from Widrow et al. (1975), used here as a self-tuning notch filter:

```
x[n] ──┬──────────────────────────────(-)──► e[n] ≈ s[n]   (the output you keep)
       │                               ▲
       └─► z^(−nD) ─► FIR h[k,n] ──► î[n]
                     (adapted by LMS / RLS using e[n])
```

- The delay `nD` decorrelates the wideband `s`, so the filter can only "predict" the narrowband `i`.
- The filter minimizes E{e²[n]}. Because `s` is unpredictable from the past, the minimum is reached when `î ≈ i`.
- The overall input→output system after convergence is **H(z) = 1 − z^(−nD) W(z)**, which should show a **notch at the interference frequency**. Plotting this is one of the clearest figures you can put in the report.

> ⚠️ **Small inconsistency in the handout:** the filter-output equation is written as `î[n] = Σ h[k,n] x[n−k]`, but the LMS update (and Fig. 1) use the delayed input `x[n−nD−k]`. Use **`x[n−nD−k]` in both** and state this explicitly in Section 3 of your report.

### Required deliverables (from the handout)
1. LMS, then RLS, implementation of the structure above.
2. **Stationary test:** `s` = white Gaussian noise, `i` = fixed sinusoid. Plot **learning curves** (error power vs. time, ensemble-averaged over independent runs) for several values of the memory parameter.
3. **Non-stationary tests:**
   a. `s` = speech, `i` = fixed sinusoid (include audio files)
   b. `s` = white noise, `i` = sinusoid with a **time-varying frequency** (e.g., a chirp)
4. **Discussion:** effect of the memory parameter (μ for LMS, λ for RLS) and of SNR on convergence, plus a direct LMS vs. RLS comparison.
5. **Report:** 12–14 pages of text plus cover page, plus a commented code listing. IEEE references, Times New Roman 12 pt, 1.5 spacing, specific margins (see §6).
6. **Reproducible package:** the professor must be able to run your code on a data file and listen to the output. **Test it on another computer before you submit.**

---

## 2. Concepts you need (in learning order)

### Tier 1: Prerequisites (review quickly; most should be familiar)
| Concept | Why it matters here | Where |
|---|---|---|
| FIR filters, convolution, frequency response H(e^jω) | The adaptive filter is a time-varying FIR filter, and you will plot its final frequency response | O&S Ch. 2, 5 |
| Z-transform, zeros on the unit circle | A notch is a pair of zeros near e^(±jω₀) | O&S Ch. 3, 5 |
| **Random signals:** mean, autocorrelation r_x[k], WSS, white noise, power spectral density | Every adaptive filter result is stated in terms of autocorrelation/PSD | O&S §2.10 and Appendix A; Haykin Ch. 1 |
| Autocorrelation of a sinusoid with random phase: r[k] = (A²/2)cos(ω₀k) | Explains why `i` stays correlated at every lag (it is predictable) while white `s` has r[k] = 0 for k ≠ 0 | Haykin Ch. 1 |
| Spectrograms / STFT | Best way to show the speech and chirp results visually | O&S Ch. 10 (time-dependent Fourier analysis) |

### Tier 2: Core adaptive filtering theory (the main learning effort)
| Concept | Key takeaways |
|---|---|
| **Wiener filter / normal equations** | Optimal weights **R w = p**, where R is the input autocorrelation matrix and p is the cross-correlation vector. The MSE is quadratic in w, so it has a single minimum. |
| **Linear prediction** | The ALE is a linear predictor with lookahead nD. A sinusoid is perfectly predictable from 2 past samples. |
| **Steepest descent** | Iteration w ← w + μ(p − Rw). Stability requires 0 < μ < 2/λ_max. Each mode converges with time constant ≈ 1/(2μλ_i). |
| **Eigenvalue spread χ(R) = λ_max/λ_min** | A strong sinusoid in white noise produces a large spread, so LMS converges slowly on some modes. **This is the main reason RLS will outperform LMS in your plots.** |
| **LMS algorithm** | Replace the true gradient with an instantaneous estimate: `w[n+1] = w[n] + μ e[n] u[n]`. Practical stability bound: 0 < μ < 2 / ((M+1)·σ_x²). |
| **Misadjustment** | Excess MSE above the Wiener minimum, approximately μ(M+1)σ_x²/2. This is the **speed vs. accuracy trade-off**: larger μ converges faster but leaves a noisier steady state. |
| **NLMS** (optional but useful) | μ_n = μ̃ / (ε + ‖u[n]‖²). It makes μ insensitive to signal level, which matters for speech because its power varies over time. |
| **Least squares with exponential forgetting** | RLS minimizes Σ λ^(n−i) e²[i]. The effective memory is about 1/(1−λ) samples. |
| **RLS algorithm** | Recursive inverse-correlation update via the matrix inversion lemma. Converges in roughly 2(M+1) iterations, largely independent of eigenvalue spread. Costs O(M²) per sample vs. O(M) for LMS. |
| **Tracking vs. convergence** | In the non-stationary (chirp) case, a smaller λ or larger μ tracks better at the cost of noisier weights. RLS is not automatically better at tracking than LMS; this is a good discussion point. |

### Tier 3: Application-specific design choices
- **Choosing the delay nD:**
  - For white noise `s`, nD = 1 is already enough.
  - For speech, `s` is strongly correlated over a few ms, and voiced speech is quasi-periodic (pitch period 2.5–12.5 ms). Too small an nD will cancel part of the speech. Try nD equivalent to roughly 1–5 ms and evaluate by listening and with spectrograms.
- **Filter length M:** two taps can model one sinusoid. More taps give a narrower, deeper notch but raise misadjustment and the cost of RLS. Try M ∈ {8, 16, 32}.
- **SNR definition.** Here the "noise" is the interference, so define it explicitly, e.g. **SIR = 10 log₁₀(σ_s² / (A²/2))**, and sweep it from about −20 dB to +10 dB.
- **What to plot as the learning curve:**
  - The handout asks for E{e²[n]}, which converges to about σ_s² + excess MSE rather than to 0.
  - Also plot the **residual interference power E{(e[n] − s[n])²}**. You know `s` in simulation, and this curve converges toward 0, which is much clearer.
  - Use a log (dB) scale.
- **Ensemble averaging:** use 100–200 independent runs with a new noise realization and a **random sinusoid phase** in each run.
- **RLS initialization:** P[0] = δ⁻¹I with small δ (e.g., 0.01 relative to the input power), and w[0] = 0.

### Algorithm summary (put a version of this in Section 2 of the report)
Regressor: `u[n] = [x[n−nD], x[n−nD−1], …, x[n−nD−M]]ᵀ`

**LMS**
```
î[n]   = wᵀ[n] u[n]
e[n]   = x[n] − î[n]
w[n+1] = w[n] + μ e[n] u[n]
```

**RLS** (forgetting factor 0 < λ ≤ 1, P[0] = δ⁻¹ I)
```
k[n] = P[n−1] u[n] / (λ + uᵀ[n] P[n−1] u[n])     % gain vector
ξ[n] = x[n] − wᵀ[n−1] u[n]                       % a-priori error
w[n] = w[n−1] + k[n] ξ[n]
P[n] = λ⁻¹ ( P[n−1] − k[n] uᵀ[n] P[n−1] )
```
Each algorithm takes about 10–20 lines of code. Implement both **yourself**, without toolbox adaptive-filter objects: the report has to explain them, and the grader will read the listing.

---

## 3. Materials to read

### Required / primary
1. **S. Haykin, *Adaptive Filter Theory*, 4th ed., Prentice Hall, 2002** (reference [1] in the handout). Read these chapters in order:
   - Stochastic processes and models (autocorrelation matrix, eigenvalues)
   - Wiener filters
   - Linear prediction (skim)
   - Method of steepest descent
   - Least-mean-square (LMS) adaptive filters
   - Normalized LMS (short)
   - Method of least squares (skim)
   - **Recursive least-squares (RLS) adaptive filters**

   Chapter numbering differs between editions, so go by title. The McGill library should have copies; check the course reserve.
2. **B. Widrow et al., "Adaptive noise cancelling: Principles and applications," *Proc. IEEE*, vol. 63, no. 12, pp. 1692–1716, Dec. 1975** (reference [2]). Focus on the sections about **cancelling periodic interference without an external reference** and the **adaptive line enhancer / self-tuning filter**. That is exactly your structure. This paper is also your best source for the Introduction, and it is available through IEEE Xplore via the McGill library.
3. **Your ECSE 412 lecture slides on adaptive filtering** (Part III of the course: reference signal, cost function, recursive optimization, LMS, RLS). The prof's notation is what the grader will expect.

### Strongly recommended
4. **J. R. Zeidler et al., "Adaptive enhancement of multiple sinusoids in uncorrelated noise," *IEEE Trans. ASSP*, 1978.** Analysis of the ALE, including how M, μ, and SNR affect the notch. Very useful for Section 4 discussion.
5. **A. V. Oppenheim & R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed.** Random signals (§2.10, Appendix A) and time-dependent Fourier analysis / spectrograms (Ch. 10).
6. **P. S. R. Diniz, *Adaptive Filtering: Algorithms and Practical Implementation* (Springer).** A clear, more modern treatment of LMS/RLS, often accessible as an e-book through university Springer access.
7. **A. H. Sayed, *Fundamentals of Adaptive Filtering* (Wiley, 2003).** Rigorous; good for tracking analysis.

### For the Introduction (applications and existing solutions; cite 6–10 sources total)
- Fixed IIR notch filters (2nd-order, poles near the zeros) as the "classical" non-adaptive solution and why they fail when ω₀ is unknown or drifting
- Power-line (50/60 Hz) interference removal in ECG/EEG
- Narrowband jammer suppression in spread-spectrum / CDMA communications
- Tonal noise / hum removal in audio
- Search IEEE Xplore for terms like *"adaptive notch filter"*, *"adaptive line enhancer"*, *"narrowband interference suppression"*

### Test data
- **Speech:** your own recording (16 kHz or 8 kHz mono WAV, ~5–10 s) is the simplest and has no licensing issues. In MATLAB, `load mtlb` also gives a short built-in speech sample (Fs ≈ 7418 Hz). For a public corpus, LibriSpeech is freely licensed.
- **Chirp interference:** build it from the instantaneous phase, `i[n] = A·cos(φ[n])` with `φ[n] = Σ ω[k]`, using a linear sweep or a slow sinusoidal frequency modulation.

---

## 4. MATLAB or Python?

A MATLAB Example is given here of an [LMS implementation](https://www.mathworks.com/help/dsp/ug/adaptive-line-enhancer-ale.html).

**Things to add to make Python work:**
- Pin versions in `requirements.txt`.
- Use only `numpy`, `scipy`, `matplotlib`, and `soundfile`.
- Provide a single `../main.py` entry point and write WAV files rather than relying on live playback.
- Give exact setup commands in the appendix (`python -m venv .venv`, `pip install -r requirements.txt`).

### Suggested folder layout (same idea in either language)
```
ECSE512_Project_<Name>/
├── README.txt               % mirrors the 1-page appendix
├── main.m                   % runs everything, regenerates all figures + audio
├── lms_ale.m                % [e, ihat, W] = lms_ale(x, M, nD, mu)
├── rls_ale.m                % [e, ihat, W] = rls_ale(x, M, nD, lambda, delta)
├── exp1_stationary.m        % learning curves vs mu / lambda
├── exp2_snr_sweep.m         % effect of SIR
├── exp3_speech.m            % speech + fixed tone → WAV outputs
├── exp4_chirp.m             % time-varying frequency tracking
├── utils/                   % make_sinusoid, plot helpers, stft (if no toolbox)
├── data/                    % input speech file(s)
└── output/                  % figures (PDF/PNG) + processed WAV files
```
---

## 5. Recommended timeline (Nov 15 → Dec 4)

Key course dates: tutorials on Thu Nov 19 and **Thu Nov 26 (the last one)**; Prof. Champagne's office hours are Mon & Wed, 11:30–13:30 (McConnell 756).

| Phase | Dates | Goals | Done when… |
|---|---|---|---|
| **0. Ramp-up** | Sun Nov 15 – Tue Nov 17 | Re-read lecture slides on adaptive filtering. Read the Haykin Wiener, steepest-descent, and LMS chapters. Skim Widrow 1975 (ALE/periodic-interference sections). Choose the language, set up the folder structure and git repo. If in a pair, split roles. | You can explain on paper why the delay prevents cancelling `s`, and you can write the LMS equations from memory. |
| **1. LMS + stationary test** | Wed Nov 18 – Fri Nov 20 | Write `lms_ale`. Generate `s` (white Gaussian, σ²=1) and `i` (sinusoid, random phase). Single-run sanity check, then ensemble learning curves (100+ runs) for 3–4 μ values. Plot the converged \|H(e^jω)\| showing the notch. Compare against the Wiener solution `R⁻¹p` as a check. | Learning curves converge; larger μ is visibly faster but has a higher floor; the notch sits at ω₀. **Bring questions to the Thu Nov 19 tutorial.** |
| **2. RLS + comparison** | Sat Nov 21 – Mon Nov 23 | Write `rls_ale`. Learning curves for λ ∈ {0.95, 0.99, 0.999}. LMS vs. RLS on the same plot. SIR sweep (−20 to +10 dB) for both. Optionally, eigenvalue-spread vs. SIR. | RLS converges in ~2M samples, independent of SIR; LMS slows at high interference power. **Mon Nov 23 office hours:** show the prof your preliminary plots. |
| **3. Non-stationary tests** | Tue Nov 24 – Fri Nov 27 | **(a) Speech + fixed tone:** pick nD, write input/output WAVs, make before/after spectrograms, compute output SNR improvement. **(b) White noise + chirp:** show tracking for several μ/λ, plot weight evolution or instantaneous notch frequency vs. true frequency. | Audio files sound clean; chirp tracking plots show the trade-off. **Last tutorial Thu Nov 26.** |
| **4. Report writing** | Wed Nov 25 – Mon Nov 30 (overlaps Phase 3) | Write Sections 2 (Background) and 3 (Application) first, since they don't depend on results. Then Section 4 (Results) as figures finalize, then 1 (Intro), 5 (Conclusion), and the abstract last. | **Complete draft by Mon Nov 30.** |
| **5. Polish & package** | Tue Dec 1 – Wed Dec 2 | Proofread; check page count (12–14) and formatting. Insert the commented code listing. Write the 1-page appendix/README. **Clean-machine test:** copy the folder to a classmate's or lab computer and run `main` from scratch. | Code runs on another computer with no edits. Optional: **Wed Dec 2 office hours** for a final question. |
| **6. Submit** | Thu Dec 3 (target) / Fri Dec 4 (deadline, 11:59 pm) | Print the paper copy. Upload the folder: report PDF, code, input files, and processed output files. | Submitted with a day of buffer. Confirm the paper-copy drop-off location/time with the prof in advance, since you can't print at 11:58 pm. |

### Suggested daily effort
About 2–3 h/day during Phases 1–3 and 3–4 h/day during Phase 4. The code is small; **the experiments, figures, and writing take most of the time.** If you fall behind, cut optional items (NLMS, eigenvalue-spread analysis) before cutting the clean-machine test.

---

## 6. Report blueprint (12–14 pages of text)

| Section | Pages | Content |
|---|---|---|
| Cover page | — | Title, name(s), ID(s), date, 5–6 line abstract |
| Table of contents | — | |
| 1. Introduction | ≤ 2 | Problem statement; applications (audio hum, ECG power-line, comms jamming); existing solutions (fixed notch → adaptive notch / ALE); project goals; report overview |
| 2. Background | 3–4 | Wiener filter and normal equations → steepest descent → LMS (stability, misadjustment) → least squares with forgetting → RLS. Complexity comparison table. |
| 3. Application to NB interference | 3–4 | ALE structure (Fig. 1), role of nD and how you chose it, M, μ/λ, initialization, signal models, SIR definition, performance metrics (learning curve, residual interference, output SNR), H(z) = 1 − z^(−nD)W(z) |
| 4. Results & discussion | 3–4 | Learning curves vs. μ and λ; LMS vs. RLS; SIR sweep; converged notch response; speech spectrograms + reference to WAV files; chirp tracking |
| 5. Conclusion | ≤ 0.5 | Main findings, limitations, possible extensions (NLMS, IIR adaptive notch, multiple tones) |
| References | — | IEEE style |
| Appendix | ≤ 1 | How to install/run, file list, expected outputs |
| Code listing | — | Commented source code |

**Formatting:** 8.5×11 in, single column, black print; top margin 1.25 in, other margins 1 in; Times New Roman 12 pt, 1.5 line spacing; page numbers at the bottom except on the cover. LaTeX with an IEEE bibliography style, or Word with an equation editor and reference manager, both work.

### Figure checklist (about 8–10 figures is plenty)
- [ ] Block diagram of the ALE structure
- [ ] LMS learning curves for 3–4 μ values (dB scale, ensemble-averaged)
- [ ] RLS learning curves for 3 λ values
- [ ] LMS vs. RLS overlay at matched steady-state error
- [ ] Converged |H(e^jω)| showing the notch at ω₀
- [ ] Convergence time / steady-state error vs. SIR, for both algorithms
- [ ] Speech: spectrograms of x, e, and s (before/after)
- [ ] Chirp: spectrogram of the input + estimated vs. true interference frequency over time (or residual error power vs. time)
- [ ] (Optional) Weight trajectories w_k[n]

---

## 7. Common pitfalls

1. **Using the non-delayed input in the filter.** The regressor must be `x[n−nD−k]`.
2. **LMS diverging.** μ is too large relative to the input power. Normalize the signals or check μ < 2/((M+1)σ_x²).
3. **Single-run "learning curves."** These are too noisy. You must average over independent runs (fresh noise and random phase each run).
4. **Expecting e²[n] → 0.** It converges to about σ_s² plus misadjustment, since `e` is your estimate of `s`. Also plot the residual interference.
5. **Speech partially cancelled.** nD is too small. Increase it and listen.
6. **Clipping in output WAVs.** Scale outputs into [−1, 1] before `audiowrite`, using the same scale factor for input and output so they are comparable.
7. **Hard-coded absolute paths** or toolbox functions the grader may not have. List the required toolboxes in the README.
8. **Leaving the printed copy to the last minute.** The deadline includes a paper copy.



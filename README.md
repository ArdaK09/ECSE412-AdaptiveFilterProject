# ECSE412-AdaptiveFilterProject

## Opening/Running the **Python** Notebook

1) Create the python environment. *Must have python installed:* `python3 -m venv .venv`
2) Activate the environment
    - Windows
      - cmd: `.venv\Scripts\activate.bat`
      - Powershell: `.venv\Scripts\Activate.ps1`
    - Mac: `source .venv/bin/activate`
3) Download the required packages for the project `pip3  install -r requirements.txt`.
4) The above command should've installed jupyter which will run the notebook. To run the web interface: `jupyter notebook`
5) Navigate to your browser and  select the file of interest: `LMS.ipynb` or `RMS.ipynb`, then from the menu bar select *Run All*.

After these steps you should see the figures in the report and the implementation of the algorithms.

After being done, you can easily leave the python venv via `deactivate` and delete everything by `rm -rf .venv`.

## Project Outline

This project implements the following ALE filter with LMS and RMs algorithms:

```
x[n] ──┬──────────────────────────────(-)──► e[n] ≈ s[n]   (the output)
       │                               ▲
       └─► z^(−nD) ─► FIR h[k,n] ──► î[n]
                     (adapted by LMS / RLS using e[n])
```

The FIR filter's goal is to detect the interference via the k memory taps it uses. </br>
For the LMS section, a white noise signal `s[n]` is mixed with a deterministic constant-phase sinusioid `i[n]` to create the input `x[n]`.
After the signal is delayed, the filter deduces the correlated part of the signal as the interference and outputs `î[n]`.
The deduced frequency content is suppressed by subtracting `î[n]`, which remains mostly `s[n]`.

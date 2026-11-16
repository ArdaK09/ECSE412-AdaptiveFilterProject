# ECSE412-AdaptiveFilterProject
---
## Opening/Running the notebook with Conda

`conda env create -f environment.yml --prune`

This should download all the requirements to your conda environement and the notebook should run now.

## TODO
  
Ryan:
- Read Claude Doc on gmail

Arda:
- Read resources (LMS paper, lecture slides)
- Create report draft
- Read Random signals (2.10)

## Pseudocode Implementation
- Create signal: `s[n]`, `i[n]`, `x[n]`.
- Init weights **h[k,n]**. Figure out what value of M (number of weights) we want to use
  - May use a bias variable as h[0,n] which would be initialized as a 1.
  - In Lec slides, says to init all values as 0, but we can play around with random initialization to seek better convergence
  - The algorithm only uses the current weights, so keep one vector of length M+1 and update it in place. 
- Init i_hat. Start with 0 because we have no prior knowledge of error.
- Init mu. Start with 0.0001
  - No negative values: μ must be greater than 0. 
  - A negative μ climbs the error surface instead of descending it, it divergs. 
  - Upper limit: the practical bound is μ < 2 / ((M+1)·σ_x²). With σ_s² = 1 and A = 1, σ_x² = 1.5. 
- Init n_D. We must figure out a good time step for this. Since `s[n]` is random noise, a delay of 1 time step is usually sufficient, but if it is any different form of noise, it will need a larger time step.
- Create loop
  - produce `e[n] = x[n] - i_hat[n]` 
  - calculate `h[k,n+1] = h[k,n] + mu * e[n] * x[n - n_D - k]`
  - calculate `i_hat[n+1] = h[k,n] convolved with x[n]`
  - plot mean-square error (formula from class slides)

## LMS Experiment Layout

Change μ: 0.0001, 0.001, 0.01, 0.1 </br>
Change nD: (1), 2, 4, 8, 16 </br>
M (Num of Weights): 4, 8, 16, 32 </br>
Numer of runs for Monte Carlo: 10-100
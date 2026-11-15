# ECSE412-AdaptiveFilterProject
---

## TODO
  
Ryan:
- Read Claude Doc on gmail

Arda:
- Read resources (LMS paper, lecture slides)
- Create python files, `venv` and `requirements.txt`
- Create report draft
- Read Random signals (2.10)

## Pseudocode Implementation
- Create signal: `s[n]`, `i[n]`, `x[n]`.
- Init weights **h[k,n]**. Figure out what value of M (number of weights) we want to use
  - May use a bias variable as h[0,n] which would be initialized as a 1.
  - In Lec slides, says to init all values as 0, but we can play around with random initialization to seek better convergence
- Init i_hat. Start with 0 because we have no prior knowledge of error.
- Init mu. Start with 1, but we will sweep some range (perhaps [-10, 10])
- Init n_D. We must figure out a good time step for this. Since `s[n]` is random noise, a delay of 1 time step is usually sufficient, but if it is any different form of noise, it will need a larger time step.
- Create loop
  - produce `e[n] = x[n] - i_hat[n]` 
  - calculate `h[k,n+1] = h[k,n] + mu * e[n] * x[n - n_D - k]`
  - calculate `i_hat[n+1] = h[k,n] convolved with x[n]`
  - plot mean-square error (formula from class slides)

# What is this website?
With the current and unfortunately unfolding world events I decided to simulate simple dynamics to model the spread of the Coronavirus disease. 

This is essentially a live API where you can play around with the input parameters to simulate the spread of an epidemic. When any of the parameters are adjusted - a new SIR model simulation is run and provides immediate visual feedback on an SIR graph. 

The SIR graph provides information about the number of susceptible, infected, and recovered people but most importantly how long the virus will take to slow down, as well as the peak number of infected people.

See https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SIR_model_with_vital_dynamics_and_constant_population for more information.

## Assumptions
There are many implicit assumptions within this model, most important of which are:
1) Recovered individuals gain permanent immunity from the virus (would have required an SIRS model instead but evidence suggests very slim chance of reinfection)
2) Government and Quarantine measures likely understated - they are highly simplified here in the sense that user may choose an approximate value for the initial population at risk.
3) Assumes infected people are not quarantined, but rather, immersed within and able to infect, on average, the specified number by the user.

## Interesting dynamics to play around with and observe:
1) Visualize the concept of "flattening the curve" vs "herd immunity" by adjusting the how many people an infected person will infect on average (during their sickness period) before they recover. We observe that the demise of the virus is accelerated if we increase the likelyhood of people getting infected.
2) How, with epidemics, we observe exponential behaviour (more accurately following a logistic curve) of the rate at which people are getting infected.

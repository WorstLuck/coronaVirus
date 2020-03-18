# What is this website?
SIR model for the evolution of Corona Virus

With the current unfolding world events I decided to use some numerical techniques I learned to simulate simple dynamics to model the spread of the Coronavirus disease.

There are many implicit assumptions within this model, most important of which are:
1) Recovered individuals gain permanent immunity from the virus (would have required an SIRS model instead but evidence suggests very slim chance of reinfection)
2) Government and Quarantine measures likely understated - they are highly simplified in the sense that user may choose an approximate value for the initial population at risk.
3) Assumes infected people are not quarantined, but rather, immersed within and able to infect, on average, the specified number by the user.

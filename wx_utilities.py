import numpy as np
import math


#### Knots to MPH ####
def knot2mph(knots):
    return knots * 1.15078

def mph2knot(mph):
    return mph / 1.15078

def ms2knot(ms):
    return ms / 0.5144447

def knot2ms(knot):
    return knot * 0.5144447

def mph2ms(mph):
    return mph * 0.44704

def ms2mph(ms):
    return ms / 0.44704

def C2F(C):
    return (C * (9.0/5.0)) + 32.0

def F2C(F):
    return (F - 32.0) * (5.0/9.0)

def C2K(C):
    return C + 273.15

def K2C(K):
    return K - 273.15

def F2K(F):
    C = F2C(F)
    return C2K(C)

def K2F(K):
    C = K2C(K)
    return C2F(C)

def ClausClap(T):
    # use the empirical version of the Clausius-Clapeyron equation
    # as described in A First Course in Atmospheric Thermodynamics (Petty)
    # Input: T (float or int) Temperature in C (NOT KELVIN)
    return 611.2 * math.exp( (17.67*T) / (T+243.5) )

def RH(T,Td):
    es = ClausClap(T)
    ev = ClausClap(Td)
    return (ev/es) * 100.0



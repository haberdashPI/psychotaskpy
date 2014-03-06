import numpy as np
from random import randint
from math import *

class ConstantAdapter:
    def __init__(self,delta_seq):
        self.deltas = delta_seq + [0]
        self.index = 0
        self.update()
    def update(self,given=None,correct=None):
        self.delta = self.delta_seq[self.index]
        self.index = self.index + 1


################################################################################
# Maximum Likelihood adapter, as described in Green (1993).
# with the following modifications
#
# 1. Put delta on log scale (since we're working with
#    differences in ms, not dB).
# 2. Add a prior over slopes, s.t. very steep slopes become
#    increasingly unlikely. In piloting not having this
#    lead to instability.

max_exp = 700
log_zero = -100

def sig_likelihood(delta,slope,alpha,midpoint):
    if delta == 0: return alpha
    
    x = slope*(log(delta/midpoint))    
    if abs(x) < max_exp:
        return alpha + (1-alpha)*(1.0/(1+exp(-x)))
    elif x > 0:
        return 1
    else:
        return alpha
        
def sig_inv_likelihood(p,slope,alpha,midpoint):
    assert(p > alpha)
    return exp(log(midpoint) - log((1-p) / (p - alpha))/slope)
def sig_solve_slope(p,delta,alpha,midpoint):
    return log((1-p)/(p-alpha)) / -(log(delta/midpoint))

class SigLikelihoodFunction:
    def __init__(self,slope,alpha,midpoint,prior):
        self.slope = slope
        self.alpha = alpha
        self.midpoint = midpoint
        self.value = prior
    def __logz(self,delta):
        if delta == 0: return log_zero
        else: return log(delta)        
    def update(self,delta,given):
        prob_yes = sig_likelihood(delta,self.slope,self.alpha,self.midpoint)
        if given == 1:
            self.value = self.value + self.__logz(prob_yes)
        else:
            self.value = self.value + self.__logz(1-prob_yes)
    def delta(self,level=0.6):
        return sig_inv_likelihood(level,self.slope,self.alpha,self.midpoint)

class MLAdapter:
    def __init__(self,start_delta,slopes,midpoints,alphas,slope_sigma):
        self.LLs = []
        self.delta = start_delta
        for slope in slopes:
            for alpha in alphas:
                for midpoint in midpoints:
                    prior = -log((slope_sigma * sqrt(2*pi)))  \
                        -(slope**2 / (2*slope_sigma**2))
                    #prior = 0.0
                    self.LLs.append(SigLikelihoodFunction(slope,alpha,
                                                          midpoint,prior))

    def update(self,given,correct):
        maxLL = self.LLs[0]

        if correct == 1:
            delta = self.delta
        else:
            delta = 0

        for LL in self.LLs:
            LL.update(delta,given)
            if maxLL.value < LL.value: maxLL = LL

        self.delta = maxLL.delta()

    def estimate(self,level=0.79):
        maxLL = max(self.LLs,key=lambda x: x.value)
        return maxLL.delta(level)

    def best(self): return max(self.LLs,key=lambda x: x.value)
    
        
    

        
                                            
            
        

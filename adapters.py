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
# Stepping adapter: classic adaptive threshold estimation ala Levitt 1971

class Stepper:
    def __init__(self,start,bigstep,littlestep,down,up,big_reverse=3,
                 drop_reversals=3,min_reversals=7,mult=False):
        
        self.down = down
        self.up = up
        self.bigstep = bigstep
        self.step = littlestep
        self.big_reverse = big_reverse
        self.drop_reversals = drop_reversals
        self.min_reversals = min_reversals
        self.mult = mult

        self.num_correct = 0
        self.num_incorrect = 0
        self.reversals = []
        self.last_direction = 0

        self.delta = start

    def update_reversals(self,direction):
        if self.last_direction and direction != self.last_direction:
            self.reversals.append(self.delta)

        self.last_direction = direction
                 
    def update(self,user_response,correct_response):
        if user_response == correct_response:
            self.num_correct = self.num_correct + 1
            self.num_incorrect = 0

            if self.num_correct >= self.down:
                self.num_correct = 0
                self.update_reversals(-1)

                if len(self.reversals) < self.big_reverse:
                    if self.mult:
                        new_delta = self.delta / self.bigstep
                    else:
                        new_delta = self.delta - self.bigstep
                else:
                    if self.mult:
                        new_delta = self.delta / self.step
                    else:
                        new_delta = self.delta - self.step

            else:
                new_delta = self.delta

            self.delta = new_delta

        else:
            self.num_incorrect = self.num_incorrect + 1
            self.num_correct = 0

            if self.num_incorrect >= self.up:
                self.num_incorrect = 0
                self.update_reversals(1)

                if len(self.reversals) < self.big_reverse:
                    if self.mult:
                        new_delta = self.delta * self.bigstep
                    else:
                        new_delta = self.delta + self.bigstep
                else:
                    if self.mult:
                        new_delta = self.delta * self.step
                    else:
                        new_delta = self.delta + self.step
            else:
                new_delta = self.delta

            self.delta = new_delta

    def estimates(self):
        if len(self.reversals) < self.min_reversals:
            return []
        else:
            if len(self.reversals) % 2 == 0:
                return self.reversals[(self.drop_reversals+1):]
            else:
                return self.reversals[self.drop_reversals:]
    def estimate(self):
        if self.mult:
            return np.exp(np.mean(np.log(self.estimates())))
        else:
            return np.mean(self.estimates())

    def estimate_sd(self):
        if self.mult:
            return np.exp(np.std(np.log(self.estimates())))
        else:
            return np.std(self.estimates())

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
    
        
    

        
                                            
            
        

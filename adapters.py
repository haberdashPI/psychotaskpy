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


# Maximum Likelihood adapter, as described in Green (1993).

def sig_likelihood(x,slope,alpha):
    return alpha + (1-alpha)*(1.0/(1+exp(-slope*x)))
def sig_inv_likelihood(p,slope,alpha):
    assert(p > alpha)
    return -log((p-1) / (alpha - p))/slope
def sig_solve_slope(p,x,alpha):
    return log((1-p)/(p-alpha)) / -x

class MLAdapter:
    def __init__(self,start_delta,possible_slopes,possible_alphas,slope_sigma):
        self.log_zero = -100
        self.LLs = []
        self.delta = start_delta
        for slope in possible_slopes:
            for alpha in possible_alphas:
                prior = -log((slope_sigma * sqrt(2*pi)))  \
                  -(slope**2 / (2*slope_sigma**2))
                #prior = 0.0
                self.LLs.append({'slope':slope, 'alpha': alpha, 'value': prior})

    def __logz(self,x):
        if x == 0: return self.log_zero
        else: return log(x)

    def update(self,given,correct):
        maxLL = self.LLs[0]

        if correct == 1:
            delta = self.delta
        else:
            delta = 0

        for LL in self.LLs:
            if given == 1: LL['value'] = LL['value'] + \
                self.__logz(sig_likelihood(delta,LL['slope'],LL['alpha']))
            else: LL['value'] = LL['value'] + \
                self.__logz(1-sig_likelihood(delta,LL['slope'],LL['alpha']))

            if maxLL['value'] < LL['value']: maxLL = LL

        self.delta = sig_inv_likelihood(0.6,maxLL['slope'],maxLL['alpha'])

    def estimate(self,level=0.79):
        maxLL = max(self.LLs,key=lambda x: x['value'])
        return sig_inv_likelihood(level,maxLL['slope'],maxLL['alpha'])
        
    

        
                                            
            
        

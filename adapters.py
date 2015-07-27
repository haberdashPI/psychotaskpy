import scipy
import scipy.stats
import numpy as np
from random import randint
from math import *


class BaseAdapter(object):
    def baseline_delta(self):
        return 0

    def next_trial(self,n):
        if n == 2:
            if randint(0,1) == 0:
                return [self.delta,self.baseline_delta()],0
            else:
                return [self.baseline_delta(),self.delta],1
        if n == 1:
            if randint(0,1) == 0:
                return [self.baseline_delta()],0
            else:
                return [self.delta],1

    def get_delta(self):
        return self.delta

    def single_question_adapters(self):
        return [self]

    def next_multi_trial(self,n):
        xs = self.next_trial(n)
        return xs[0],[xs[1]]

class ConstantStimuliAdapter(BaseAdapter):
    def __init__(self,delta_seq):
        self.deltas = delta_seq
        self.index = 0
        self.update()

    def update(self,given=None,correct=None):
        if self.index < len(self.deltas):
            self.delta = self.deltas[self.index]
        elif self.index > len(self.deltas):
            raise RuntimeError('Unexpected trial index: '+self.index)
        self.index = self.index + 1


class MultiAdapter(BaseAdapter):
    def __init__(self,*adapters):
        self.adapters = adapters

    def single_question_adapters(self):
        return self.adapters

    def next_trial(self,n):
        raise RuntimeError('Cannot get a single response for a MultiAdapter')

    def next_multi_trial(self,n):
        xs = zip(*[a.next_trial(n) for a in self.adapters])
        return zip(*xs[0]), xs[1]

################################################################################
# Stepping adapter: classic adaptive threshold estimation ala Levitt 1971


class Stepper(BaseAdapter):
    def __init__(self,start,bigstep,littlestep,down,up,big_reverse=3,
                 drop_reversals=3,min_reversals=7,mult=False,
                 min_delta=float('-inf'),max_delta=float('inf')):

        self.min_delta = min_delta
        self.max_delta = max_delta
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

            self.delta = min(max(new_delta,self.min_delta),self.max_delta)

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

            self.delta = min(max(new_delta,self.min_delta),self.max_delta)

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
# Bayesian estimation of slopes, as per Kontsevich & Tyler 1999


def _log_sum(xs):
    min_x = np.min(xs)
    return np.log(np.sum(np.exp(xs - min_x))) + min_x


def _prob_response(correct,x,table):

    L = 1
    try: L = len(x)
    except: pass

    theta = np.tile(table.theta,(L,1)).T
    sigma = np.tile(table.sigma,(L,1)).T
    miss = np.tile(table.miss,(L,1)).T

    N = scipy.stats.norm.cdf(x,loc=theta,scale=sigma)
    N[np.isnan(N)] = 0.0

    p_correct = miss/2 + (1.0-miss)*N
    if correct: return p_correct
    else: return 1-p_correct


def _threshold(table,thresh=0.79):
    theta = table.theta
    sigma = table.sigma
    miss = table.miss

    return scipy.stats.norm.ppf((thresh-miss/2)/(1.0-miss/2),
                                loc=theta,scale=sigma)



class KTAdapter(BaseAdapter):
    def __init__(self,start_delta,possible_deltas,log_prior_table):
        self.mult = False
        self.possible_deltas = possible_deltas
        self.table = log_prior_table
        self.delta = start_delta
        if not (self.table.columns == 'lp').any():
            self.table['lp'] = 0

    def update(self,user_response,correct_response):
        correct = user_response == correct_response

        # update posterior
        p = _prob_response(correct,[self.delta],self.table)
        self.table.lp += np.squeeze(np.log(p))
        self.table.lp -= _log_sum(self.table.lp)

        # select minimum entropy delta
        p_corrects = _prob_response(True,self.possible_deltas,self.table)
        p_incorrects = 1-p_corrects

        p_corrects *= np.exp(self.table.lp)[:,np.newaxis]
        p_c_norm = np.sum(p_corrects,axis=0)

        p_incorrects *= np.exp(self.table.lp)[:,np.newaxis]
        p_i_norm = np.sum(p_incorrects,axis=0)

        entropy = -np.sum(p_corrects * \
                          (np.log(p_corrects) - np.log(p_c_norm)),axis=0) + \
                  -np.sum(p_incorrects * \
                          (np.log(p_incorrects) - np.log(p_i_norm)),axis=0)

        self.delta = self.possible_deltas[np.argmin(entropy)]

    def estimate(self):
        ts = _threshold(self.table)
        return np.average(ts[~np.isnan(ts)],
                          weights=np.exp(self.table.lp[~np.isnan(ts)]))

    def estimate_sd(self):
        ts = _threshold(self.table)
        ws = np.exp(self.table.lp)
        thresh = np.average(ts, weights=ws)

        return np.sqrt(np.average((ts-thresh)**2, weights=ws))

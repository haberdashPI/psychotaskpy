from itertools import repeat
import scipy
import scipy.stats
import numpy as np
import pandas as pd
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

    def multi_track_index(self):
        return None

    def report_threshold(self):
        return ('Threshold: %2.3f, SD: %2.1f\n' %
                (self.estimate(),self.estimate_sd()))

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


class InterleavedAdapter(BaseAdapter):
    def __init__(self,n_trials,*adapters):
        self.adapters = adapters
        selections = np.repeat(np.arange(len(adapters)),n_trials/2)
        self.selections = list(np.random.choice(selections,replace=False,
                                                size=n_trials))

    def next_trial(self,n):
        self.current_adapter = self.selections.pop()
        stims,response = self.adapters[self.current_adapter].next_trial(n)
        return zip(repeat(self.current_adapter),stims), response

    def update(self,user_response,correct_response):
        self.adapters[self.current_adapter].update(user_response,
                                                   correct_response)

    def get_delta(self):
        return self.adapters[self.current_adapter].get_delta()

    def multi_track_index(self):
        return self.current_adapter

    def report_threshold(self):
        return '\n'.join([('Track %d: ' % i) + a.report_threshold()
                          for i,a in enumerate(self.adapters)])

    def estimate(self):
        return self.adapters[self.current_adapter].estimate()
    def estimate_sd(self):
        return self.adapters[self.current_adapter].estimate_sd()

################################################################################
# classic method of constant stimuli


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



class RefinedStepper(Stepper):
    def __init__(self,standard,start,bigstep,littlestep,down,up,big_reverse=3,
                 drop_reversals=3,min_reversals=7,mult=False,
                 min_delta=float('-inf'),max_delta=float('inf')):

        super(RefinedStepper,self).__init__(start,bigstep,littlestep,down,up,
                                            big_reverse,drop_reversals,
                                            min_reversals,mult,min_delta,
                                            max_delta)
        self.deltas = []
        self.responses = []
        self.standard = standard

    def update(self,user_response,correct_response):
        self.deltas.append(self.delta)
        self.responses.append(user_response == correct_response)
        return super(RefinedStepper,self).update(user_response,correct_response)

    def report_threshold(self):
        refined = refined_estimate(np.log(self.estimate() / self.standard),
                                   np.array(self.responses),
                                   np.log(np.array(self.deltas) /
                                          self.standard))

        thresh = np.exp(refined[0])*self.standard
        sd = refined[1]

        return ('Threshold: %2.3f, SD: %2.1f\n' % (thresh,sd))

# a test case for the functions below
# responses = [True,  True,  True,  True,  True,  True,  True,  True,  True,
#         True,  True,  True, False,  True,  True,  True,  True, False,
#         True,  True,  True,  True, False,  True,  True,  True, False,
#         True,  True,  True,  True,  True,  True,  True,  True,  True,
#         True, False,  True,  True,  True,  True,  True,  True,  True]
# log_deltas = [-2.30258509, -2.30258509, -2.30258509, -2.99573227, -2.99573227,
#        -2.99573227, -3.68887945, -3.68887945, -3.68887945, -4.38202663,
#        -4.38202663, -4.38202663, -5.07517382, -4.38202663, -4.38202663,
#        -4.38202663, -5.07517382, -5.07517382, -4.72860022, -4.72860022,
#        -4.72860022, -5.07517382, -5.07517382, -4.72860022, -4.72860022,
#        -4.72860022, -5.07517382, -4.72860022, -4.72860022, -4.72860022,
#        -5.07517382, -5.07517382, -5.07517382, -5.42174741, -5.42174741,
#        -5.42174741, -5.768321  , -5.768321  , -5.42174741, -5.42174741,
#        -5.42174741, -5.768321  , -5.768321  , -5.768321  , -6.11489459]        
# estimate = -5.1329360802804889

def _phi_approx(x):
    return 1. / (1. + np.exp(-(0.07056*(x**3) + 1.5976*x)))
sqrt_2 = np.sqrt(2)


def _curve_log_prob(y,totals,miss,log_delta,theta,sigma):
    diffs = log_delta[np.newaxis,:] - theta[:,np.newaxis]
    p = (miss/2) + (1-miss)*_phi_approx(np.exp((diffs)*sigma) / sqrt_2)
    return np.sum(scipy.stats.binom.logpmf(y,totals,p,),axis=1)

def _logwmean(value,log_prob):
    return np.exp(scipy.misc.logsumexp(np.log(value) + log_prob) -
                  scipy.misc.logsumexp(log_prob))

# importance sampling estimate of the threshold
def refined_estimate(estimate,responses,log_deltas,
                     delta_range=np.log([0.0001,0.9]),sigma=1,miss=0.01,
                     threshold=0.79,resolution=500,sample_sd=4):
    if np.isnan(estimate):
        estimate = np.mean(log_deltas[len(log_deltas)/2:])

    raw = pd.DataFrame({'correct': responses, 'log_delta': log_deltas})
    summary = raw.groupby('log_delta').correct.sum().reset_index()
    summary['N'] = raw.groupby('log_delta').correct.count().reset_index().correct

    theta = np.random.normal(estimate,sample_sd,size=resolution)
    q_lprob = scipy.stats.norm.logcdf(theta,loc=estimate,scale=sample_sd)
    log_prob = _curve_log_prob(summary.correct.astype('int64'),
                               summary.N,miss,summary.log_delta,theta,sigma)
    weights = log_prob - q_lprob
    weights = np.exp(weights - np.max(weights))

    dprime = scipy.stats.norm.ppf((threshold-miss/2)/(1-miss))
    thresh_off = -np.log(dprime)/sigma
    thresh = np.average(theta + thresh_off,weights=weights)
    thresh_sd = np.average(((theta + thresh_off) - thresh)**2,weights=weights)

    return thresh,thresh_sd

################################################################################
# Bayesian estimation of slopes, as per Kontsevich & Tyler 1999
# This is a slightly modified equation, that handles negative deltas

class KTAdapterAbstract(BaseAdapter):
    def __init__(self,start_delta,possible_deltas,log_prior_table,repeats=0):
        self.mult = False
        self.possible_deltas = possible_deltas
        self.table = log_prior_table
        self.delta = start_delta
        self.last_repeat = 0
        self.repeats = repeats
        if not (self.table.columns == 'lp').any():
            self.table['lp'] = 0

    def update(self,user_response,correct_response):
        correct = user_response == correct_response

        # update posterior
        p = self._prob_response(correct,[self.delta],self.table)
        self.table.lp += np.squeeze(np.log(p))
        self.table.lp -= scipy.misc.logsumexp(self.table.lp)

        # select minimum entropy delta
        p_corrects = self._prob_response(True,self.possible_deltas,self.table)
        p_incorrects = 1-p_corrects

        p_corrects *= np.exp(self.table.lp)[:,np.newaxis]
        p_c_norm = np.sum(p_corrects,axis=0)

        p_incorrects *= np.exp(self.table.lp)[:,np.newaxis]
        p_i_norm = np.sum(p_incorrects,axis=0)

        entropy = -np.sum(p_corrects *
                          (np.log(p_corrects) - np.log(p_c_norm)),axis=0) + \
                  -np.sum(p_incorrects *
                          (np.log(p_incorrects) - np.log(p_i_norm)),axis=0)

        if self.last_repeat == self.repeats:
            self.last_repeat = 0
            self.delta = self.possible_deltas[np.argmin(entropy)]
        else:
            self.last_repeat += 1

    def estimate(self):
        ts = self._threshold(self.table)
        return np.average(ts[~np.isnan(ts)],
                          weights=np.exp(self.table.lp[~np.isnan(ts)]))

    def estimate_sd(self):
        ts = self._threshold(self.table)
        ws = np.exp(self.table.lp)
        thresh = np.average(ts, weights=ws)

        return np.sqrt(np.average((ts-thresh)**2, weights=ws))


def ktadapter(start,deltas,thetas,sigmas,prior,miss=0.08,repeats=0):
    params = pd.DataFrame({'theta': thetas, 'sigma': sigmas,'miss': miss})
    params['lp'] = prior(params)
    return KTAdapter(start,deltas,params.copy(),repeats=repeats)


class KTAdapter(KTAdapterAbstract):
    def __init__(self,*params):
        KTAdapterAbstract.__init__(self,*params)
    def _prob_response(self,correct,x,table):
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


    def _threshold(self,table,thresh=0.79):
        theta = table.theta
        sigma = table.sigma
        miss = table.miss

        return scipy.stats.norm.ppf((thresh-miss/2)/(1.0-miss/2),
                                    loc=theta,scale=sigma)
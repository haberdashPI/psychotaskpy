from util import *
from settings import *
import adapters
import experiment
import calibrate

import pandas as pd
import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import resample, get_window

import statsmodels.api as sm
import statsmodels.formula.api as smf

# setup the types of phases we want to use
import AFC
import passive

atten = calibrate.atten_86dB_for_left[booth()] + 32 # 54 dB
print "Using attenuation of ",atten


groups = ["NP_S30S_120","NP_S240","NP_S300","NP_S30S_150"]

question_str = Vars('Was that Mba[{responses[0]}], ba[{responses[1]}] or ' +
                    'pa[{responses[2]}]?')

conditions = {'Train': {'feedback': True, 'word_distribution': 'trimodal',
                        'question': {'str': question_str, 'alternatives': 3,
                                     'feedback': True}},
              'Test': {'feedback': False, 'word_distribution': 'uniform',
                       'question': {'str': question_str, 'alternatives': 3,
                                    'feedback': False}}}

examples = [[{'str': 'Mba', 'delta': 3}],[{'str': 'ba', 'delta': 8}],
            [{'str': 'pa', 'delta': 13}]]
examples = np.repeat(examples,5)
np.random.shuffle(examples)

env = {'title': 'Non-native Phoneme Contrast',
       'sample_rate_Hz': 44100,
       'debug': True,
       'repeat_examples': False,
       'examples': list(examples),
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': UserSelect('Trials',[60,120],priority=5),
       'feedback_delay_ms': 400,
       'beep_ms': 15,
       'ramp_ms': 5,
       'SOA_ms': 5.1*1000,
       'phase': 'AFC',
       'response_delay_ms': 500,
       'presentations': 1,
       'instructions': 'Label each sound as either Mba, ba or pa.',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'condition': UserSelect('Condition',['Train','Test'],
                               conditions,priority=3),
       'num_blocks': UserNumber('Blocks',1,priority=4)}


sounds = []
for i in xrange(1,16):
  file = 'sounds/'+str(i)+'RMSnorm.wav'
  fs,sound = wav.read(file)
  sound = attenuate(sound/(2.0**16),atten)
  assert fs == 44100

  sounds.append(sound)

def generate_sound(env,delta):
  return sounds[delta]
env['generate_sound'] = generate_sound


class SpeechAdapter(adapters.ConstantStimuliAdapter):
  def __init__(self,deltas):
    super(SpeechAdapter,self).__init__(deltas)
    self.responses = []

  def next_trial(self,n):
    assert n == 1
    if self.delta < 5:
      return [self.delta],0
    elif self.delta < 10:
      return [self.delta],1
    elif self.delta >= 10:
      return [self.delta],2

  def update(self,given=None,correct=None):
    super(SpeechAdapter,self).update(given,correct)
    if correct is not None:
      self.responses.append(given)

  def estimate(self):
    if self.index < len(self.deltas)-1:
      return float('NaN')
    else:
      binom = sm.families.Binomial(sm.families.links.probit)
      df = pd.DataFrame({'resp': np.array(self.responses) == 0,
                         'vot': np.array(self.deltas[:len(self.responses)])})
      fit = smf.glm('resp ~ vot',df,family=binom).fit()
      return 0.5-np.arctan(fit.params['vot'])/np.pi

  def estimate_sd(self):
    return 0

def trimodal(N):
  cat = np.random.choice(range(3),size=N)
  token = np.digitize(np.random.normal(size=N),[-1.5,-0.5,0.5,1.5])
  return cat*5 + token


def generate_adapter(env):
  if env['word_distribution'] == "trimodal":
    return SpeechAdapter(trimodal(env['num_trials']))
  elif env['word_distribution'] == "uniform":
    deltas = np.repeat(np.arange(15),env['num_trials']/15)
    return SpeechAdapter(np.random.choice(deltas,env['num_trials'],
                                          replace=False))
  else:
    raise RuntimeError("No word distributed named "+env['word_distribution'])

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__": experiment.start(env)

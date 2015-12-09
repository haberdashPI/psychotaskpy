import pandas as pd
from util import *
from settings import *
import adapters
import experiment
import calibrate

import AFC

atten = calibrate.atten_86dB_for_left[booth()]
print "Using attenuation of ",atten

conditions = {'noise_tone':
              {'has_tone': True,
               'tone_onset_from_noise_onset': 50,
               'instructions': 'You will be asked if the second sound is ' +
                    'longer or shorter than the first. The first sound will ' +
                    'always be the same length. Please ignore the beep ' +
                    'as best you can.',
               'examples':
               [{'str': 'Shorter Sound', 'delta': -100},
                {'str': 'Longer Sound', 'delta': 100}]},

              'noise_tone_after':
              {'has_tone': True,
               'tone_onset_from_noise_offset': 200,
               'instructions': 'You will be asked if the second sound is ' +
                   'longer or shorter than the first. The first sound will ' +
                   'always be the same length. Please ignore the beep ' +
                   'as best you can.',
               'examples':
               [{'str': 'Shorter Sound', 'delta': -100},
                {'str': 'Longer Sound', 'delta': 100}]},

              'noise_only':
              {'has_tone': False,
               'instructions': 'You will be asked if the second sound is ' +
               'longer or shorter than the first. The first sound will ' +
               'always be the same length.',
               'examples':
               [{'str': 'Shorter Sound', 'delta': -100},
                {'str': 'Longer Sound', 'delta': 100}]}}

env = {'title': 'Noise duration Discrimination',
       'sample_rate_Hz': 44100,
       'debug': False,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 63,
       'feedback_delay_ms': 400,
       'tone_ms': 20,
       'report_threshold': False,
       'noise_onset_ms': 100,
       'tone_Hz': 1000,
       'noise_ms': 450,
       'noise_low_Hz': 600,
       'noise_high_Hz': 1400,
       'ramp_ms': 10,
       'SOA_ms': 1100,
       'SNR_dB': 40,
       'response_delay_ms': 500,
       'presentations': 2,
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': 'noise_length',
       'phase': 'AFC',
       'cache_stimuli': False,
       'deltas': np.linspace(-100,100,9),
       'condition': UserSelect('Condition',['noise_tone','noise_only',
                                            'noise_tone_after'],
                               conditions,priority=1),
       'num_blocks': UserNumber('Blocks',1,priority=2),
       'question':
       {'str': Vars('Was the second noise shorter [{responses[0]}] or ' +
                    'longer [{responses[1]}]?'),
        'alternatives': 2, 'feedback': False}}


def generate_sound(env,stimulus):
  if stimulus is None:
    delta = 0
  else:
    delta = stimulus

  noise = notch_noise(env['noise_low_Hz'],env['noise_high_Hz'],
                      env['noise_ms'] + delta,
                      env['ramp_ms'],env['atten_dB'] +
                      env['SNR_dB'],env['sample_rate_Hz'])

  noise_space = silence(env['noise_onset_ms'],env['sample_rate_Hz'])

  if env['has_tone'] and stimulus is not None:
    if 'tone_onset_from_noise_onset' in env:
      tone_onset_ms = env['tone_onset_from_noise_onset'] + env['noise_onset_ms']
    else:
      tone_onset_ms = (env['tone_onset_from_noise_offset'] +
                       env['noise_onset_ms'] + env['noise_ms'])

    atone = tone(env['tone_Hz'],env['tone_ms'],env['atten_dB'],
                 env['ramp_ms'],env['sample_rate_Hz'])
    space = silence(tone_onset_ms,env['sample_rate_Hz'])

    noise_and_signal = mix(np.vstack([space, atone]),
                           np.vstack([noise_space, noise]))
    return left(noise_and_signal).copy()
  else:
    return left(noise).copy()

env['generate_sound'] = generate_sound


class NoiseLengthAdapter(adapters.ConstantStimuliAdapter):
  def next_trial(self,n):
    assert n == 2
    if self.delta <= 0:
      return [None,self.delta],0
    else:
      return [None,self.delta],1


def generate_adapter(env):
  deltas = np.random.choice(np.repeat(env['deltas'],
                                      env['num_trials']/len(env['deltas'])),
                            env['num_trials'])

  return NoiseLengthAdapter(deltas)

env['generate_adapter'] = generate_adapter

if __name__ == "__main__": experiment.start(env)

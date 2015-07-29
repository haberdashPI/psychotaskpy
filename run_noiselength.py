import pandas as pd
from util import *
from settings import *
import adapters
import experiment

# setup the types of phases we want to use
import AFC

booth_atten = {'corner': 27.6,  # calibrated on 9-15-14
               'left': 9.3,     # calibrated on 05-20-15
               'middle': 30.7,  # calibrated on 10-14-14
               'right': 31.1,   # calibrated on 04-15-15
               'none': 16}

# TODO: check that the right kind of sounds play
# check that alternation works correctly
# verify that there isn't any alternative cue for the length of sounds

atten = booth_atten[booth()]
print "Using attenuation of ",atten

conditions = {'noise_tone':
              {'has_tone': True,
               'instructions': 'You will be listening for the shorter' +
               ' sound. Ignore the tone.',
               'examples':
               [{'str': 'Longer Sound', 'delta': (0,True)},
                {'str': 'Shoter Sound', 'delta': (300,True)},
                {'str': 'Longer Sound', 'delta': (0,False)},
                {'str': 'Shoter Sound', 'delta': (300,False)}]},
              'noise_only':
              {'has_tone': False,
               'instructions': 'You will be listening for the shorter' +
               ' sound.',
               'examples':
               [{'str': 'Shorter Sound', 'delta': 200},
                {'str': 'Longer Sound', 'delta': 0}]}}

env = {'title': 'Noise duration Discrimination',
       'sample_rate_Hz': 44100,
       'debug': True,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 6,
       'feedback_delay_ms': 400,
       'tone_ms': 20,
       'tone_inside_ms': 250,
       'tone_outside_ms': 0,
       'noise_onset_ms': 100,
       'tone_Hz': 1000,
       'noise_ms': 500,
       'noise_low_Hz': 600,
       'noise_high_Hz': 1400,
       'ramp_ms': 10,
       'SOA_ms': 1100,
       'SNR_dB': 25,
       'response_delay_ms': 500,
       'presentations': 2,
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': 'noise_length',
       'phase': 'AFC',
       'cache_stimuli': False,
       'condition': UserSelect('Condition',['noise_tone','noise_only'],
                               conditions,priority=1),
       'num_blocks': UserNumber('Blocks',1,priority=2),
       'question':
       {'str': Vars('Was {labels[0]} [{responses[0]}] or ' +
                    '{labels[1]} [{responses[1]}] shorter?'),
        'alternatives': 2, 'feedback': False}}


def generate_sound(env,stimulus):
  if env['has_tone']:
    delta = stimulus[0]
  else:
    delta = stimulus
  if delta is None:
    delta = 0

  noise = notch_noise(env['noise_low_Hz'],env['noise_high_Hz'],
                      env['noise_ms'] - delta,
                      env['ramp_ms'],env['atten_dB'] +
                      env['SNR_dB'],env['sample_rate_Hz'])

  noise_space = silence(env['noise_onset_ms'],env['sample_rate_Hz'])

  if env['has_tone']:
    tone_in_signal = bool(stimulus[1])
    is_signal = stimulus[0] is not None

    if is_signal == tone_in_signal:
      tone_onset_ms = env['tone_inside_ms']
    else:
      tone_onset_ms = env['tone_outside_ms']

    mytone = tone(env['tone_Hz'],env['tone_ms'],env['atten_dB'],
                  env['ramp_ms'],env['sample_rate_Hz'])
    space = silence(tone_onset_ms,env['sample_rate_Hz'])

    noise_and_signal = mix(np.vstack([space, mytone]),
                           np.vstack([noise_space, noise]))
    return left(noise_and_signal).copy()
  else:
    return left(noise).copy()

env['generate_sound'] = generate_sound


class NoiseLengthAdapter(adapters.KTAdapter):
  def baseline_delta(self):
    return None


def generate_adapter(env):
  deltas = np.linspace(-env['noise_ms'],env['noise_ms'],200)
  thetas = np.tile(deltas,50)
  sigmas = np.repeat(np.logspace(0,np.log(env['noise_ms'])/np.log(10),50),200)
  params = pd.DataFrame({'theta': thetas,'sigma': sigmas,'miss': 0.08})
  params['lp'] = (np.log(scipy.stats.norm.pdf(params.theta,loc=0,
                         scale=env['noise_ms']/2)) +
                  np.log(scipy.stats.norm.pdf(params.sigma, loc=0,
                         scale=env['noise_ms'])))

  if env['has_tone']:
    ad1 = NoiseLengthAdapter(300,deltas,params.copy())
    ad2 = NoiseLengthAdapter(300,deltas,params.copy())
    return adapters.InterleavedAdapter(env['num_trials'],ad1,ad2)
  else:
    return NoiseLengthAdapter(300,deltas,params)

env['generate_adapter'] = generate_adapter

if __name__ == "__main__": experiment.start(env)

import copy
import numpy as np
from util import *
from settings import *
import adapters
import experiment

import AFC

groups = ['children']

booth_atten = {'corner': 27.6,  # calibrated on 9-15-14
               'left': 9.3,     # calibrated on 05-20-15
               'middle': 30.7,  # calibrated on 10-14-14
               'right': 31.1,   # calibrated on 04-15-15
               'none': 16}

atten = booth_atten[booth()]+1  # 85 not 86 dB tone
print "Using attenuation of ",atten

insideQ = {'str': Vars('Was the beep inside [{responses[0]}] or' +
                       ' outside [{responses[1]}] of the noise?'),
           'alternatives': 2,
           'feedback': False}
inside_pitchQa = [insideQ,
                  {'str': Vars('Was the beep low [{responses[0]}] or ' +
                               'high [{responses[1]}]?'),
                   'alternatives': 2,
                   'feedback': False}]
inside_pitchQb = list(reversed(inside_pitchQa))

two_tone_examplesA = [{'str': 'Low tone', 'delta': (None,0)},
                      {'str': 'High tone', 'delta': (None,1)},
                      {'str': 'Low tone, outside of noise',
                       'delta': (0,0)},
                      {'str': 'Low tone, inside of noise',
                       'delta': (250,0)},
                      {'str': 'Low tone, outside of noise (again).',
                       'delta': (450,0)},
                      {'str': 'High tone, outside of noise',
                       'delta': (0,1)},
                      {'str': 'High tone, inside of noise',
                       'delta': (250,1)},
                      {'str': 'High tone, outside of noise (again).',
                       'delta': (450,1)}]

two_tone_examplesB = copy.deepcopy(two_tone_examplesA)
for x in two_tone_examplesB: x['delta'] = (x['delta'][1],x['delta'][0])

two_tone_condition = {'low_tone_frequency_Hz': 900,
                      'high_tone_frequency_Hz': 1100}

conditions = {'tone1': {'tone_frequency_Hz': 1000},
              'noise': {'signal_high_Hz': 5000,'signal_type': 'lowpass'},
              'tone2a':
              prepare({'question_order': 'place_first',
                       'questions': inside_pitchQa,
                       'examples': two_tone_examplesA},
                      two_tone_condition),
              'tone2b':
              prepare({'question_order': 'place_second',
                       'questions': inside_pitchQb,
                       'examples': two_tone_examplesB},
                      two_tone_condition)}

noise_onset_ms = 300
env = {'title': 'Tone Place',
       'debug': True,
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 48,
       'feedback_delay_ms': 400,
       'signal_ms': 20,
       'ramp_ms': 10,
       'SOA_ms': 4000,
       'presentations': 1,
       'response_delay_ms': 500,
       'report_threshold': False,
       'instructions': 'You will be asked to indicate whether the sound was ' +
                       'inside or outside of the noise.',
       'phase': 'AFC',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': 'children',
       'num_blocks': 1,
       'max_signal_onset_ms': 1400,'SNR_dB': 25,
       'noise_onset_ms': noise_onset_ms,'noise_length_ms': 450,
       'noise_low_Hz': 600, 'noise_high_Hz': 1400,
       'tone_positions':
       np.array([-100,-75,-50,0,100,150,200,250,275,300,325,350]) + noise_onset_ms,
       'position_repeats': 4,
       'signal_type': 'tone',
       'question_order': 'place_only',
       'questions': [insideQ],
       'examples':
       [{'str': 'Outside (before) noise', 'delta': -300 + noise_onset_ms},
        {'str': 'Inside of noise', 'delta': 200 + noise_onset_ms},
        {'str': 'Outside (after) noise.','delta': 750 + noise_onset_ms}],
       'condition': UserSelect('Condition',['tone1','tone2a','tone2b','noise'],
                               conditions,priority=1.5)}


def generate_sound(env,delta):
    if env['question_order'] == 'place_first':
      high_tone = bool(delta[1])
      place = delta[0]
    elif env['question_order'] == 'place_second':
      high_tone = bool(delta[0])
      place = delta[1]
    else:
      high_tone = None
      place = delta

    if env['signal_type'] == 'tone':
      if high_tone is None:
        tone_frequency_Hz = env['tone_frequency_Hz']
      elif high_tone:
        tone_frequency_Hz = env['high_tone_frequency_Hz']
      else:
        tone_frequency_Hz = env['low_tone_frequency_Hz']

      signal = tone(tone_frequency_Hz,
                    env['signal_ms'],
                    env['atten_dB'],
                    env['ramp_ms'],
                    env['sample_rate_Hz'])
    elif env['signal_type'] == 'lowpass':
      signal = lowpass_noise(env['signal_high_Hz'],env['signal_ms'],
                             env['ramp_ms'],env['atten_dB'],
                             env['sample_rate_Hz'])

    if place is None:
      return left(signal).copy()
    else:
      space = silence(place,env['sample_rate_Hz'])

      noise = notch_noise(env['noise_low_Hz'],
                          env['noise_high_Hz'],
                          env['noise_length_ms'],
                          env['ramp_ms'],env['atten_dB'] +
                          env['SNR_dB'],
                          env['sample_rate_Hz'])

      noise_space = silence(env['noise_onset_ms'],
                            env['sample_rate_Hz'])

      max_length = (env['max_signal_onset_ms']+env['signal_ms'])/1000.0
      noise_and_signal = mix(np.vstack([space, signal]),
                             np.vstack([noise_space, noise]),
                             int(round(max_length * env['sample_rate_Hz'])))

      return left(noise_and_signal).copy()
env['generate_sound'] = generate_sound


class TonePlaceAdapter(adapters.ConstantStimuliAdapter):
  def __init__(self,env):
    places = np.random.choice(np.repeat(env['tone_positions'],
                                        env['position_repeats']),
                              size=env['num_trials'],
                              replace=False)

    adapters.ConstantStimuliAdapter.__init__(self,places)
    self.noise_range = (env['noise_onset_ms'],
                        env['noise_onset_ms'] +
                        env['noise_length_ms'])

  def next_trial(self,n):
    assert n == 1
    outside = int(self.delta < self.noise_range[0] or
                  self.delta >= self.noise_range[1])
    return [self.delta],outside


class ToneFreqAdapter(adapters.ConstantStimuliAdapter):
  def __init__(self,env):
    tones = np.random.randint(2,size=env['num_trials'])
    adapters.ConstantStimuliAdapter.__init__(self,tones)

  def next_trial(self,n):
    assert n == 1
    return [self.delta],self.delta


def generate_adapter(env):
  if env['question_order'] == 'place_only':
    return TonePlaceAdapter(env)
  elif env['question_order'] == 'place_first':
    return adapters.MultiAdapter(TonePlaceAdapter(env),
                                 ToneFreqAdapter(env))
  elif env['question_order'] == 'place_second':
    return adapters.MultiAdapter(ToneFreqAdapter(env),
                                 TonePlaceAdapter(env))
  else:
    raise RuntimeError("'" + env['question_order'] +
                       "' is not a valid question order.")

env['generate_adapter'] = generate_adapter

if __name__ == "__main__": experiment.start(env)

import copy
import numpy as np
from util import *
from settings import *
import adapters
import experiment
import calibrate

import AFC

groups = ['children']
atten = calibrate.atten_86dB_for_left[booth()]+1  # 85 not 86 dB tone
print "Using attenuation of ",atten

question = {'str': Vars('Was the beep inside [{responses[0]}] or' +
                        ' outside [{responses[1]}] of the noise?'),
            'alternatives': 2,
            'feedback': False}
examples = [{'str': 'Outside (before) noise',
             'delta': Vars("noise_onset_ms-100",eval=True)},
            {'str': 'Inside of noise',
             'delta': Vars("noise_onset_ms+50",eval=True)},
            {'str': 'Outside (after) noise.',
             'delta': Vars("noise_offset_ms+50",eval=True)}]

#two_questionsA = [question,
#                  {'str': Vars('Was the beep low [{responses[0]}] or ' +
#                               'high [{responses[1]}]?'),
#                   'alternatives': 2,
#                   'feedback': False}]
#two_questionsB = list(reversed(two_questionsA))

two_tone_examplesA = [{'str': 'Low tone', 'delta': (None,0)},
                      {'str': 'High tone', 'delta': (None,1)},
                      {'str': 'Low tone, outside of noise',
                       'delta': [Vars('noise_onset_ms-100',eval=True),0]},
                      {'str': 'Low tone, inside of noise',
                       'delta': [Vars('noise_onset_ms+50',eval=True),0]},
                      {'str': 'Low tone, outside of noise (again).',
                       'delta': [Vars('noise_offset_ms+100',eval=True),0]},
                      {'str': 'High tone, outside of noise',
                       'delta': [Vars('noise_onset_ms-100',eval=True),1]},
                      {'str': 'High tone, inside of noise',
                       'delta': [Vars('noise_onset_ms+100',eval=True),1]},
                      {'str': 'High tone, outside of noise (again).',
                       'delta': [Vars('noise_offset_ms+100',eval=True),1]}]

# reorder exampels for the B ordering
two_tone_examplesB = copy.deepcopy(two_tone_examplesA)
for x in two_tone_examplesB: x['delta'] = [x['delta'][1],x['delta'][0]]

condition_order = ['450tone1', '750tone1', '450tone2','450noise']
conditions = {'450tone1': {'tone_frequency_Hz': 1000, 'noise_length_ms': 450,
                           'tone_positions': Vars("""[noise_onset_ms-100,noise_onset_ms-50,
                                                      noise_onset_ms, noise_onset_ms+50,
                                                      noise_onset_ms+100,noise_onset_ms+150,
                                                      noise_onset_ms+200, noise_offset_ms-200,
                                                      noise_offset_ms-150, noise_offset_ms-100,
                                                      noise_offset_ms-50, noise_offset_ms,
                                                      noise_offset_ms+25, noise_offset_ms+50]""",eval=True)},
              '750tone1': {'tone_frequency_Hz': 1000, 'noise_length_ms': 750,
                           'tone_positions': Vars("""[noise_onset_ms-100,noise_onset_ms-50,
                                                      noise_onset_ms, noise_onset_ms+75,
                                                      noise_onset_ms+150,noise_onset_ms+225,
                                                      noise_onset_ms+300, noise_offset_ms-375,
                                                      noise_offset_ms-300, noise_offset_ms-225,
                                                      noise_offset_ms-150, noise_offset_ms-75,
                                                      noise_offset_ms, noise_offset_ms+25,
                                                      noise_offset_ms+50]""",eval=True)},

              '450noise': {'signal_high_Hz': 5000,'signal_type': 'lowpass', 'noise_length_ms': 450},

              '450tone2': {'examples': two_tone_examplesA,
                         'low_tone_frequency_Hz': 900,
                         'high_tone_frequency_Hz': 1100, 
                         'noise_length_ms': 450,
                         'tone_positions': Vars("""[noise_onset_ms-100,noise_onset_ms-50,
                                                    noise_onset_ms, noise_onset_ms+50,
                                                    noise_onset_ms+100,noise_onset_ms+150,
                                                    noise_onset_ms+200, noise_offset_ms-200,
                                                    noise_offset_ms-150, noise_offset_ms-100,
                                                    noise_offset_ms-50, noise_offset_ms,
                                                    noise_offset_ms+25, noise_offset_ms+50]""",eval=True)}}
                         

env = {'title': 'Tone Place',
       'debug': False,
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 48,
       'feedback_delay_ms': 0,  # there is no feedback
       'signal_ms': 20,
       'ramp_ms': 10,
       'SOA_ms': 4000,
       'presentations': 1,
       'response_delay_ms': 500,
       'next_trial_delay_ms': 500,
       'report_threshold': False,
       'instructions': 'You will be asked to indicate whether the sound was ' +
                       'inside or outside of the noise.',
       'phase': 'AFC',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': 'children',
       'num_blocks': 6,
       'max_signal_onset_ms': 1400, 'SNR_dB': 17,
       'noise_low_Hz': 600, 'noise_high_Hz': 1400,
       'noise_onset_ms': 300,
       'noise_offset_ms': Vars('noise_onset_ms+noise_length_ms',eval=True),
       'examples': examples,
       'position_repeats': 4,
       'signal_type': 'tone',
       'question_order': 'place_only',
       'questions': [question],
       'condition': UserSelect('Condition',condition_order,
                               conditions,priority=1.5)}


def generate_sound(env,delta):
    if env['question_order'] == 'place_first':
      high_tone = bool(delta[1])
      place = delta[0]
    elif env['question_order'] == 'place_second':
      high_tone = bool(delta[0])
      place = delta[1]      
    elif 'low_tone_frequency_Hz' in env:
      high_tone = bool(delta[1])
      place = delta[0]
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
    super(ToneFreqAdapter,self).__init__(tones)

  def next_trial(self,n):
    assert n == 1
    return [self.delta],self.delta
    
class TonePlaceFreqAdapter(adapters.ConstantStimuliAdapter):
  def __init__(self,env):
    places = np.random.choice(np.repeat(env['tone_positions'],
                                        env['position_repeats']),
                              size=env['num_trials'],
                              replace=False)
    tones = np.random.randint(2,size=env['num_trials'])

    adapters.ConstantStimuliAdapter.__init__(self,zip(places,tones))
    self.noise_range = (env['noise_onset_ms'],
                        env['noise_onset_ms'] +
                        env['noise_length_ms'])

  def next_trial(self,n):
    assert n == 1
    outside = int(self.delta[0] < self.noise_range[0] or
                  self.delta[0] >= self.noise_range[1])
    return [self.delta],outside

def generate_adapter(env):
  if env['question_order'] == 'place_only':
    if 'low_tone_frequency_Hz' in env:
        return TonePlaceFreqAdapter(env)
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

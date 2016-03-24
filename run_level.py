from util import *
from settings import *

import pandas as pd
import scipy.stats
import adapters
import experiment
import phase
import calibrate

# setup the types of phases we want to use
import AFC

phases = ['AFC']

freqs = ['250','500','1k','2k','4k','8k']

dBSPL_to_dBHL = {'250': 27, '500': 13.5, '1k': 7.5, '2k': 9,
                 '4k': 12, '8k': 15.5}

def calibration_fn(freq,dB_HL):
    return (20 + calibrate.atten_20dB_by_freq[booth()][freq] -
            (dB_HL+dBSPL_to_dBHL[freq]))


conditions = [{'name': '250', 'tone_Hz': 250},
              {'name': '500', 'tone_Hz': 500},
              {'name': '1k', 'tone_Hz': 1000},
              {'name': '2k', 'tone_Hz': 2000},
              {'name': '4k', 'tone_Hz': 4000},
              {'name': '8k', 'tone_Hz': 8000}]
np.random.shuffle(conditions)

env = {'title': 'Tone Detection',
       'sid': UserNumber('Subject ID',0,priority=0),
       'debug': True,
       'start_block': 0,
       'phase': 'AFC',
       'sample_rate_Hz': 44100,
       'group': 'level',
       'num_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 15,
       'feedback_delay_ms': 400,
       'beep_ms': 200,
       'ramp_ms': 5,
       'SOA_ms': 900,
       'response_delay_ms': 500,
       'example_standard': 'No tone played',
       'example_signal': "There's a Tone!",
       'example_delta': 60,
       'instructions': 'You will be listening for a tone.',
       'presentations': 2,
       'question': {'str': Vars('Did Time 1 [{responses[0]}] or Time 2' +
                                ' [{responses[1]}] have a tone?'),
                     'alternatives': 2,
                     'labels': ['Time 1','Time 2']},
       'examples': [{'str': 'Beep', 'delta': 60},
                    {'str': 'Silence', 'delta': None}],
       'conditions': conditions}


def generate_sound(env,delta):
    if delta is not None:
        print "atten: ",calibration_fn(env['condition'], delta)
      
        beep = tone(env['tone_Hz'],
                    env['beep_ms'],
                    calibration_fn(env['condition'],delta),
                    env['ramp_ms'],
                    env['sample_rate_Hz'])

        return left(beep).copy()
    else:
        return silence(env['beep_ms'],env['sample_rate_Hz']).copy()

env['generate_sound'] = generate_sound

class LevelAdapter(adapters.KTAdapter):
  def __init__(self,*params):
      adapters.KTAdapter.__init__(self,*params)
  def baseline_delta(self):
    return None

def generate_adapter(env):
    params = pd.DataFrame({'theta': np.tile(np.linspace(120,-10,130),50),
                           'sigma': np.repeat(np.linspace(0.2,100,50),130),
                           'miss': 0.08})

    params['lp'] = np.log(scipy.stats.norm.pdf(params.theta,loc=0,scale=50)) + \
        np.log(scipy.stats.norm.pdf(params.sigma, loc=0,scale=50))
    
    min_dB = -10 #calibration_fn[condition].x[0]+0.01
    max_dB = 80 #calibration_fn[condition].x[-1]-0.01
    return LevelAdapter(60,np.linspace(min_dB,max_dB,100),params)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__": experiment.start(env)

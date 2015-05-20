from itertools import repeat
from scipy.interpolate import interp1d
import pandas as pd
import scipy.stats
from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import twoAFC
import passive

phases = ['2AFC']

#booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
#               'middle': 30.7, # calibrated on 10-14-14
#			   'right': 31.1, # calibrated on 04-15-15
#               'none': 26}
			   

freqs = ['250','500','1k','2k','4k','8k']

# calibrated on 05-20-15
dBSPL_to_dBHL = {'250': 27, '500': 13.5, '1k': 7.5, '2k': 9, '4k': 12, '8k': 15.5}

# def make_calfn(freq,curve):
    # atten,dBSPL = zip(*curve)
    # return interp1d(np.array(dBSPL) - dBSPL_to_dBHL[freq],atten)

# calibration_fn = dict(map(lambda (freq,curve): (freq,make_calfn(freq,curve)),
                          # calibration_curve[booth()].iteritems()))

atten_20dB = {'left': {'250': 70, '500': 71.3, '1k': 75, '2k': 67.5, '4k': 66, '8k': 65}}                  
def calibration_fn(freq,dB_HL):
    return 20+atten_20dB[booth()][freq] - (dB_HL+dBSPL_to_dBHL[freq])

env = {'title': 'Tone Detection',
       'debug': False,
       'sample_rate_Hz': 44100,
       'groups': ['level'],
       'default_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 15,
       'feedback_delay_ms': 400}

stimulus = {'beep_ms': 200,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'response_delay_ms': 500,
            'example_standard': 'No tone played',
            'example_signal': "There's a Tone!",
            'example_delta': 60,
            'instructions': 'You will be listening for a tone.',
            'sound_labels': ['Time 1','Time 2'],
            'full_question': 'Did time 1 [Q] or time 2 [P] have a tone?',
            'condition_order': ['250','500','1k','2k','4k','8k'],
            'conditions': {'250': 250, '500': 500, '1k': 1000,
                           '2k': 2000, '4k': 4000, '8k': 8000}}
                                                      
def generate_sound(env,stimulus,condition,delta):
    if delta != 0:
        cond = stimulus['conditions'][condition]

        beep = tone(cond,
                    stimulus['beep_ms'],
                    calibration_fn(condition,delta),
                    stimulus['ramp_ms'],
                    env['sample_rate_Hz'])

        return left(beep).copy()
    else:
        return silence(stimulus['beep_ms'],env['sample_rate_Hz']).copy()

stimulus['generate_sound'] = generate_sound

def generate_adapter(env,stimulus,condition):
    params = pd.DataFrame({'theta': np.tile(np.linspace(120,-10,130),50),
                           'sigma': np.repeat(np.linspace(0.2,100,50),130),
                           'miss': 0.08})

    params['lp'] = np.log(scipy.stats.norm.pdf(params.theta,loc=0,scale=50)) + \
        np.log(scipy.stats.norm.pdf(params.sigma, loc=0,scale=50))
    
    min_dB = -10 #calibration_fn[condition].x[0]+0.01
    max_dB = 80 #calibration_fn[condition].x[-1]-0.01
    return adapters.KTAdapter(60,np.linspace(min_dB,max_dB,100),params)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__":
    np.random.shuffle(freqs)
    experiment.start(env,stimulus,phases,conditions=freqs)

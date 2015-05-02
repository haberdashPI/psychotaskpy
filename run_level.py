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
			   
 # calibrated on 05-02-15			   
calibration_curve = {'left': [(20,98.8),(40,78.8),(45,73.8),(50,68.75),(55,63.7),(60,58.6),
							  (65,53.6),(70,48.5),(75,43.4),(80,37.7),(85,30.8),
							  (87.5,26.9),(90,25.3),(91.25,22.6),(92.5,18),(93.75,13.6),(95,13)],
					 'none': zip(np.linrange(20,80,10),np.linrange(100,10,10))}

atten = booth_atten[booth()]
print "Using attenuation of ",atten

env = {'title': 'Tone Detection',
       'debug': True,
       'sample_rate_Hz': 44100,
       'groups': ['level'],
       'default_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 15,
       'feedback_delay_ms': 400}

stimulus = {'atten_dB': atten,
            'beep_ms': 200,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'response_delay_ms': 500,
            'example_standard': 'No tone played',
            'example_signal': "There's a Tone!",
            'example_delta': -10,
            'instructions': 'You will be listening for a tone.',
            'sound_labels': ['Time 1','Time 2'],
            'full_question': 'Which time period had a tone?',
            'condition_order': ['250','500','1k','2k','4k','8k'],
            'conditions': {'250': 250, '500': 500, '1k': 1000,
                           '2k': 2000, '4k': 4000, '8k': 8000}}
                                                      

def generate_sound(env,stimulus,condition,delta):
    if delta != 0:
        cond = stimulus['conditions'][condition]

        beep = tone(cond,
                    stimulus['beep_ms'],
                    stimulus['atten_dB'] + delta,
                    stimulus['ramp_ms'],
                    env['sample_rate_Hz'])

        return left(beep).copy()
    else:
        return silence(stimulus['beep_ms'],env['sample_rate_Hz']).copy()

stimulus['generate_sound'] = generate_sound

def generate_adapter(env,stimulus,condition):
    params = pd.DataFrame({'theta': np.tile(np.linspace(120,-10,130),50),
                           'sigma': np.repeat(np.linspace(0.2,100,50),100),
                           'miss': 0.08})

    params['lp'] = np.log(scipy.stats.norm.pdf(params.theta,loc=0,scale=50)) + \
        np.log(scipy.stats.norm.pdf(params.sigma, loc=0,scale=50))

    return adapters.KTAdapter(-10,np.linspace(90,-30,100),params)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__":
    experiment.start(env,stimulus,phases)

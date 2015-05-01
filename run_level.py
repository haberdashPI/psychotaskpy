
from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import twoAFC
import passive

phases = ['2AFC']

booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
               'middle': 30.7, # calibrated on 10-14-14
               'none': 26}

atten = booth_atten[booth()]
print "Using attenuation of ",atten

env = {'title': 'Tone Detection',
       'debug': True,
       'sample_rate_Hz': 44100,
       'groups': ['Day1','fs_50ms','F_50ms','F30Ps_50ms','F30Pd_50ms','FD_50ms',
                  'fs30Pd_50ms'],
       'default_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 30,
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
    level = stimulus['conditions'][condition]
    return adapters.Stepper(start=-10,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True,min_delta = -200,
                            max_delta = 0)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__":
    experiment.start(env,stimulus,phases)

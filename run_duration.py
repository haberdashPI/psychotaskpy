from util import *
import glob
import adapters
import experiment

# setup the types of phases we want to use
import twoAFC
import passive

phases = ['2AFC','passive_today','passive_static']

booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
               'middle': 30.7, # calibrated on 10-14-14
               'none': 26}

atten = booth_atten[booth()]
print "Using attenuation of ",atten

env = {'title': 'Duration Discrimination',
       'debug': False,
       'sample_rate_Hz': 44100,
       'groups': ['FD_50ms'],
       'default_blocks': 6,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400}

stimulus = {'atten_dB': atten,
            'beep_ms': 15,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'response_delay_ms': 500,
            'passive_delay_ms': 767, # found from average time between responses
            'example_standard': 'Shorter sound',
            'example_signal': 'Longer sound',
            'instructions': 'You will be listening for the longer sound.',
            'question': 'longer',
            'question': 'longer',
            'condition_order': ['d1k50ms','d1k100ms','d4k50ms'],
            'conditions':
            {'d1k50ms': {'length_ms': 50, 'frequency_Hz': 1000,
                         'example_delta': 100},
             'd1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,
                          'example_delta': 100},
             'd4k50ms': {'length_ms': 100, 'frequency_Hz': 4000,
                         'example_delta': 100}}}

def generate_sound(env,stimulus,condition,delta):
    cond = stimulus['conditions'][condition]

    beep = tone(cond['frequency_Hz'],
                stimulus['beep_ms'],
                stimulus['atten_dB'],
                stimulus['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(cond['length_ms'] - stimulus['beep_ms'] + delta,
                    env['sample_rate_Hz'])

    return left(np.vstack([beep,space,beep])).copy()

stimulus['generate_sound'] = generate_sound

def generate_adapter(env,stimulus,condition):
    length = stimulus['conditions'][condition]['length_ms']
    return adapters.Stepper(start=0.1*length,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True,min_delta=0,
							max_delta=stimulus['SOA_ms']/2)
							
env['generate_adapter'] = generate_adapter

experiment.start(env,stimulus,phases)

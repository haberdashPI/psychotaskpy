from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import twoAFC
import passive

phases = ['2AFC','passive_today','passive_static']

booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
               'middle': 30.7, # calibrated on 10-14-14
               'none': 26}

atten = booth_atten[booth()]
print "Using attenuation of ",atten

env = {'title': 'Frequency Discrimination',
       'debug': False,
       'sample_rate_Hz': 44100,
       'groups': ['Day1','F_50ms','F30Ps_50ms','F30Pd_50ms','PF_50ms','FD_50ms'],
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
            'example_standard': 'Higher frequency sound',
            'example_signal': 'Lower frequency sound',
            'example_delta': 100,
            'instructions': 'You will be listening for the lower frequency sound.',
            'question': 'lower in frequency',
            'condition_order': ['f1k50ms','f1k100ms','f4k50ms'],
            'conditions':
            {'f1k50ms': {'length_ms': 50, 'frequency_Hz': 1000, 'example_delta': 100},
             'f1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,'example_delta': 100},
             'f4k50ms': {'length_ms': 100, 'frequency_Hz': 4000, 'example_delta': 100}}}

def generate_tones(env,stimulus,condition,delta):
    cond = stimulus['conditions'][condition]

    beep = tone(cond['frequency_Hz'] - delta,
                stimulus['beep_ms'],
                stimulus['atten_dB'],
                stimulus['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(cond['length_ms'] - stimulus['beep_ms'],
                    env['sample_rate_Hz'])

    return left(np.vstack([beep,space,beep])).copy()

stimulus['generate_tones'] = generate_tones

def generate_adapter(env,stimulus,condition):
    freq = stimulus['conditions'][condition]['frequency_Hz']
    return adapters.Stepper(start=0.1*freq,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True)
env['generate_adapter'] = generate_adapter

experiment.start(env,stimulus,phases)

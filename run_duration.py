from psychopy.sound import Sound
from psychopy.gui import DlgFromDict
from util import *
import glob
import adapters

run = True

booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
               'middle': 30.7, # calibrated on 10-14-14
               'none': 26}
atten = booth_atten[booth()]
print "Using attenuation of ",atten

setup = {'User ID': '0000',
         'Group': ['FD_50ms'],
         'Phase': ['train','passive_today','passive_static'],
         'Condition': ['d1k50ms','d1k100ms','d4k50ms'],
         'Blocks': 6, 'Start Block': 0}
setup_order=['User ID','Group','Phase','Condition','Blocks',
             'Start Block']

env = {'debug': False,
       'sample_rate_Hz': 44100,
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
            'conditions':
            {'d1k50ms': {'length_ms': 50, 'frequency_Hz': 1000,
                         'example_delta': 100},
             'd1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,
                          'example_delta': 100},
             'd4k50ms': {'length_ms': 100, 'frequency_Hz': 4000,
                         'example_delta': 100}}}

def generate_tones(stimulus,env,condition,delta):
    cond = stimulus['conditions'][condition]
    
    beep = tone(cond['frequency_Hz'],
                stimulus['beep_ms'],
                stimulus['atten_dB'],
                stimulus['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(cond['length_ms'] - stimulus['beep_ms'] + delta,
                    env['sample_rate_Hz'])

    stim = left(np.vstack([beep,space,beep]))

    return Sound(stim.copy())

stimulus['generate_tones'] = generate_tones

def generate_adapter(stimulus,condition):
    length = stimulus['conditions'][condition]['length_ms']
    return adapters.Stepper(start=0.1*length,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True)
env['generate_adapter'] = generate_adapter

dialog = DlgFromDict(dictionary=setup,title='Duration Discrimination',
                         order=setup_order)

from run_blocks import blocked_run
# NOTE: we do not import run_blocks until later because of a bug in pscyhopy
# that requires we create the dialog before importing other gui components.

if run and dialog.OK:
    blocked_run(setup['User ID'],setup['Group'],setup['Phase'],
                setup['Condition'],setup['Start Block'],setup['Blocks'],
                stimulus,env)

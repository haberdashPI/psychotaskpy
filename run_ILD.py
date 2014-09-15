from psychopy.sound import Sound
from psychopy.gui import DlgFromDict
from util import *
import glob
import adapters

run = True

# calibrated on 09-15-14
booth_atten = {'corner': {'right': 45.3, 'left': 43.6}, 
               'left': {'right': 42.8, 'left': 41.7}, 
               'none': {'right': 45, 'left': 45}}
atten = booth_atten[booth()]
print "Using attenuation of ",atten

if run:
    setup = {'User ID': '0000',
             'Group': ['Day1','A','P','A_3hP'],
             'Phase': ['train','passive_today'],
             'Condition': ['ILD_4k0dB','ILD_4k6dB','ILD_6k0dB'],
             'Blocks': 5, 'Start Block': 0}
    dialog = DlgFromDict(dictionary=setup,title='ILD',
                         order=['User ID','Group','Phase','Condition',
                                'Blocks','Start Block'])

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400,
       'offset_stimulus_text': False}

stimulus = {'atten_dB': atten, 
            'ramp_ms': 10, 
            'SOA_ms': 950,# ??
            'response_delay_ms': 500,
            'passive_delay_ms': 767,
            'example_standard': 'Sound more to the center',
            'example_signal': 'Sound more to the right',
            'example_delta': 8,
            'start_delta_dB': 6,
            'instructions': 'You will be listening for the sound to your right ear.',
            'question': 'to the right',
            'conditions':
            {'ILD_4k0dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 0},
             'ILD_4k6dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 6},
             'ILD_6k0dB': {'length_ms': 300, 'frequency_Hz': 6000,'offset_dB': 0}}}

def generate_tones_fn(stimulus,env,condition):
    cond = stimulus['conditions'][condition]
    def generate_tones(delta):
        delta + cond['offset_dB']
        left_tone = left(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['left'] + delta/2,
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz']))

        right_tone = right(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['right'] - delta/2,
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz']))

        return Sound((left_tone + right_tone).copy())

    return generate_tones
stimulus['generate_tones_fn'] = generate_tones_fn

def generate_adapter(stimulus,condition):
    return adapters.Stepper(start=stimulus['start_delta_dB'],
                        bigstep=0.5,littlestep=0.25,
                        down=3,up=1,min_delta=0)

env['generate_adapter'] = generate_adapter

from run_blocks import *
# NOTE: we do not import run_blocks until later because of a bug in pscyhopy
# that requires we create the dialog before importing other gui components.

if run and dialog.OK:
    blocked_run(setup['User ID'],setup['Group'],setup['Phase'],
                setup['Condition'],setup['Start Block'],setup['Blocks'],
                stimulus,env)

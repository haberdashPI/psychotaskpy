from psychopy.sound import Sound
from psychopy.gui import DlgFromDict
from util import *
import glob
import adapters

run = True

booth_atten = \
    {'corner': {'right': 45.3, 'left': 43.6}, # calibrated on 09-15-14
     'left': {'right': 42.8, 'left': 41.7},   # calibrated on 09-15-14
     'middle': {'right': 47.8, 'left': 46.7}, # calibrated on 10-14-14
     'none': {'right': 45, 'left': 45}}
atten = booth_atten[booth()]
print "Using attenuation of ",atten

if run:
    setup = {'User ID': '0000',
             'Group': ['Day1','A','P','A_3hP'],
             'Phase': ['train','passive_today'],
             'Condition': ['ILD_4k0dB','ILD_4k6dB','ILD_6k0dB','ITD_500Hz0us'],
             'Blocks': 5, 'Start Block': 0,
             'Starting Level': 0}
    dialog = DlgFromDict(dictionary=setup,title='ILD',
                         order=['User ID','Group','Phase','Condition',
                                'Blocks','Start Block', 'Starting Level'])

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
            'instructions': 'You will be listening for the sound to your right ear.',
            'question': 'to the right',
            'conditions':
            {'ILD_4k0dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 0, 'type': 'ILD',
                             'example_delta': 8},
             'ILD_4k6dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 6, 'type': 'ILD',
                             'example_delta': 8},
             'ILD_6k0dB': {'length_ms': 300, 'frequency_Hz': 6000,'offset_dB': 0, 'type': 'ILD',
                             'example_delta': 8},
             'ITD_500Hz0us': {'length_ms': 300, 'frequency_Hz': 500, 'offset_us': 0, 'type': 'ITD',
                             'example_delta': 200}}}
             
def us_to_phase(us,freq):
    return 2*pi * us/10**6 * freq

def generate_tones_fn(stimulus,env,condition):
    cond = stimulus['conditions'][condition]
    def generate_tones(delta):
        
        if cond['type'] == 'ILD':
            # BUG FIXED: delta was not changed for generalization conditions
            delta = delta + cond['offset_dB']
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
            
        elif cond['type'] == 'ITD':
            delta = delta + cond['offset_us']
            left_tone = left(tone(cond['frequency_Hz'],
                                cond['length_ms'],
                                stimulus['atten_dB']['left'],
                                stimulus['ramp_ms'],
                                env['sample_rate_Hz'],
                                phase = -us_to_phase(delta,cond['frequency_Hz'])/2))
                                
            right_tone = right(tone(cond['frequency_Hz'],
                                cond['length_ms'],
                                stimulus['atten_dB']['left'],
                                stimulus['ramp_ms'],
                                env['sample_rate_Hz'],
                                phase = +us_to_phase(delta,cond['frequency_Hz'])/2))
                                
            return Sound((left_tone + right_tone).copy())
            
        else:
            raise RuntimeError('Unknown stimulus type: ' + cond['type'])
            

    return generate_tones
stimulus['generate_tones_fn'] = generate_tones_fn

def generate_adapter(stimulus,condition):
    cond = stimulus['conditions'][condition]
    if cond['type'] == 'ILD':
        return adapters.Stepper(start=setup['Starting Level'],
                            bigstep=0.5,littlestep=0.25,
                            down=3,up=1,min_delta=0)
    elif cond['type'] == 'ITD':
        return adapters.Stepper(start=setup['Starting Level'],
                    bigstep=10**0.2,littlestep=10**0.05,
                    down=3,up=1,min_delta=1,mult=True)

env['generate_adapter'] = generate_adapter

from run_blocks import *
# NOTE: we do not import run_blocks until later because of a bug in pscyhopy
# that requires we create the dialog before importing other gui components.

if run and dialog.OK:
    blocked_run(setup['User ID'],setup['Group'],setup['Phase'],
                setup['Condition'],setup['Start Block'],setup['Blocks'],
                stimulus,env)

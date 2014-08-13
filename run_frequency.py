from psychopy.sound import Sound
from psychopy.gui import DlgFromDict
from util import *
import glob
import adapters

run = True

# calibrated on 4-29-14
booth_atten = {'corner': 31.5, 'left': 29.6, 'none': 0}
atten = booth_atten[booth()]
print "Using attenuation of ",atten

if run:
    setup = {'User ID': '0000',
             'Group': ['Day1','AA','PP','AA30PP_2'],
             'Phase': ['train','passive_today'],
             'Condition': ['1k50ms','1k100ms','4k50ms'],
             'Blocks': 6, 'Start Block': 0}
    dialog = DlgFromDict(dictionary=setup,title='Frequency Discrimination',
                         order=['User ID','Group','Phase','Condition',
                                'Blocks','Start Block'])

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
            'example_standard': 'Higher frequency sound',
            'example_signal': 'Lower frequency sound',
            'example_delta': 100,
            'instructions': 'You will be listening for the lower frequency sound.',
            'question': 'lower in frequency',
            'conditions':
            {'1k50ms': {'length_ms': 50, 'frequency_Hz': 1000},
             '1k100ms': {'length_ms': 100, 'frequency_Hz': 1000},
             '4k50ms': {'length_ms': 100, 'frequency_Hz': 4000}}}

def generate_tones_fn(stimulus,env,condition):
    cond = stimulus['conditions'][condition]
    def generate_tones(delta):

        beep = tone(cond['frequency_Hz'] - delta,
                    stimulus['beep_ms'],
                    stimulus['atten_dB'],
                    stimulus['ramp_ms'],
                    env['sample_rate_Hz'])

        space = silence(cond['length_ms'] - stimulus['beep_ms'],
                        env['sample_rate_Hz'])

        stim = left(np.vstack([beep,space,beep]))

        return Sound(stim.copy())

    return generate_tones
stimulus['generate_tones_fn'] = generate_tones_fn

def generate_adapter(stimulus,condition):
    freq = stimulus['conditions'][condition]['frequency_Hz']
    return adapters.Stepper(start=0.1*freq,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True)
env['generate_adapter'] = generate_adapter

from run_blocks import blocked_run
# NOTE: we do not import run_blocks until later because of a bug in pscyhopy
# that requires we create the dialog before importing other gui components.

if run and dialog.OK:
    blocked_run(setup['User ID'],setup['Group'],setup['Phase'],
                setup['Condition'],setup['Start Block'],setup['Blocks'],
                stimulus,env)

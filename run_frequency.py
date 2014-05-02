from psychopy.gui import DlgFromDict
from util import *

run = True
# NOTE: this is way up here because of a bug in the GUI
# which requries that we run the dialog before importing
# anything that uses pyglet.media. If we don't do this
# then the dropdown selection of conditions doesn't
# work.

# calibrated on 4-29-14
booth_atten = {'corner': 31.5, 'left': 29.6, 'none': 30}
atten = booth_atten[booth()]
print "Using attenuation of ",atten


if run:
    setup = {'User ID': '0000', 'Group': 'f50p',
             'Phase': ['train','test'],
             'Condition': ['1k50ms','1k100ms','4k50ms'],
             'Blocks': 6, 'Start Block': 0}
    dialog = DlgFromDict(dictionary=setup,title='Frequency Discrimination',
                        order=['User ID','Group','Phase','Condition',
                               'Blocks','Start Block'])

import frequency
import time
import adapters
from psychopy.visual import Window, TextStim
from psychopy.sound import Sound
from psychopy.core import wait


stimulus = {}
env = {}

stimulus = {'atten_dB': atten, 
            'beep_ms': 15,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'response_delay_ms': 500,
            'conditions':
            {'1k50ms': {'length_ms': 50, 'frequency_Hz': 1000},
             '1k100ms': {'length_ms': 100, 'frequency_Hz': 1000},
             '4k50ms': {'length_ms': 100, 'frequency_Hz': 4000}}}

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400}

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

def create_window(env):
    if env['debug']:
        win = Window([400,400])
        win.setMouseVisible(False)
        return win
    else:
        win = Window(fullscr=True)
        win.setMouseVisible(False)
        return win

def blocked_frequency(sid,group,phase,condition,start_block,num_blocks):
    env['win'] = create_window(env)
    env['num_blocks'] = num_blocks
    stimulus['generate'] = generate_tones_fn(stimulus,env,condition)
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['stimulus'] = condition
        info_order = ['sid','group','phase','block','stimulus']

        freq = stimulus['conditions'][condition]['frequency_Hz']
        wait(3.0)

        frequency.examples(env,stimulus)
        
        for i in range(start_block,num_blocks):
            info['block'] = i
            dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")

            env['adapter'] = adapters.Stepper(start=0.1*freq,
                                            bigstep=2,littlestep=np.sqrt(2),
                                            down=3,up=1,mult=True)
            
            frequency.run(env,stimulus,LineWriter(dfile,info,info_order))
    finally:
        env['win'].close()



if run and dialog.OK:
    blocked_frequency(setup['User ID'],setup['Group'],setup['Phase'],
                      setup['Condition'],setup['Start Block'],setup['Blocks'])

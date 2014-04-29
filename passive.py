import pdb

from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info
import random
import numpy as np
import datetime

def examples(env,stimulus):
    high_message = TextStim(env['win'],
                            text='High frequency\n' +
                                 '(Hit any key to continue)')
    low_message = TextStim(env['win'],
                           text='Low frequency\n'+
                                '(Hit any key to continue)')
    responder = KeyboardResponder()

    high_sound = stimulus['generate'](0)
    low_sound = stimulus['generate'](100)

    low = False

    instructions = \
       TextStim(env['win'],
                text='You will be listening for the lower frequency sound.'+
                'Hit any key to hear some examples.')

    instructions.draw()
    env['win'].flip()
    waitKeys()

    clearEvents()
    while not getKeys():
        low = not low
        if low:
            low_message.draw()
            env['win'].flip()
            low_sound.play()
            wait(1,1)
        else:
            high_message.draw()
            env['win'].flip()
            high_sound.play()
            wait(1,1)

def run(env,stimulus,write_line):
    
    env['win'].flip()

    stim_1 = stimulus['generate'](0)
    stim_2 = stimulus['generate'](0)
    
    for trial in range(env['num_trials']):
        signal_interval = random.randint(0,1)

        stim_1.play()

        delay = stim_1.getDuration() + stimulus['SOA_ms'] / 1000.0
        wait(delay,delay)
        
        stim_2.play()

        delay = stim_2.getDuration() + stimulus['response_delay_ms']/1000.0 + \
          stimulus['passive_delay_ms']/1000.0
        wait(delay,delay)
                
        line_info = {'timestamp': datetime.datetime.now()}

        order = ['timestamp']
        
        write_line(line_info,order)

        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)
        
    
    

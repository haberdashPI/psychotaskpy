import pdb

from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info
import random
import numpy as np
import datetime
import pandas as pd
from twoAFC import KeyboardResponder

def run(env,stimulus,write_line):
    
    env['win'].flip()

    stim_1 = stimulus['generate'](0)
    stim_2 = stimulus['generate'](0)

    responder = KeyboardResponder()

    wait(1,1)
    
    for trial in range(env['num_trials']):
        # provide the user an oportunity to escape from the program
        responder.getKeys()
        
        signal_interval = random.randint(0,1)

        stim_1.play()

        delay = stimulus['SOA_ms']/1000.0 - stim_1.getDuration()
        wait(delay,delay)
        
        stim_2.play()

        delay = (stimulus['response_delay_ms']/1000.0 - stim_2.getDuration()) + \
          stimulus['passive_delay_ms']/1000.0
        wait(delay,delay)
                
        line_info = {'timestamp': datetime.datetime.now()}

        order = ['timestamp']
        
        write_line(line_info,order)

        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)
        
def run_track(env,stimulus,track,write_line):
    
    env['win'].flip()

    responder = KeyboardResponder()

    wait(1,1)

    delays_ms = pd.to_datetime(track.timestamp).diff()
    # HACK!! (could be broken by an update to numpy)
    delays_ms = delays_ms.apply(lambda x: x.astype('float64') / 1e6)
    delays_ms[0] = delays_ms.median()

    for track_index,track_row in track.iterrows():
        # provide the user an oportunity to escape from the program
        responder.getKeys()

        signal_interval = track_row['correct_response']
        if signal_interval == 0:
            stim_1 = stimulus['generate'](track_row['delta'])
            stim_2 = stimulus['generate'](0)
            
        else:
            stim_1 = stimulus['generate'](0)
            stim_2 = stimulus['generate'](track_row['delta'])
        
        stim_1.play()

        delay = stimulus['SOA_ms']/1000.0 - stim_1.getDuration()
        wait(delay,delay)
        
        stim_2.play()

        delay = max((stimulus['response_delay_ms']/1000.0 - stim_2.getDuration()),
                    delays_ms[track_index]/1000.0 - stim_2.getDuration() -
                    stimulus['SOA_ms']/1000 - env['feedback_delay_ms']/1000.0)

        wait(delay,delay)
                
        line_info = {'delta': track_row['delta'],
                     'signal_interval': signal_interval,
                     'timestamp': datetime.datetime.now()}

        order = ['delta','signal_interval','timestamp']
        
        write_line(line_info,order)

        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)
        
    
    
    
    

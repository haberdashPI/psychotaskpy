import pdb

from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info
import random
import numpy as np
import datetime

response_1 = 'q'
response_2 = 'p'

class KeyboardResponder:
    def __init__(self):
        self.timer = Clock()

    def get_response(self):
        self.timer.reset()
        response = waitKeys([response_1, response_2],timeStamped=self.timer)[0]
        while not (response[0] == response_1 or response[0] == response_2):
            response = waitKeys([response_1, response_2],timeStamped=self.timer)[0]

        return {'value': int(response[0] == response_2), 'rt': response[1]}

    def wait_for_any_key(self):
        waitKeys()

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
    stim_1_message = TextStim(env['win'],text='Sound 1\t\t\t\t\t\t\t\t')
    stim_2_message = TextStim(env['win'],text='\t\t\t\t\t\t\t\tSound 2')
    start_message = TextStim(env['win'],text='Press any key when you are ready.')
    correct_message = TextStim(env['win'],text='Correct!!')
    incorrect_message = TextStim(env['win'],text='Wrong')

    adapter = env['adapter']
    responder = KeyboardResponder()
    query_message = \
        TextStim(env['win'],
                 text='Was Sound 1 [Q] or Sound 2 [P] lower in frequency?',
                 alignHoriz='center')

    start_message.draw()
    env['win'].flip()
    responder.wait_for_any_key()
    env['win'].flip()
    
    for trial in range(env['num_trials']):
        signal_interval = random.randint(0,1)

        if signal_interval == 0:
            stim_1 = stimulus['generate'](adapter.delta)
            stim_2 = stimulus['generate'](0)
            
        else:
            stim_1 = stimulus['generate'](0)
            stim_2 = stimulus['generate'](adapter.delta)

        stim_1_message.draw()
        env['win'].flip()
        stim_1.play()

        delay = stim_1.getDuration() + stimulus['SOA_ms'] / 1000.0
        wait(delay,delay)

        stim_2_message.draw()
        env['win'].flip()
        stim_2.play()

        delay = stim_2.getDuration() + stimulus['response_delay_ms']/1000.0
        wait(delay,delay)
        
        query_message.draw()
        env['win'].flip()
        response = responder.get_response()

        line_info = {'delta': adapter.delta,
                    'user_response': response['value'],
                    'correct_response': signal_interval,
                    'rt': response['rt'],
                    'threshold': adapter.estimate(),
                    'threshold_sd': adapter.estimate_sd(),
                    'timestamp': datetime.datetime.now()}

        order = ['user_response','correct_response','rt','delta',
                 'threshold','threshold_sd','timestamp']
        
        write_line(line_info,order)

        adapter.update(response['value'],signal_interval)

        if response['value'] == signal_interval: correct_message.draw()
        else: incorrect_message.draw()

        env['win'].flip()
        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)
        
    TextStim(env['win'],
             text='Threshold: %2.3f, SD: %2.3f\n (Hit any key to continue)' %
             (adapter.estimate(),adapter.estimate_sd())).draw()
    env['win'].flip()
    responder.wait_for_any_key()
    
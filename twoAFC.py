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

class UserEscape(Exception):
    pass

class KeyboardResponder:
    def get_response(self):
        response = waitKeys([response_1, response_2],timeStamped=True)[0]
        while not (response[0] == response_1 or response[0] == response_2):
            if response[0] == 'escape':
                raise UserEscape()
            response = waitKeys([response_1, response_2],timeStamped=True)[0]

        return {'value': int(response[0] == response_2), 'rt': response[1]}

    def waitKeys(self):
        response = waitKeys()
        if response[0] == 'escape':
                raise UserEscape()
        return response
        

    def getKeys(self):
        response = getKeys()
        if len(response) > 0 and response[0] == 'escape':
                raise UserEscape()
        return response

def examples(env,stimulus,condition):
    standard_message = TextStim(env['win'],
                            text=stimulus['example_standard']+'\n' +
                                 '(Hit any key to continue)')
    signal_message = TextStim(env['win'],
                            text=stimulus['example_signal']+'\n'+
                                '(Hit any key to continue)')

    responder = KeyboardResponder()

    standard_sound = stimulus['generate'](0)
    signal_sound = stimulus['generate'](stimulus['conditions'][condition]['example_delta'])

    signal = False

    instructions = \
       TextStim(env['win'],
                text=stimulus['instructions']+
                ' Hit any key to hear some examples.')

    instructions.draw()
    env['win'].flip()
    responder.waitKeys()

    clearEvents()
    while not responder.getKeys():
        signal = not signal
        if signal:
            signal_message.draw()
            env['win'].flip()
            signal_sound.play()
            delay = stimulus['SOA_ms']/1000.0
            wait(delay,delay)
        else:
            standard_message.draw()
            env['win'].flip()
            standard_sound.play()
            delay = stimulus['SOA_ms']/1000.0
            wait(delay,delay)

def run(env,stimulus,write_line):
    if 'offset_stimulus_text' not in env or env['offset_stimulus_text']:
        stim_1_message = TextStim(env['win'],text='Sound 1\t\t\t\t\t\t\t\t')
        stim_2_message = TextStim(env['win'],text='\t\t\t\t\t\t\t\tSound 2')
    else:
        stim_1_message = TextStim(env['win'],text='Sound 1')
        stim_2_message = TextStim(env['win'],text='Sound 2')
        
    start_message = TextStim(env['win'],text='Press any key when you are ready.')
    correct_message = TextStim(env['win'],text='Correct!!')
    incorrect_message = TextStim(env['win'],text='Wrong')

    adapter = env['adapter']
    responder = KeyboardResponder()
    query_message = \
        TextStim(env['win'],
                 text='Was Sound 1 [Q] or Sound 2 [P] '+stimulus['question']+'?',
                 alignHoriz='center')

    start_message.draw()
    env['win'].flip()
    responder.waitKeys()
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

        delay = stimulus['SOA_ms']/1000.0
        wait(delay,delay)

        stim_2_message.draw()
        env['win'].flip()
        stim_2.play()
        stim_done_time = getTime()
        
        delay = stim_2.getDuration() + stimulus['response_delay_ms']/1000.0
        wait(delay,delay)
        
        query_message.draw()
        env['win'].flip()
        response = responder.get_response()

        delta = adapter.delta
        adapter.update(response['value'],signal_interval)
    
        line_info = {'delta': delta,
                    'user_response': response['value'],
                    'correct_response': signal_interval,
                    'rt': response['rt'] - stim_done_time,
                    'threshold': adapter.estimate(),
                    'threshold_sd': adapter.estimate_sd(),
                    'timestamp': datetime.datetime.now()}

        order = ['user_response','correct_response','rt','delta',
                 'threshold','threshold_sd','timestamp']
        
        write_line(line_info,order)

        if response['value'] == signal_interval: correct_message.draw()
        else: incorrect_message.draw()

        env['win'].flip()
        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)

    if adapter.mult:
        TextStim(env['win'],
                text='Threshold: %2.3f, SD: %2.1f%%\n (Hit any key to continue)' %
                (adapter.estimate(),100*(adapter.estimate_sd()-1))).draw()
    else:
        TextStim(env['win'],
                text='Threshold: %2.3f, SD: %2.3f\n (Hit any key to continue)' %
                (adapter.estimate(),adapter.estimate_sd())).draw()

    env['win'].flip()
    responder.waitKeys()
    

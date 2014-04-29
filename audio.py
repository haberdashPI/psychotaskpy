import pdb

import pyxid
from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info
import random
import numpy as np
import datetime

use_response_pad = False

if use_response_pad:
    response_1 = 1
    response_2 = 3
else:
    response_1 = 'q'
    response_2 = 'p'

class KeyboardResponder:
    def __init__(self):
        self.timer = Clock()

    def get_response(self):
        self.timer.reset()
        response = waitKeys([response_1, response_2],timeStamped=self.timer)[0]
        return {'value': int(response[0] == response_2), 'rt': response[1]}

    def wait_for_any_key(self):
        waitKeys()

class CedrusPadResponder:
    def __init__(self,short_time_ms = 100):
        pyxid.use_response_pad_timer = True
        devices = pyxid.get_xid_devices()
        self.dev = devices[0]
        self.short_time = short_time_ms / 1000.0;

    def get_response(self):
        self.start_time = self.dev.query_base_time()
        self.dev.clear_response_queue()

        triggered = False

        self.dev.poll_for_response()
        while (self.dev.response_queue_size() > 0) or (not triggered):
            if self.dev.response_queue_size() > 0:
                response = self.dev.get_next_response()
                if response['pressed'] and \
                  (response['key'] == response_1 or \
                   response['key'] == response_2):
                    triggered = True

            wait(self.short_time,self.short_time)
            self.dev.poll_for_response()

        return {'value': int(response['key'] == response_2),
                'rt': (response['time'] - self.start_time) / 1000.0}

    def wait_for_any_key(self):
        triggered = False
        self.dev.clear_response_queue()
        
        # wait for the trigger button to be pressed
        self.dev.poll_for_response()
        while (self.dev.response_queue_size() > 0) or (not triggered):
            if self.dev.response_queue_size() > 0:
                response = self.dev.get_next_response()
                if not response['pressed']:
                    triggered = True
                    
            wait(self.short_time,self.short_time)
            self.dev.poll_for_response()   

def space_stimuli(env,stimulus,deltas=None):
    beep = tone(stimulus['freq_Hz'],stimulus['beep_ms'],
                stimulus['atten_dB'],stimulus['ramp_ms'],
                env['sample_rate_Hz'])
    stim = beep
    if deltas is None:
        intervals = stimulus['intervals']
    else:
        intervals = stimulus['intervals'] + deltas

    for interval in intervals:
        length = env['sample_rate_Hz'] * (interval - stimulus['beep_ms'])/1000.0
        stim = np.vstack([stim, np.zeros((round(length),2)), beep])

    return Sound(stim.copy())

def create_deltas(stimulus,delta):
    intervals = stimulus['intervals']
    deltas = np.zeros(len(intervals))

    sign = random.randint(0,1)*2 - 1
    index = random.randint(1,len(intervals)-1)
    scale = min(intervals[index],intervals[index-1]) - stimulus['beep_ms']

    deltas[index] = scale*delta*sign
    deltas[index-1] = -deltas[index];

    return deltas

def run(env,stimulus,write_line):
    stim_1_message = TextStim(env['win'],text='Sound 1\t\t\t\t\t\t\t\t')
    stim_2_message = TextStim(env['win'],text='\t\t\t\t\t\t\t\tSound 2')
    start_message = TextStim(env['win'],text='Press any key when you are ready.')
    correct_message = TextStim(env['win'],text='Correct!!')
    incorrect_message = TextStim(env['win'],text='Wrong')

    adapter = env['adapter']

    if use_response_pad:
        responder = CedrusPadResponder()
        query_message = \
          TextStim(env['win'],
                   text='Were the sounds\n the SAME[L] or DIFFERENT[R]?',
                   alignHoriz='center')
    else:
        responder = KeyboardResponder()
        query_message = \
          TextStim(env['win'],
                   text='Were the sounds\n the SAME[Q] or DIFFERENT[P]?',
                   alignHoriz='center')

    start_message.draw()
    env['win'].flip()
    responder.wait_for_any_key()
    
    for trial in range(env['num_trials']):
        # same or different trial
        use_different_stimulus = random.randint(0,1) == 0

        stim_1 = space_stimuli(env,stimulus)

        deltas = create_deltas(stimulus,adapter.delta)

        if use_different_stimulus:
            stim_2 = space_stimuli(env,stimulus,deltas)
        else:
            stim_2 = stim_1


        stim_1_message.draw()
        env['win'].flip()
        stim_1.play()

        delay = stim_1.getDuration() + stimulus['SOA_ms'] / 1000.0
        wait(delay,delay)

        stim_2_message.draw()
        env['win'].flip()
        stim_2.play()

        delay = stim_2.getDuration() * 1.1
        wait(delay,delay)

        query_message.draw()
        env['win'].flip()
        response = responder.get_response()

        line_info = {'delta': adapter.delta,
                    'user_response': response['value'],
                    'correct_response': int(use_different_stimulus),
                    'rt': response['rt'],
                    'threshold': adapter.estimate(),
                    'timestamp': datetime.datetime.now()}

        order = ['user_response','correct_response','rt','delta','threshold','timestamp']
        delta_names = ['delta%02d' % x for x in range(len(stimulus['intervals']))]
        order = delta_names + order
        if use_different_stimulus:
            line_info.update(dict(zip(delta_names,deltas)))
        else:
            line_info.update(dict(zip(delta_names,
                                      np.zeros(len(stimulus['intervals'])))))

        write_line(line_info,order)

        adapter.update(response['value'],int(use_different_stimulus))
        if adapter.delta > 1: adapter.delta = 1

        if response['value'] == int(use_different_stimulus): correct_message.draw()
        else: incorrect_message.draw()

        env['win'].flip()
        delay = env['feedback_delay_ms'] / 1000.0
        wait(delay,delay)

    TextStim(env['win'],
             text='Threshold: %2.1f%%' % (adapter.estimate() * 100)).draw()
    env['win'].flip()
    responder.wait_for_any_key()
    

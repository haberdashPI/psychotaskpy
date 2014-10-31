import expyriment as ex

from util import tone, Info
from phase import phase

import random
import numpy as np
import datetime

response_1 = 'q'
response_2 = 'p'

@phase('2AFC')
def train(env,stimulus,condition,block,is_start,write_line):
    if is_start: examples(env,stimulus,condition)
    run(env,stimulus,write_line)

def examples(env,stimulus,condition):
    standard_message = ex.stimuli.TextBox(
                            stimulus['example_standard']+'\n' +
                                 '(Hit any key to continue)',(400,400))
    standard_message.preload()
    signal_message = ex.stimuli.TextBox(
                            stimulus['example_signal']+'\n'+
                                '(Hit any key to continue)',(400,400))
    signal_message.preload()

    standard_sound = stimulus['generate'](0)
    signal_sound = \
      stimulus['generate'](stimulus['conditions'][condition]['example_delta'])

    signal = False

    instructions = \
       ex.stimuli.TextBox(
            stimulus['instructions']+'\nHit any key to hear some examples.',
            (800,400))

    env['exp'].keyboard.clear()
    instructions.present()
    env['exp'].keyboard.wait()

    while env['exp'].keyboard.check() is None:
        signal = not signal
        if signal:
            signal_message.present()
            signal_sound.play()
            env['exp'].clock.wait(stimulus['SOA_ms']) # ? is sound asynchronized? if not I'll have to subtract the sounds length
        else:
            standard_message.present()
            standard_sound.play()
            env['exp'].clock.wait(stimulus['SOA_ms']) # ? is sound asynchronized? if not I'll have to subtract the sounds length

def run(env,stimulus,write_line):
    if 'offset_stimulus_text' not in env or env['offset_stimulus_text']:
        stim_1_message = ex.stimuli.TextLine('Sound 1                                                  ')
        stim_2_message = ex.stimuli.TextLine('                                                  Sound 2')
    else:
        stim_1_message = ex.stimuli.TextLine('Sound 1')
        stim_2_message = ex.stimuli.TextLine('Sound 2')
        
    stim_1_message.preload()
    stim_2_message.preload()

    start_message = ex.stimuli.TextLine('Press any key when you are ready.')
    start_message.preload()
    correct_message = ex.stimuli.TextLine('Correct!!')
    correct_message.preload()
    incorrect_message = ex.stimuli.TextLine('Wrong')
    incorrect_message.preload()
    
    adapter = env['adapter']
    
    query_message = \
        ex.stimuli.TextLine('Was Sound 1 [Q] or Sound 2 [P] '+
                            stimulus['question']+'?')
    query_message.preload()

    start_message.present()
    env['exp'].keyboard.wait()

    for trial in range(env['num_trials']):
        signal_interval = random.randint(0,1)

        if signal_interval == 0:
            stim_1 = stimulus['generate'](adapter.delta)
            stim_2 = stimulus['generate'](0)
            
        else:
            stim_1 = stimulus['generate'](0)
            stim_2 = stimulus['generate'](adapter.delta)

        stim_1_message.present()
        stim_1.play()

        env['exp'].clock.wait(stimulus['SOA_ms'])

        stim_2_message.present()
        stim_2.play()
        
        delay_ms = stim_2.get_length()*1000 + \
          stimulus['response_delay_ms']
        env['exp'].clock.wait(delay_ms)
        
        query_message.present()
        
        response,rt = \
          env['exp'].keyboard.wait_char([response_1,response_2])
        rt += stimulus['response_delay_ms']
        response = int(response == response_2)
        
        delta = adapter.delta
        adapter.update(response,signal_interval)
    
        line_info = {'delta': delta,
                    'user_response': response,
                    'correct_response': signal_interval,
                    'rt': rt,
                    'threshold': adapter.estimate(),
                    'threshold_sd': adapter.estimate_sd(),
                    'timestamp': datetime.datetime.now()}

        order = ['user_response','correct_response','rt','delta',
                 'threshold','threshold_sd','timestamp']
        
        write_line(line_info,order)

        if response == signal_interval:
            correct_message.present()
        else:
            incorrect_message.present()

        env['exp'].clock.wait(env['feedback_delay_ms'])

    if adapter.mult:
        ex.stimuli.TextBox('Threshold: %2.3f, SD: %2.1f%%\n',
                           '(Hit any key to continue)' %
                            (adapter.estimate(),
                             100.0*(adapter.estimate_sd()-1)),
                             (400,400)).present()
    else:
        ex.stimuli.TextBox('Threshold: %2.3f, SD: %2.1f%%\n',
                           '(Hit any key to continue)' %
                            (adapter.estimate(),
                             100.0*(adapter.estimate_sd()-1)),
                             (400,400)).present()

    env['exp'].keyboard.clear()
    env['exp'].keyboard.wait()
    

import expyriment as ex

from util import tone, Info
from phase import phase

import util
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
                                 '(Hit any key to continue)',util.MESSAGE_DIMS)
    standard_message.preload()
    signal_message = ex.stimuli.TextBox(
                            stimulus['example_signal']+'\n'+
                                '(Hit any key to continue)',util.MESSAGE_DIMS)
    signal_message.preload()


    standard_sound = stimulus['generate'](0)
    example_delta = 0
    try:
        example_delta = stimulus['conditions'][condition]['example_delta']
    except:
        example_delta = stimulus['example_delta']
    signal_sound = stimulus['generate'](example_delta)

    signal = False

    instructions = \
       ex.stimuli.TextBox(
            stimulus['instructions']+'\nHit any key to hear some examples.',
            util.MESSAGE_DIMS)

    env['exp'].keyboard.clear()
    instructions.present()
    env['exp'].keyboard.wait()

    while env['exp'].keyboard.check() is None:
        signal = not signal
        if signal:
            signal_message.present()
            signal_sound.play()
            env['exp'].clock.wait(stimulus['SOA_ms'],env['exp'].keyboard.check)
        else:
            standard_message.present()
            standard_sound.play()
            env['exp'].clock.wait(stimulus['SOA_ms'],env['exp'].keyboard.check)

def run(env,stimulus,write_line):
    if stimulus.has_key('sound_labels'):
        sound_1 = stimulus['sound_labels'][0]
        sound_2 = stimulus['sound_labels'][1]
    else:
        sound_1 = 'Sound 1'
        soudn_2 = 'Sound 2'

    if 'offset_stimulus_text' not in env or env['offset_stimulus_text']:
        stim_1_message = ex.stimuli.TextLine(sound_1+'                                                  ')
        stim_2_message = ex.stimuli.TextLine('                                                  '+sound_2)
    else:
        stim_1_message = ex.stimuli.TextLine(sound_1)
        stim_2_message = ex.stimuli.TextLine(sound_2)
        
    stim_1_message.preload()
    stim_2_message.preload()

    start_message = ex.stimuli.TextLine('Press any key when you are ready.')
    start_message.preload()
    correct_message = ex.stimuli.TextLine('Correct!!')
    correct_message.preload()
    incorrect_message = ex.stimuli.TextLine('Wrong')
    incorrect_message.preload()
    
    adapter = env['adapter']
    
    query_message_str = ''
    try: query_message_str = stimulus['full_question']
    except: query_message_str = 'Was '+sound_1+' [Q] or '+sound_2+'  [P] '+\
        stimulus['question']+'?'
    query_message = ex.stimuli.TextLine(query_message_str)
    query_message.preload()

    start_message.present()
    env['exp'].keyboard.wait()

    for trial in range(env['num_trials']):
        env['exp'].keyboard.check()

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
        
        response = None
        while response is None:
            query_message.present()

            # response may come back None if user asks to quit and then
            # cancels, requiring us to poll for a response again
            response,rt = \
                env['exp'].keyboard.wait_char([response_1,response_2])
            

        rt += stimulus['response_delay_ms']
        response = int(response == response_2)

        if response == signal_interval:
            correct_message.present()
        else:
            incorrect_message.present()
        env['exp'].clock.wait(env['feedback_delay_ms'])

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

    if adapter.mult:
        ex.stimuli.TextBox('Threshold: %2.3f, SD: %2.1f%%\n'
                           '(Hit any key to continue)' %
                            (adapter.estimate(),
                             100.0*(adapter.estimate_sd()-1)),
                             util.MESSAGE_DIMS).present()
    else:
        ex.stimuli.TextBox('Threshold: %2.3f, SD: %2.1f\n'
                           '(Hit any key to continue)' %
                            (adapter.estimate(),adapter.estimate_sd()),
                             util.MESSAGE_DIMS).present()

    env['exp'].keyboard.clear()
    env['exp'].keyboard.wait()
    

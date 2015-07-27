import expyriment as ex
import datetime
from itertools import cycle, count
from collections import OrderedDict

import util
from phase import phase, phase_defaults
from settings import Plural, If


@phase('AFC')
def train(env,is_start,write_line):
    if is_start: examples(env)
    run(env,write_line)

@phase_defaults('AFC')
def defaults(env):
    default_question = {'responses': If('alternatives <= 2',['q','p'],
                                                            ['q','b','p']),
                        'feedback': True}

    if env['presentations'] == 1: default_labels = ['']
    else: default_labels = ['Sound '+str(i+1)
                            for i in range(env['presentations'])]

    defaults = {'labels': default_labels,
                'stimulus_label_spacing': 40,
                'report_threshold': True,
                'questions': Plural('question',default_question)}

    return defaults


def setup_message(message_str,use_box=False):
    if use_box:
        message = ex.stimuli.TextBox(message_str,util.MESSAGE_DIMS)
        message.preload()
    else:
        message = ex.stimuli.TextLine(message_str)
        message.preload()

    return message


def examples(env):
    s = env['instructions'] + '\nHit any key to hear some examples.'
    instructions = setup_message(s,True)

    env['exp'].keyboard.clear()
    instructions.present()
    env['exp'].keyboard.wait()
    for example in env['examples']:
        s = example['str']+'\n(Hit any key to continue)'
        example['message'] = setup_message(s,True)

    e = cycle(env['examples'])

    keep_playing = True
    last_sound = None
    clock = env['exp'].clock
    while keep_playing:
        example = e.next()
        example['message'].present()
        last_sound = env['sound'](example['delta'])
        last_sound.play()
        wait_for = clock.time + env['SOA_ms']

        while wait_for > clock.time and keep_playing:   
            if env['exp'].keyboard.check(): keep_playing = False

    if last_sound:
        last_sound.stop()


def build_stim_messages(env):
    labels = env['labels']
    assert isinstance(labels,list)

    spacings = [' '*env['stimulus_label_spacing']
                for i in range(env['presentations'])]
    stim_messages = []
    for i,label in enumerate(labels):
        message_spaces = list(spacings)
        message_spaces[i] = label
        stim_messages.append(setup_message(''.join(message_spaces)))

    return stim_messages


def present_sounds(env,stims,stim_messages):
    stim_sounds = [env['sound'](stim) for stim in stims]

    for i,(sound,message) in enumerate(zip(stim_sounds,stim_messages)):
        if i > 0: env['exp'].clock.wait(env['SOA_ms'])
        message.present()
        sound.play()
        last_sound_start = env['exp'].clock.time

    delay_ms = stim_sounds[-1].get_length()*1000 + env['response_delay_ms']
    env['exp'].clock.wait(delay_ms)
    return last_sound_start + stim_sounds[-1].get_length()*1000


def prepare_feedback():
    correct = setup_message('Correct!!')
    incorrect = setup_message('Wrong')

    def fn(response,correct_response):
        if response == correct_response: correct.present()
        else: incorrect.present()

    return fn


def collect_response(env,feedback,adapter,question,correct_response):

    key_response = None
    while key_response is None:
        question['message'].present()
        start_time = env['exp'].clock.time
        key_response,key_rt = (env['exp'].keyboard.
                               wait_char(question['responses']))

    for i,r in enumerate(question['responses']):
        if r == key_response: response = i
    response_time = start_time + key_rt

    if question['feedback']:
        feedback(response,correct_response)
        env['exp'].clock.wait(env['feedback_delay_ms'])

    return response, response_time

def record_response(env,adapter,response,response_time,correct_response,
                    last_sound_time):
    

    return result


def add_entry(info,name,plural_pattern,values):
    if len(values) > 1:
        for i,v in enumerate(values):
            info[plural_pattern % i] = v
    else: info[name] = values[0]
    return info


def run(env,write_line):
    # prepare text messages
    questions = env['questions']
    for q in questions: q['message'] = setup_message(q['str'])
    stim_messages = build_stim_messages(env)
    start_message = setup_message('Press any key when you are ready.')

    feedback = prepare_feedback()
    adapter = env['adapter']

    # begin the experiment
    start_message.present()
    env['exp'].keyboard.wait()
    for trial in range(env['num_trials']):
        env['exp'].keyboard.check()

        # present sounds
        stims,correct_responses = adapter.next_multi_trial(env['presentations'])
        last_sound_time = present_sounds(env,stims,stim_messages)

        # collect (possibly multiple) responses
        adapters = adapter.single_question_adapters()
        for i,a,correct_response,question in \
                zip(count(),adapters,correct_responses,questions):

            response,rt = collect_response(env,feedback,a,question,
                                           correct_response)

            delta = a.get_delta()
            a.update(response,correct_response)
        
            result = OrderedDict()
            result['trial'] = trial
            result['delta'] = delta
            result['user_response'] = response
            result['correct_response'] = correct_response
            result['rt'] = rt - last_sound_time
            if env['report_threshold']:
                result['threshold'] = a.estimate()
                result['threshold_sd'] = a.estimate_sd()
            result['timestamp'] = datetime.datetime.now()
            if len(adapters) > 1: result['response_index'] = i
            write_line(result,result.keys())

    if env['report_threshold']:
        if adapter.mult:
            t = setup_message(env['condition'] +
                              ' Threshold: %2.3f, SD(log): %2.1f%%\n'
                              '(Hit any key to continue)' %
                              (adapter.estimate(),adapter.estimate_sd()),True)
            t.present()
        else:
            t = setup_message(env['condition']+
                              ' Threshold: %2.3f, SD: %2.1f\n'
                              '(Hit any key to continue)' %
                              (adapter.estimate(),adapter.estimate_sd()),True)
            t.present()

        env['exp'].keyboard.wait()
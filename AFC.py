import expyriment as ex
import datetime
from itertools import cycle

import util
from phase import phase
from settings import prepare, summarize

@phase('2AFC')
def train2(env,is_start,write_line):
    assert env['alternatives'] == 2
    if is_start: examples(env)
    run(env,write_line)


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
    for example in env['stimulus']['examples']:
        s = example['str']+'\n(Hit any key to continue)'
        example['message'] = setup_message(s,True)

    e = cycle(env['stimulus']['examples'])
    while env['exp'].keyboard.check() is None:
        example = e.next()
        example['message'].present()
        env['sound'](example['delta']).play()
        env['exp'].clock.wait(env['SOA_ms'],env['exp'].keyboard.check)

def default_labels(env):
    if env['alternatives'] == 1:
        return ''
    else: return ['Sound '+str(i+1) for i in range(env['alternatives'])]


def default_responses(env):
    responses = {1: ['q','p'], 2: ['q','p'], 3: ['q','b','p']}
    return responses[env['alternatives']]


def build_stim_messages(env):
    labels = env['labels']
    spacings = [' '*env['stimulus_label_spacing']
                for i in range(env['alternatives'])]
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

    delay_ms = stim_sounds[-1].get_length()*1000 + env['response_delay_ms']
    env['exp'].clock.wait(delay_ms)


def prepare_feedback():
    correct = setup_message('Correct!!')
    incorrect =  setup_message('Wrong')
    def fn(response,correct_response):
        if response == correct_response: correct.present()
        else: incorrect.present()

    return fn


def collect_response(env,feedback,correct_response,question,offset):
    key_response = None
    while key_response is None:
        question['message'].present()
        key_response,key_rt = (env['exp'].keyboard.
                               wait_char(question['responses']))

    for i,r in enumerate(question['responses']):
        if r == key_response: response = i
    rt = key_rt + offset

    if question['feedback']:
        feedback(response,correct_response)
        env['exp'].clock.wait(env['feedback_delay_ms'])

    return response,rt


def run(env,write_line):
    defaults = {'labels': default_labels(env),
                'stimulus_label_spacing': 40,
                'responses': default_responses(env),
                'labels': default_labels(env),
                'feedback': True,
                'followup_questions': []}
    env = prepare(env,defaults,True)

    stim_messages = build_stim_messages(env)
    start_message = setup_message('Press any key when you are ready.')
    _,question = summarize(env,['responses','labels','feedback','question'])
    questions = [question] + env['followup_questions']
    for q in questions: q['message'] = setup_message(q['question'])

    feedback = prepare_feedback()
    adapter = env['adapter']

    start_message.present()
    env['exp'].keyboard.wait()
    for trial in range(env['num_trials']):
        env['exp'].keyboard.check()

        correct_responses,stims = adapter.select_deltas(env['alternatives'])
        present_sounds(env,stims,stim_messages)

        offset = env['response_delay_ms']
        responses = []
        for i,(correct,q) in enumerate(zip(correct_responses,questions)):
            response,rt = collect_response(env,feedback,correct,q,offset)
            responses.append(response)
            if i == 0: question_rt = rt

        delta = adapter.delta
        adapter.update_all(responses,correct_responses)

        line_info = {'delta': delta,
                     'user_response': response,
                     'correct_response': correct_responses[0],
                     'rt': question_rt,
                     'threshold': adapter.estimate(),
                     'threshold_sd': adapter.estimate_sd(),
                     'timestamp': datetime.datetime.now()}

        order = ['user_response','correct_response','rt','delta',
                 'threshold','threshold_sd','timestamp']

        for i,r in enumerate(responses[1:]):
            key = 'followup%02d' % (i+1)
            line_info[key] = r
            order.append(key)

            key = 'followup_correct%02d' % (i+1)
            line_info[key] = correct_responses[i+1]
            order.append(key)

        write_line(line_info,order)

    if adapter.mult:
        t = setup_message(env['condition']+' Threshold: %2.3f, SD(log): %2.1f%%\n'
                      '(Hit any key to continue)' %
                      (adapter.estimate(),adapter.estimate_sd()),True)
        t.present()
    else:
        t = setup_message(env['condition']+' Threshold: %2.3f, SD: %2.1f\n'
                      '(Hit any key to continue)' %
                      (adapter.estimate(),adapter.estimate_sd()),True)
        t.present()

    env['exp'].keyboard.wait()

from util import *
import adapters
import experiment

# setup the types of phases we want to use
import AFC
import passive

phases = ['2AFC','passive_today','passive_static']

booth_atten = {'corner': 27.6, # calibrated on 9-15-14
               'left': 9.3,    # calibrated on 05-20-15
               'middle': 30.7, # calibrated on 10-14-14
               'right': 31.1,  # calibrated on 04-15-15
               'none': 26}

atten = booth_atten[booth()]
print "Using attenuation of ",atten

groups = ['FD_50ms','fs24D_50ms']

stimuli = {'d1k50ms': {'length_ms': 50, 'frequency_Hz': 1000,
                       'examples': [{'str': 'Shorter sound','delta': 0},
                                    {'str': 'Longer sound','delta': 25}]},
           'd1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,
                        'example': [{'str': 'Shorter sound','delta': 0},
                                    {'str': 'Longer sound','delta': 50}]},
           'd4k50ms': {'length_ms': 100, 'frequency_Hz': 4000,
                       'example': [{'str': 'Shorter sound','delta': 0},
                                   {'str': 'Longer sound','delta': 50}]}}


env = {}

env = {'title': 'Duration Discrimination',
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400,
       'beep_ms': 15,
       'ramp_ms': 5,
       'SOA_ms': 900,
       'response_delay_ms': 500,
       'passive_delay_ms': 767,  # found from average time between response
       'instructions': 'You will be listening for the longer sound.',
       'alternatives': 2,
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'phase': UserSelect('Phase',phases,priority=2),
       'stimulus': UserSelect('Stimulus',['f1k50ms','f1k100ms','f4k50ms'],
                              stimuli,priority=3),
       'num_blocks': UserNumber('Blocks',6,priority=4),
       'question': Vars('Was {labels[0]} [{responses[0]}] or ' +
                        '{labels[1]} [{responses[1]}] longer?')}

def generate_sound(env,stimulus,condition,delta):
    beep = tone(env['stimulus']['frequency_Hz'],
                env['beep_ms'],
                env['atten_dB'],
                env['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(env['stimulus']['length_ms'] - env['beep_ms'] + delta,
                    env['sample_rate_Hz'])

    return left(np.vstack([beep,space,beep])).copy()
stimulus['generate_sound'] = generate_sound


def generate_adapter(env,stimulus,condition):
    length = env['stimulus']['length_ms']
    return adapters.Stepper(start=0.1*length,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True,min_delta=0,
                            max_delta=stimulus['SOA_ms']/2)
env['generate_adapter'] = generate_adapter

if __name__ == "__main__": experiment.start(env)

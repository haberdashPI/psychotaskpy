from util import *
from settings import *
import adapters
import experiment
import calibrate

# setup the types of phases we want to use
import AFC
import passive

phases = ['AFC','passive_today','passive_static','passive_random']
atten = calibrate.atten_86dB_for_left[booth()]
print "Using attenuation of ",atten

groups = ['Day1','f','fp','f30p','f4hp','f24p','f7Dp']
exposures = ['matched_notask','static_notask','interval_notask','interval_task','none']

conditions = {'d1k50ms': {'length_ms': 50, 'frequency_Hz': 1000,
                          'examples': [{'str': 'Shorter sound','delta': 0},
                                       {'str': 'Longer sound','delta': 25}]},
              'd1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,
                           'examples': [{'str': 'Shorter sound','delta': 0},
                                        {'str': 'Longer sound','delta': 50}]},
              'd4k50ms': {'length_ms': 100, 'frequency_Hz': 4000,
                          'examples': [{'str': 'Shorter sound','delta': 0},
                                       {'str': 'Longer sound','delta': 50}]}}


env = {'title': 'Duration Discrimination',
       'passive_files': np.load('../data/d1k50ms_files.npy'),
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': UserSelect('Trials',[60,45],priority=5),
       'feedback_delay_ms': 400,
       'beep_ms': 15,
       'ramp_ms': 5,
       'SOA_ms': 900,
       'response_delay_ms': 500,
       'passive_delay_ms': 767,  # found from average time between response
       'presentations': 2,
       'instructions': 'You will be listening for the longer sound.',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'exposure': UserSelect('Exposure Type',exposures,priority=1.5),
       'phase': UserSelect('Phase',phases,priority=2),
       'condition': UserSelect('Condition',['d1k50ms','d1k100ms','d4k50ms'],
                               conditions,priority=3),
       'num_blocks': UserNumber('Blocks',6,priority=4),
       'write_to_file': Amend('exposure'),
       'question':
        {'str': Vars('Was {labels[0]} [{responses[0]}] or ' +
                     '{labels[1]} [{responses[1]}] longer?'),
         'alternatives': 2}}

def generate_sound(env,delta):
    beep = tone(env['frequency_Hz'],
                env['beep_ms'],
                env['atten_dB'],
                env['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(env['length_ms'] - env['beep_ms'] + delta,
                    env['sample_rate_Hz'])

    return left(np.vstack([beep,space,beep])).copy()
env['generate_sound'] = generate_sound


def generate_adapter(env):
    length = env['length_ms']
    return adapters.Stepper(start=0.1*length,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True,min_delta=0,
                            max_delta=env['SOA_ms']/2)
env['generate_adapter'] = generate_adapter

if __name__ == "__main__": experiment.start(env)

from util import *
from settings import *
import adapters
import experiment

# setup the types of phases we want to use
import AFC
import passive

phases = ['AFC','passive_today','passive_yesterday','passive_first']

booth_atten = {'corner': 27.6,  # calibrated on 9-15-14
               'left': 9.3,     # calibrated on 05-20-15
               'middle': 30.7,  # calibrated on 10-14-14
               'right': 31.1,   # calibrated on 04-15-15
               'none': 26}

atten = booth_atten[booth()]
print "Using attenuation of ",atten


groups = ['Day1','fs24D_50ms','fs24Pd_50ms','fs24D_50ms','fs7dPd_50ms']

conditions = {'f1k50ms': {'length_ms': 50, 'frequency_Hz': 1000,
                          'examples': [{'str': 'Higher frequency sound',
                                        'delta': 0},
                                       {'str': 'Lower frequency sound',
                                        'delta': 100}]},
              'f1k100ms': {'length_ms': 100, 'frequency_Hz': 1000,
                           'examples': [{'str': 'Higher frequency sound',
                                         'delta': 0},
                                        {'str': 'Lower frequency sound',
                                         'delta': 100}]},
              'f4k50ms': {'length_ms': 100, 'frequency_Hz': 4000,
                          'examples': [{'str': 'Higher frequency sound',
                                        'delta': 0},
                                       {'str': 'Lower frequency sound',
                                        'delta': 400}]}}

env = {'title': 'Frequency Discrimination',
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
       'instructions': 'You will be listening for the lower frequency sound.',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'phase': UserSelect('Phase',phases,priority=2),
       'condition': UserSelect('Condition',['f1k50ms','f1k100ms','f4k50ms'],
                               conditions,priority=3),
       'num_blocks': UserNumber('Blocks',6,priority=4),
       'question':
        {'str': Vars('Was {labels[0]} [{responses[0]}] or ' +
                     '{labels[1]} [{responses[1]}] lower in frequency?'),
         'alternatives': 2}}

def generate_sound(env,delta):
    beep = tone(env['frequency_Hz'] - delta,
                env['beep_ms'],
                env['atten_dB'],
                env['ramp_ms'],
                env['sample_rate_Hz'])

    space = silence(env['length_ms'] - env['beep_ms'],
                    env['sample_rate_Hz'])

    return left(np.vstack([beep,space,beep])).copy()
env['generate_sound'] = generate_sound


def generate_adapter(env):
    freq = env['frequency_Hz']
    min_freq = 300
    return adapters.Stepper(start=0.1*freq,bigstep=2,littlestep=np.sqrt(2),
                            down=3,up=1,mult=True,min_delta=0,
                            max_delta=freq - min_freq)
env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__": experiment.start(env)

from util import *
from settings import *
import adapters
import experiment
import calibrate

# setup the types of phases we want to use
import AFC
import passive

phases = ['AFC','passive_today','passive_yesterday']

atten = calibrate.atten_70dB_for_LR[booth()]
print "Using attenuation of ",atten


groups = ['Day1','fs_50ms','F_50ms','F30Ps_50ms','F30Pd_50ms',
          'FD_50ms','fs30Pd_50ms','fs24Pd_50ms']

conditions = {'ILD_4k0dB':
              {'frequency_Hz': 4000,'offset_dB': 0,
               'type': 'ILD',
               'examples': [{'str': 'Sound more to the center','delta': 0},
                            {'str': 'Sound more to the right','delta': 8}]},
              'ILD_4k6dB':
              {'frequency_Hz': 4000,'offset_dB': 6,
               'type': 'ILD',
               'examples': [{'str': 'Sound more to the center','delta': 0},
                            {'str': 'Sound more to the right','delta': 8}]},
              'ILD_6k0dB':
              {'frequency_Hz': 6000,'offset_dB': 0,
               'type': 'ILD',
               'examples': [{'str': 'Sound more to the center','delta': 0},
                            {'str': 'Sound more to the right','delta': 8}]},
              'ITD_500Hz0us':
              {'frequency_Hz': 500, 'offset_us': 0,
               'type': 'ITD',
               'examples': [{'str': 'Sound more to the center','delta': 0},
                            {'str': 'Sound more to the right','delta': 200}]},
              'ITD_500Hz200us':
              {'frequency_Hz': 500,'offset_us': 200,
               'type': 'ITD',
               'examples': [{'str': 'Sound more to the center','delta': 0},
                            {'str': 'Sound more to the right','delta': 200}]}}


env = {'title': 'Frequency Discrimination',
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'debug': False,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400,
       'ramp_ms': 10,
       'SOA_ms': 900,
       'response_delay_ms': 500,
       'presentations': 2,
       'length_ms': 300,
       'instructions': 'You will be listening for the sound to your right ear.',
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'phase': UserSelect('Phase',phases,priority=2),
       'condition': UserSelect('Condition',['ILD_4k0dB','ILD_4k6dB','ILD_6k0dB',
                                            'ITD_500Hz0us','ITD_500Hz200us'],
                               conditions,priority=3),
       'starting_level': UserNumber('Starting Level',6,priority=4),
       'num_blocks': UserNumber('Blocks',5,priority=5),
       'stimulus_label_spacing': 0,
       'question': {'str': Vars('Was {labels[0]} [{responses[0]}] or ' +
                                '{labels[1]} [{responses[1]}] more to the right?'),
                    'alternatives': 2}}


# convert microseconds into phase differences
def us_to_phase(us,freq):
    return 2*pi * us/10**6 * freq


def generate_sound(env,delta):
    freq_Hz = env['frequency_Hz']
    if env['type'] == 'ILD':
        delta = delta + env['offset_dB']
        left_tone = left(tone(freq_Hz,
                              env['length_ms'],
                              env['atten_dB']['left'][freq_Hz] + delta/2,
                              env['ramp_ms'],
                              env['sample_rate_Hz']))

        right_tone = right(tone(freq_Hz,
                                env['length_ms'],
                                env['atten_dB']['right'][freq_Hz] - delta/2,
                                env['ramp_ms'],
                                env['sample_rate_Hz']))

        return (left_tone + right_tone).copy()

    elif env['type'] == 'ITD':
        delta = delta + env['offset_us']
        phase = -us_to_phase(delta,freq_Hz)/2
        left_tone = left(tone(freq_Hz,
                              env['length_ms'],
                              env['atten_dB']['left'][freq_Hz],
                              env['ramp_ms'],
                              env['sample_rate_Hz'],
                              phase=phase))

        phase = +us_to_phase(delta,freq_Hz)/2
        right_tone = right(tone(freq_Hz,
                                env['length_ms'],
                                env['atten_dB']['right'][freq_Hz],
                                env['ramp_ms'],
                                env['sample_rate_Hz'],
                                phase=phase))

        return (left_tone + right_tone).copy()

    else:
        raise RuntimeError('Unknown condition type: ' +
                           env['type'])
env['generate_sound'] = generate_sound


def generate_adapter(env):
    if env['type'] == 'ILD':
        return adapters.Stepper(start=env['starting_level'],
                                bigstep=0.5,littlestep=0.25,
                                down=3,up=1,min_delta=0)
    elif env['type'] == 'ITD':
        return adapters.Stepper(start=env['starting_level'],
                                bigstep=10**0.2,littlestep=10**0.05,
                                down=3,up=1,min_delta=1,mult=True)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__": experiment.start(env)

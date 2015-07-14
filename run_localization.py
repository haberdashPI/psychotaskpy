from util import *
from settings import *
import adapters
import experiment

# setup the types of phases we want to use
import AFC
import passive

phases = ['2AFC','passive_today','passive_yesterday']

booth_atten = {'corner': {'right': 45.3, 'left': 43.6},  # calibrated on 09-15-14
               'left':   {'right': 42.8, 'left': 41.7},  # calibrated on 09-15-14
               'middle': {'right': 47.8, 'left': 46.7},  # calibrated on 10-14-14
               'none':   {'right': 45, 'left': 45}}

atten = booth_atten[booth()]
print "Using attenuation of ",atten


groups = ['Day1','fs_50ms','F_50ms','F30Ps_50ms','F30Pd_50ms',
          'FD_50ms','fs30Pd_50ms','fs24Pd_50ms']

stimuli = {'ILD_4k0dB':
           {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 0,'type': 'ILD',
            'examples': [{'str': 'Sound more to the center','delta': 0}
                         {'str': 'Sound more to the right','delta': 8}]},
            'ILD_4k6dB':
            {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 6,
             'type': 'ILD',
             'examples': [{'str': 'Sound more to the center','delta': 0}
                          {'str': 'Sound more to the right','delta': 8}]},
             'ILD_6k0dB':
            {'length_ms': 300, 'frequency_Hz': 6000,'offset_dB': 0,
             'type': 'ILD',
             'examples': [{'str': 'Sound more to the center','delta': 0}
                          {'str': 'Sound more to the right','delta': 8}]},
            'ITD_500Hz0us':
            {'length_ms': 300, 'frequency_Hz': 500, 'offset_us': 0,
             'type': 'ITD',
             'examples': [{'str': 'Sound more to the center','delta': 0}
                          {'str': 'Sound more to the right','delta': 200}]},
            'ITD_500Hz200us':
            {'length_ms': 300, 'frequency_Hz': 500,'offset_us': 200,
             'type': 'ITD',
             'examples': [{'str': 'Sound more to the center','delta': 0}
                          {'str': 'Sound more to the right','delta': 200}]}}

env = {'title': 'Frequency Discrimination',
       'sample_rate_Hz': 44100,
       'atten_dB': atten,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400,
       'ramp_ms': 10,
       'SOA_ms': 900,
       'response_delay_ms': 500,
       'passive_delay_ms': 767,  # found from average time between response
       'instructions': 'You will be listening for the sound to your right ear.',
       'alternatives': 2,
       'sid': UserNumber('Subject ID',0,priority=0),
       'group': UserSelect('Group',groups,priority=1),
       'phase': UserSelect('Phase',phases,priority=2),
       'stimulus': UserSelect('Stimulus',['f1k50ms','f1k100ms','f4k50ms'],
                              stimuli,priority=3),
       'starting_level': UserNumber('Starting Level',6,priority=4),
       'num_blocks': UserNumber('Blocks',6,priority=5),
       'stimulus_label_spacing': 0,
       'question': Vars('Was {labels[0]} [{responses[0]}] or ' +
                         '{labels[1]} [{responses[1]}] lower in frequency?')}


# convert microseconds into phase differences
def us_to_phase(us,freq):
    return 2*pi * us/10**6 * freq


def generate_sound(env,delta):
    if env['stimulus']['type'] == 'ILD':
        delta = delta + env['stimulus']['offset_dB']
        left_tone = left(tone(env['stimulus']['frequency_Hz'],
                              env['stimulus']['length_ms'],
                              env['atten_dB']['left'] + delta/2,
                              env['ramp_ms'],
                              env['sample_rate_Hz']))

        right_tone = right(tone(env['stimulus']['frequency_Hz'],
                                env['stimulus']['length_ms'],
                                env['atten_dB']['right'] - delta/2,
                                env['ramp_ms'],
                                env['sample_rate_Hz']))

        return (left_tone + right_tone).copy()

    elif env['stimulus']['type'] == 'ITD':
        delta = delta + env['stimulus']['offset_us']
        phase = -us_to_phase(delta,env['stimulus']['frequency_Hz'])/2
        left_tone = left(tone(env['stimulus']['frequency_Hz'],
                              env['stimulus']['length_ms'],
                              env['atten_dB']['left'],
                              env['ramp_ms'],
                              env['sample_rate_Hz'],
                              phase=phase))

        phase = +us_to_phase(delta,env['stimulus']['frequency_Hz'])/2
        right_tone = right(tone(env['stimulus']['frequency_Hz'],
                                env['stimulus']['length_ms'],
                                env['atten_dB']['left'],
                                env['ramp_ms'],
                                env['sample_rate_Hz'],
                                phase=phase))

        return (left_tone + right_tone).copy()

    else:
        raise RuntimeError('Unknown stimulus type: ' + env['stimulus']['type'])
env['generate_sound'] = generate_sound


def generate_adapter(env,stimulus,condition):
    if env['stimulus']['type'] == 'ILD':
        return adapters.Stepper(start=env['fields']['starting_level'],
                                bigstep=0.5,littlestep=0.25,
                                down=3,up=1,min_delta=0)
    elif env['stimulus']['type'] == 'ITD':
        return adapters.Stepper(start=env['fields']['starting_level'],
                                bigstep=10**0.2,littlestep=10**0.05,
                                down=3,up=1,min_delta=1,mult=True)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__": experiment.start(env)

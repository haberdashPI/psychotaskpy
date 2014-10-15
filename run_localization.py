from util import *
import glob
import adapters
import experiment

run = True

booth_atten = \
    {'corner': {'right': 45.3, 'left': 43.6}, # calibrated on 09-15-14
     'left': {'right': 42.8, 'left': 41.7},   # calibrated on 09-15-14
     'middle': {'right': 47.8, 'left': 46.7}, # calibrated on 10-14-14
     'none': {'right': 45, 'left': 45}}
atten = booth_atten[booth()]
print "Using attenuation of ",atten

env = {'title': 'Frequency Discrimination',
       'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': '../data',
       'num_trials': 60,
       'default_blocks': 5,
       'feedback_delay_ms': 400,
       'groups': ['Day1','A','P','A_3hP','L30TLp','L24LToff'],
       'fields': {'Starting Level': 6},
       'field_order': ['Starting Level'],
       'offset_stimulus_text': False}

stimulus = {'atten_dB': atten, 
            'ramp_ms': 10, 
            'SOA_ms': 950,# ??
            'response_delay_ms': 500,
            'passive_delay_ms': 767,
            'example_standard': 'Sound more to the center',
            'example_signal': 'Sound more to the right',
            'instructions': 'You will be listening for the sound to your right ear.',
            'question': 'to the right',
            'condition_order': ['ILD_4k0dB','ILD_4k6dB','ILD_6k0dB',
                                'ITD_500Hz0us','ITD_500Hz200us'],
            'conditions':
            {'ILD_4k0dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 0,
                            'type': 'ILD','example_delta': 8},
             'ILD_4k6dB': {'length_ms': 300, 'frequency_Hz': 4000,'offset_dB': 6,
                           'type': 'ILD','example_delta': 8},
             'ILD_6k0dB': {'length_ms': 300, 'frequency_Hz': 6000,'offset_dB': 0,
                           'type': 'ILD','example_delta': 8},
             'ITD_500Hz0us': {'length_ms': 300, 'frequency_Hz': 500, 'offset_us': 0,
                              'type': 'ITD','example_delta': 200},
			 'ITD_500Hz200us' : {'length_ms': 300, 'frequency_Hz': 500,
                                  'offset_us': 200, 'type': 'ITD',
                                  'example_delta': 200}}}

# convert microseconds into phase differences
def us_to_phase(us,freq):
    return 2*pi * us/10**6 * freq

def generate_tones(env,stimulus,condition,delta):
    cond = stimulus['conditions'][condition]

    if cond['type'] == 'ILD':
        delta = delta + cond['offset_dB']
        left_tone = left(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['left'] + delta/2,
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz']))

        right_tone = right(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['right'] - delta/2,
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz']))

        return (left_tone + right_tone).copy()

    elif cond['type'] == 'ITD':
        delta = delta + cond['offset_us']
        left_tone = left(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['left'],
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz'],
                            phase = -us_to_phase(delta,cond['frequency_Hz'])/2))

        right_tone = right(tone(cond['frequency_Hz'],
                            cond['length_ms'],
                            stimulus['atten_dB']['left'],
                            stimulus['ramp_ms'],
                            env['sample_rate_Hz'],
                            phase = +us_to_phase(delta,cond['frequency_Hz'])/2))

        return (left_tone + right_tone).copy()

    else:
        raise RuntimeError('Unknown stimulus type: ' + cond['type'])
stimulus['generate_tones'] = generate_tones

def generate_adapter(env,stimulus,condition):
    cond = stimulus['conditions'][condition]
    if cond['type'] == 'ILD':
        return adapters.Stepper(start=env['fields']['Starting Level'],
                            bigstep=0.5,littlestep=0.25,
                            down=3,up=1,min_delta=0)
    elif cond['type'] == 'ITD':
        return adapters.Stepper(start=env['fields']['Starting Level'],
                    bigstep=10**0.2,littlestep=10**0.05,
                    down=3,up=1,min_delta=1,mult=True)

env['generate_adapter'] = generate_adapter

experiment.start(env,stimulus)

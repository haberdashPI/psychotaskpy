from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import motor
import passive

phases = ['motor_synch']

env = {'title': 'Frequency Discrimination',
       'use_response_pad': True,
       'countdown_interval': 750,
       'countdown_length': 3,
       'debug': True,
       'sample_rate_Hz': 44100,
       'groups': ['Test'],
       'default_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 60,
       'feedback_delay_ms': 400}
    
rhythm = 'A'
stimulus = {'atten_dB': 20, # TODO: calibration
            'freq_Hz': 250,
            'beep_ms': 25,
            'ramp_ms': 10,
            'instructions': 'Tap along to the rhythm you hear. Continue to repeat the rhythm once the sound stops. ',
            'intervals': rhythm_intervals(rhythm),
            'continuation_ms': 4700,#47000,
            'n_synch': 1,#6,
            'condition_order': ['rhtyhm A']}

def generate_tones(env,stimulus,condition,repeat):
    beep = tone(stimulus['freq_Hz'],stimulus['beep_ms'],
                stimulus['atten_dB'],stimulus['ramp_ms'],
                env['sample_rate_Hz'])
    sound = beep.copy()
    for cycle in range(stimulus['n_synch']):
        for interval in stimulus['intervals']:
            sound = np.vstack([sound, silence(interval,env['sample_rate_Hz']),
                               beep.copy()])
    return sound
stimulus['generate_tones'] = generate_tones

experiment.start(env,stimulus,phases)

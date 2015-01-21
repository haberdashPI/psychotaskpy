################################################################################
from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import motor
import passive

phases = ['motor_synch','motor_monitor']

env = {'title': 'Motor Synchronization',
       'use_response_pad': True,
       'countdown_interval': 750,
       'countdown_length': 3,
       'debug': False,
       'sample_rate_Hz': 44100,
       'groups': ['Test'],
       'default_blocks': 6,
       'data_file_dir': '../data'}
    
rhythm = 'A2'
intervals = {'A':  [107, 429, 214, 1065, 536, 643, 321, 857],
             'A2': [640, 160, 560, 960, 320, 400, 240, 720],
             'B2': [320, 1040, 800, 160, 240, 400, 480, 560]}

stimulus = {'atten_dB': 20,
            'freq_Hz': 250,
            'beep_ms': 25,
            'ramp_ms': 10,
            'instructions': 'Tap along to the rhythm you hear. '+
                 'Continue to repeat the rhythm once the sound stops. ',
            'intervals': intervals[rhythm],
            'continuation_ms': 47000,
            'n_synch': 6,
            'condition_order': ['rhythm A','rhtyhm A2','rhythm B2'],
            'random_seeds': [ 1986, 31051,  6396, 21861, 15014,  1988,  2051,
                              27160, 17545, 21009 ],
            'monitor_instructions': 'Tap the bottom left button whenever you '+
                                    'hear a deviation from the rhythm.',
            'n_monitor': 8,
            'n_deviants': 3,
            'n_deviant_wait': 2,
            'deviant_ms': 200}

def generate_sound(env,stimulus,condition,repeat=1,random_seed=None):
    beep = tone(stimulus['freq_Hz'],stimulus['beep_ms'],
                stimulus['atten_dB'],stimulus['ramp_ms'],
                env['sample_rate_Hz'])

    intervals,deviants = generate_intervals_and_deviants(stimulus,repeat,random_seed)

    sound = beep.copy()
    for interval in intervals:
        sound = np.vstack([sound, silence(interval,env['sample_rate_Hz']), beep.copy()])

    return sound,deviants
stimulus['generate_sound'] = generate_sound

def generate_intervals_and_deviants(stimulus,repeat,random_seed):
    rhythm_N = len(stimulus['intervals'])
    intervals = np.tile(stimulus['intervals'],repeat)
    
    if random_seed is None:
        return intervals,[]

    else:
        with RandomSeed(random_seed):
            n_deviants = np.random.randint(stimulus['n_deviants']+1)
            deviant_indices = np.random.random_integers(rhythm_N*stimulus['n_deviant_wait'],
                                                        rhythm_N*stimulus['n_monitor']-1,
                                                        size=n_deviants)
            deviant_dirs = np.random.choice([-1,1],n_deviants)

        # deviate events, possibly changing the order if the
        # difference is greater than the interval separating two events.
        events = np.cumsum(intervals)
        events[deviant_indices] += deviant_dirs*stimulus['deviant_ms']
        intervals = np.ediff1d(np.sort(events),to_begin=events[0])
        return intervals,events[deviant_indices]

experiment.start(env,stimulus,phases)

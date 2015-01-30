################################################################################
from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import motor
import passive

phases = ['motor_synch','motor_monitor','motor_mixed']

env = {'title': 'Motor Synchronization',
       'use_response_pad': True,
       'countdown_interval': 750,
       'countdown_length': 3,
       'debug': False,
       'sample_rate_Hz': 44100,
       'groups': ['Test'],
       'default_blocks': 4,
       'data_file_dir': '../data'}
    
stimulus = {'atten_dB': 20,
            'beep_ms': 25,
            'ramp_ms': 10,
            'instructions': {'motor_synch': 'Tap along to the rhythm you hear. '+
                                  'Continue to repeat the rhythm once the sound stops. ',
                             'motor_monitor': 'Tap the bottom left button whenever you '+
                                    'hear a deviation from the rhythm.',
                             'motor_mixed': 'Tap along to the rhythm you hear. '+
                                 'When you see "Stop tapping!", just listen to the rhythm'+
                                 ' and tap the buton any time you hear a deviation from the'+
                                 ' rhythm.'},
            'condition_order': ['A0','A','B','A1k'],                                    
            'intervals_ms': {'A0':  [107, 429, 214, 1065, 536, 643, 321, 857],
                            'A':   [640, 160, 560, 960, 320, 400, 240, 720],
                            'A1k': [640, 160, 560, 960, 320, 400, 240, 720],
                            'B':   [320, 1040, 800, 160, 240, 400, 480, 560]},
            'freq_Hz' : {'A0': 250, 'A': 250, 'B': 250, 'A1k': 1000},
            'continuation_ms': {'motor_synch': 47000, 'motor_monitor': 0, 'motor_mixed': 0},
            'random_seeds': [ 1986, 31051,  6396, 21861, 15014,  1988,  2051,
                              27160, 17545, 21009 ],
            'n_repeats': {'motor_synch': 6, 'motor_monitor': 17, 'motor_mixed': 17},
            'n_deviant_wait': {'motor_monitor': 2, 'motor_mixed': 8},
            'timed_message': {'motor_synch': ['',0],
                              'motor_monitor': ['',0],
                              'motor_mixed': ['Stop tapping!', 6]},
            'n_deviants': 3,
            'deviant_ms': 200}

def generate_sound(env,stimulus,condition,repeat=1,deviant_wait=0,random_seed=None):
    beep = tone(stimulus['freq_Hz'][condition],
                stimulus['beep_ms'],stimulus['atten_dB'],stimulus['ramp_ms'],
                env['sample_rate_Hz'])

    intervals,deviants = generate_intervals_and_deviants(stimulus,condition,
                                                         repeat,deviant_wait,random_seed)

    sound = beep.copy()
    for interval in intervals:
        sound = np.vstack([sound, silence(interval,env['sample_rate_Hz']), beep.copy()])

    return sound,deviants
stimulus['generate_sound'] = generate_sound

def generate_intervals_and_deviants(stimulus,condition,repeat,deviant_wait,random_seed):
    rhythm_N = len(stimulus['intervals_ms'][condition])
    intervals = np.tile(stimulus['intervals_ms'][condition],repeat)
    
    if random_seed is None:
        return intervals,[]

    else:
        with RandomSeed(random_seed):
            n_deviants = np.random.randint(stimulus['n_deviants']+1)
            deviant_indices = np.random.random_integers(rhythm_N*deviant_wait,
                                                        rhythm_N*repeat-1,
                                                        size=n_deviants)
            deviant_dirs = np.random.choice([-1,1],n_deviants)

        # deviate events, possibly changing the order if the
        # difference is greater than the interval separating two events.
        events = np.cumsum(intervals)
        events[deviant_indices] += deviant_dirs*stimulus['deviant_ms']
        events = np.sort(events)
        intervals = np.ediff1d(events,to_begin=events[0])
        return intervals,events[deviant_indices]

experiment.start(env,stimulus,phases)

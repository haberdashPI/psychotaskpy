################################################################################
from itertools import repeat
from util import *
import glob
import adapters
import experiment
import phase
import oset

# setup the types of phases we want to use
import motor
import responder
import passive

phases = ['motor_synch','motor_monitor']

env = {'title': 'Motor Synchronization',
       'responder': responder.nanopad,
       'countdown_interval': 750,
       'countdown_length': 3,
       'debug': True,
       'sample_rate_Hz': 44100,
       'groups': ['Test'],
       'default_blocks': 4,
       'data_file_dir': '../data',
       'response_window': 1000,
       'program_file_dir': 'program_data'}

instructions ={'motor_synch': 'Tap along to the rhythm you hear during synchronization. '+
                    'Continue to repeat the rhythm once the sound stops. ',
               'motor_monitor': 'Tap the bottom left button whenever you '+
                    'hear a deviation from the rhythm during the monitor phase.'}

timed_images = {'motor_synch': [('initiate.png',0),
                                ('synchronize.png',4000*2),
                                ('continue.png',4000*8)],
                'motor_monitor': [('listen.png',0),
                                  ('monitor.png',4000*2)]}

stimulus = {'atten_dB': 20,
            'beep_ms': 25,
            'ramp_ms': 10,
            'instructions': instructions,
            'condition_order': ['A','B','A1k'],
            'intervals_ms': {'A':   [640, 160, 560, 960, 320, 400, 240, 720],
                             'A1k': [640, 160, 560, 960, 320, 400, 240, 720],
                             'B':   [320, 1040, 800, 160, 240, 400, 480, 560]},
            'freq_Hz' : {'A0': 250, 'A': 250, 'B': 250, 'A1k': 1000},
            'continuation_ms': 47000,
            'timed_images': dict(zip(['A','B','A1k'],repeat(timed_images))),
            'random_seeds': [ 1986, 31051,  6396, 21861, 15014,  1988,  2051,
                              27160, 17545, 21009 ],
            'n_repeats': 8,
            'n_deviant_wait': 2,
            'num_deviants': 3,
            'n_deviants': 3,
            'deviant_ms': 200}

def generate_sound(env,stimulus,condition,block):
    repeat = stimulus['n_repeats']
    random_seed = stimulus['random_seeds'][block]
    
    intervals,deviants = \
      generate_intervals_and_deviants(stimulus,condition,repeat,random_seed)

    beep = tone(stimulus['freq_Hz'][condition],
                stimulus['beep_ms'],stimulus['atten_dB'],stimulus['ramp_ms'],
                env['sample_rate_Hz'])
    sound = beep.copy()
    
    for interval in intervals:
        some_silence = silence(interval - stimulus['beep_ms'],env['sample_rate_Hz'])
        sound = np.vstack([sound, some_silence, beep.copy()])

    return sound,deviants

stimulus['generate_sound'] = generate_sound

def generate_intervals_and_deviants(stimulus,condition,repeat,random_seed):
    rhythm_N = len(stimulus['intervals_ms'][condition])
    intervals = np.tile(stimulus['intervals_ms'][condition],repeat)
    times = np.cumsum(intervals)
    
    if random_seed is None:
        return intervals,[]

    else:
        with RandomSeed(random_seed):
            deviant_indices = select_deviants(stimulus,condition,times,rhythm_N,repeat)
            deviant_dirs = np.random.choice([-1,1],len(deviant_indices))

        # create the new times, after deviation, possible reordering the events
        # if necessary
        new_times = times.copy()
        new_times[deviant_indices] += deviant_dirs*stimulus['deviant_ms']
        new_times = np.sort(new_times)
        intervals = np.ediff1d(new_times,to_begin=times[0])
        return intervals,new_times[~(new_times == times)]


def select_deviants(stimulus,condition,times,rhythm_N,repeat):
    cycles = oset.oset(range(stimulus['n_deviant_wait'],repeat))
    selected = []

    def not_too_close(i):
        if selected: 
            mindiff = min(np.abs(times[i] - times[selected]))
            return mindiff >= env['response_window']
        else: return True

    while cycles:
        if np.random.randint(2):
            c = cycles.pop()
            # TODO: do we need to remove the next cycle, I think so.
            if cycles: cycles.pop()
            
            possible_times = filter(not_too_close,range((c*rhythm_N),((c+1)*rhythm_N)))
            selected.append(np.random.choice(possible_times))
        else:
            cycles.pop()

    return selected

if __name__ == "__main__":
    experiment.start(env,stimulus,phases)

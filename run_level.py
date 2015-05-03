from itertools import repeat
from scipy.interpolate import interp1d
import pandas as pd
import scipy.stats
from util import *
import glob
import adapters
import experiment
import phase

# setup the types of phases we want to use
import twoAFC
import passive

phases = ['2AFC']

#booth_atten = {'corner': 27.6, 'left': 25.7, # calibrated on 9-15-14
#               'middle': 30.7, # calibrated on 10-14-14
#			   'right': 31.1, # calibrated on 04-15-15
#               'none': 26}
			   

# calibrated on 05-03-15
calibration_curve = \
  {'left': {'1k': [(20,98.8),(40,78.8),(45,73.8),(50,68.75),(55,63.7),
                   (60,58.6),(65,53.6),(70,48.5),(75,43.4),(80,37.7),
                   (85,30.8),(87.5,26.9),(90,25.3),(91.25,22.6),
                   (92.5,18),(93.75,13.6),(95,13)],
            '250': [(10,104),(20,93.9),(30,83.9),(40,73.8),(50,64.2),
                    (60,54.2),(70,43.7),(80,33),(82.5,30.4),(85,27.15),
                    (86.25,26.2),(86.875,25.4),(87.5,23),(88.125,22.75),
                    (88.75,22.6),(90,22),(91,21.2),(92,20.3),(93,18.6),
                    (94,17.5)],
            '500': [(10,105.7),(30,85.6),(50,65.7),(70,45.4),(80,34.6),
                    (82.5,31.75),(85,29.0),(86.25,28),(86.875,27.5),
                    (87.1875,26.7),(87.5,25.45),(90,24.05),(92.5,22.6),
                    (93,22.1),(94,21.5)],
            '2k': [(10,105.7),(30,85.3),(50,65.5),(70,45.1),(80,34.3),
                   (8.25,31.15),(85,27.5),(86.25,27.5),(86.875,25.85),
                   (87.1875,25.85),(87.34375,23.7),(87.5,23.7),(90,22.2),
                   (91.25,19.6),(92.5,15.3),(93.25,11.4),(93.5,11.5),
                   (93.75,11.4)],
            '4k': [(10,99.6),(40,69.4),(50,59.8),(70,39.4),(80,28.6),
                   (82.5,25.4),(85,22),(86.25,21.9),(87,20.4),(87.5,18.4),
                   (88.125,17.2),(89,17.15),(90,17.15),(91,15.2),(92,15.2),
                   (93,12.8),(94,11.3)],
            '8k': [(10,97.4),(50,57.8),(70,37.1),(80,26.5),(82.5,24.8),
                   (82.75,23.5),(86.25,21.1),(85,21.1),(86.25,21.1),(86.5,21.1),
                   (86.75,21.1),(86.8,21.1),(86.85,21.1),(86.86,21.1),(86.8775,18.1),
                   (86.875,18.1),(87,18.1),(87.5,18.1),
                   (88,18),(88.5,18),(89,15.9),(90,15.8),(92,15.8),(93,13.5)]},
                   
   'none': dict(zip(['250','500','1k','2k','4k','8k'],
                    repeat(zip(np.linspace(20,80,10),
                               np.linspace(100,10,10)),6)))}

dBSPL_to_dBHL = {'250': 27, '500': 13.5, '1k': 7.5, '2k': 9, '4k': 12, '8k': 15.5}

def make_calfn(freq,curve):
    atten,dBSPL = zip(*curve)
    return interp1d(atten,np.array(dBSPL) + dBSPL_to_dBHL[freq],'cubic')

calibration_fn = dict(map(lambda (freq,curve): (freq,make_calfn(freq,curve)),
                          calibration_curve[booth()].iteritems()))

env = {'title': 'Tone Detection',
       'debug': True,
       'sample_rate_Hz': 44100,
       'groups': ['level'],
       'default_blocks': 1,
       'data_file_dir': '../data',
       'num_trials': 30,
       'feedback_delay_ms': 400}

stimulus = {'beep_ms': 200,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'response_delay_ms': 500,
            'example_standard': 'No tone played',
            'example_signal': "There's a Tone!",
            'example_delta': 70,
            'instructions': 'You will be listening for a tone.',
            'sound_labels': ['Time 1','Time 2'],
            'full_question': 'Which time period had a tone?',
            'condition_order': ['250','500','1k','2k','4k','8k'],
            'conditions': {'250': 250, '500': 500, '1k': 1000,
                           '2k': 2000, '4k': 4000, '8k': 8000}}
                                                      
def generate_sound(env,stimulus,condition,delta):
    if delta != 0:
        cond = stimulus['conditions'][condition]

        beep = tone(cond,
                    stimulus['beep_ms'],
                    calibration_fn[condition](delta),
                    stimulus['ramp_ms'],
                    env['sample_rate_Hz'])

        return left(beep).copy()
    else:
        return silence(stimulus['beep_ms'],env['sample_rate_Hz']).copy()

stimulus['generate_sound'] = generate_sound

def generate_adapter(env,stimulus,condition):
    params = pd.DataFrame({'theta': np.tile(np.linspace(120,-10,130),50),
                           'sigma': np.repeat(np.linspace(0.2,100,50),130),
                           'miss': 0.08})

    params['lp'] = np.log(scipy.stats.norm.pdf(params.theta,loc=0,scale=50)) + \
        np.log(scipy.stats.norm.pdf(params.sigma, loc=0,scale=50))
    
    dBs = zip(*calibration_curve[booth()][condition])[1]
    min_dB = min(dBs) + dBSPL_to_dBHL[condition]
    max_dB = max(dBs) + dBSPL_to_dBHL[condition]
    return adapters.KTAdapter(70,np.linspace(min_dB,max_dB,100),params)

env['generate_adapter'] = generate_adapter

# only run the expeirment if this file is being called directly
# from the command line.
if __name__ == "__main__":
    experiment.start(env,stimulus,phases)

import audio
import time
import adapters
from util import *
from psychopy.visual import Window, TextStim
from psychopy.core import wait
from psychopy.gui import DlgFromDict

stimulus = {}
env = {}

rhythm = 'A'
stimulus = {'atten_dB': 10,
            'freq_Hz': 250,
            'beep_ms': 25,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'intervals': rhythm_intervals(rhythm)}

alphas = np.linspace(0,0.3,num=4)

slopes = (adapters.sig_solve_slope(p=0.95,x=delta,alpha=0.0) \
          for delta in np.linspace(0.01,0.95,num=1000))

ml_adapter = adapters.MLAdapter(0.95,sorted(slopes),alphas)

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': 'data',
       'num_trials': 30,
       'feedback_delay_ms': 500,
       'adapter': ml_adapter}

def create_window(env):
    if env['debug']: return Window([400,400])
    else: return Window(fullscr=True)

def blocked_audio(sid,group,phase,start_block,num_blocks):
    env['win'] = create_window(env)
    env['num_blocks'] = num_blocks
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['rhythm'] = rhythm
        
        TextStim(env['win'],text='Tapping Task')
        wait(3.0)
        
        dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")

        for i in range(start_block,num_blocks):
            info['block'] = i
            audio.run(env,stimulus,LineWriter(dfile,info))
    finally:
        env['win'].close()
        
setup = {'User ID': '0000', 'Group': 'test', 'Phase': 'phase',
         'Blocks': 5, 'Start Block': 0}
dialog = DlgFromDict(dictionary=setup,title='Rhythm Discrimination')
if dialog.OK:
    blocked_audio(setup['User ID'],setup['Group'],setup['Phase'],
                  setup['Start Block'],setup['Blocks'])

import motor
import time
from util import *
from psychopy.visual import Window, TextStim
from psychopy.core import wait


stimulus = {}
env = {}

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': 'data',
       'continuation_ms': 8000, #47000
       'n_synch': 2} # 6
    
rhythm = 'A'
stimulus{'atten_dB': 10,
         'freq_Hz': 250,
         'beep_ms': 25,
         'ramp_ms': 5,
         'intervals': rhythm_intervals(rhythm)}

def create_window(env):
    if env.debug: return Window([400,400])
    else: return Window(fullscr=True)

def blocked_motor(sid,group,phase,start_block,num_blocks):
    env.win = create_window(env)
    env.num_blocks = num_blocks
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['rhythm'] = rhythm
        
        TextStim(env.win,text='Tapping Task')
        wait(3.0)
        
        dfile = unique_file(env.data_file_dir + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")
        
        motor.run(env,stimulus,LineWriter(dfile,info))
    finally:
        env.win.close()
        

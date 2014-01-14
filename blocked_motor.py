import motor
import time
from util import *
from psychopy.visual import Window, TextStim
from psychopy.core import wait


stimulus = Info()
env = Info()

env.debug = True
env.sample_rate_Hz = 44100
env.data_file_dir = 'data'

env.continuation_ms = 8000 #47000
env.n_synch = 2 # 6

stimulus.atten_dB = 10
stimulus.freq_Hz = 250
stimulus.beep_ms = 25
stimulus.ramp_ms = 5
rhythm = 'A'
stimulus.intervals = rhythm_intervals('A')

def create_window(env):
    if env.debug: return Window([400,400])
    else: return Window(size=(1024,748),fullscr=True)

def blocked_motor(sid,group,phase,start_block,num_blocks):
    env.win = create_window(env)
    env.num_blocks = num_blocks
    try: 
        info = Info()
        info.sid = sid
        info.group = group
        info.phase = phase
        info.rhythm = rhythm
        
        TextStim(env.win,text='Tapping Task')
        wait(3.0)
        
        dfile = unique_file(env.data_file_dir + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")
        
        motor.run(env,stimulus,LineWriter(dfile,info))
    finally:
        env.win.close()

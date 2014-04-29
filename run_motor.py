import motor
import time
from util import *
from psychopy.visual import Window, TextStim
from psychopy.core import wait
from psychopy.gui import DlgFromDict

stimulus = {}
env = {}
run = True

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': 'data',
       'continuation_ms': 47000, #47000,
       'n_synch': 6} # 6
    
rhythm = 'A'
stimulus = {'atten_dB': 20,
         'freq_Hz': 250,
         'beep_ms': 25,
         'ramp_ms': 5,
         'intervals': rhythm_intervals(rhythm)}

def create_window(env):
    if env['debug']:
        win = Window([400,400])
        win.setMouseVisible(False)
        return win
    else:
        win = Window(fullscr=True)
        win.setMouseVisible(False)
        return win

def blocked_motor(sid,group,phase,start_block,num_blocks):
    env['win'] = create_window(env)
    env['num_blocks'] = num_blocks
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['rhythm'] = rhythm
        info_order = ['sid','group','phase','rhythm']
        
        TextStim(env['win'],text='Tapping Task')
        wait(3.0)
        
        dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")
        
        motor.run(env,stimulus,LineWriter(dfile,info,info_order))
    finally:
        env['win'].close()
        
if run:
    setup = {'User ID': '0000', 'Group': 'pilot', 'Phase': 'test',
            'Blocks': 1, 'Start Block': 0}
    dialog = DlgFromDict(dictionary=setup,title='Rhythm Discrimination',
                        order=['User ID','Group','Phase','Blocks','Start Block'])
    if dialog.OK:
        blocked_motor(setup['User ID'],setup['Group'],setup['Phase'],
                      setup['Start Block'],setup['Blocks'])

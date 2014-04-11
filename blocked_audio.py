import audio
import time
import adapters
from util import *
from psychopy.visual import Window, TextStim
from psychopy.core import wait
from psychopy.gui import DlgFromDict

stimulus = {}
env = {}
run = True

rhythm = 'A'
stimulus = {'atten_dB': 20,
            'freq_Hz': 250,
            'beep_ms': 25,
            'ramp_ms': 5,
            'SOA_ms': 900,
            'intervals': rhythm_intervals(rhythm)}

env = {'debug': False,
       'sample_rate_Hz': 44100,
       'data_file_dir': 'data',
       'num_trials': 50,
       'feedback_delay_ms': 500}    

def adapter():
    alphas = np.linspace(0,0.3,num=4)
    midpoints = np.linspace(0.001,0.99,num=500)
    slope_sigma = adapters.sig_solve_slope(p=0.95,delta=0.02,alpha=0.0,
                                           midpoint=0.01)
    slopes = np.linspace(0.01,2*slope_sigma,num=25)

    return adapters.MLAdapter(start_delta=0.95,slopes=sorted(slopes),
                              alphas=alphas,midpoints=midpoints,
                              slope_sigma=slope_sigma)

def create_window(env):
    if env['debug']:
        win = Window([400,400])
        win.setMouseVisible(False)
        return win
    else:
        win = Window(fullscr=True)
        win.setMouseVisible(False)
        return win

def blocked_audio(sid,group,phase,start_block,num_blocks):
    env['win'] = create_window(env)
    env['num_blocks'] = num_blocks
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['rhythm'] = rhythm
        info_order = ['sid','group','phase','rhythm','block']
        
        TextStim(env['win'],text='Tapping Task')
        wait(3.0)
        
        for i in range(start_block,num_blocks):
            env['adapter'] = adapter()
            info['block'] = i
            dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                            time.strftime("%Y_%m_%d_") + phase + "_%02d.dat")
            
            audio.run(env,stimulus,LineWriter(dfile,info,info_order))
    finally:
        env['win'].close()



if run:
    setup = {'User ID': '0000', 'Group': 'pilot', 'Phase': 'test',
            'Blocks': 5, 'Start Block': 0}
    dialog = DlgFromDict(dictionary=setup,title='Rhythm Discrimination',
                        order=['User ID','Group','Phase','Blocks','Start Block'])
    if dialog.OK:
        blocked_audio(setup['User ID'],setup['Group'],setup['Phase'],
                      setup['Start Block'],setup['Blocks'])

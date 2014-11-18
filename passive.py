import expyriment as ex

from util import tone, Info,nth_file
from phase import phase

import random
import numpy as np
import datetime
import pandas as pd

@phase
def passive_static(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    run(env,stimulus,write_line)

@phase
def passive_today(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from today
    tfile = nth_file(block,env['data_file_dir'] + '/' + sid + '_' +
                        time.strftime("%Y_%m_%d_") + 'train' +
                        "_%02d.dat",wrap_around=True)

    print "Running passively from file: " + tfile
    run_track(env,stimulus,pd.read_csv(tfile),write_line)

@phase
def passive_first(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

        print env['data_file_dir'] + '/' + sid + '_*train*.dat'
        tfiles = glob.glob(env['data_file_dir'] + '/' + sid + '_*train*.dat')
        print tfiles

        # make sure there are actually the right number of blocks
        assert len(tfiles) == env['num_blocks']
    
    tfiles = glob.glob(env['data_file_dir'] + '/' + sid + '_*train*.dat')
    print "Running passively from track in file: " + tfiles[block]
    run_track(env,stimulus,pd.read_csv(tfiles[block]),write_line)

def run(env,stimulus,write_line):
    env['exp'].screen.clear()
    env['exp'].screen.update()    

    stim_1 = stimulus['generate'](0)
    stim_2 = stimulus['generate'](0)

    env['exp'].clock.wait(1000)
    
    for trial in range(env['num_trials']):
        # provide an oportunity to exit/pause the program
        env['exp'].keyboard.check()
        
        signal_interval = random.randint(0,1)

        stim_1.play()
        env['exp'].clock.wait(stimulus['SOA_ms'])
        stim_2.play()

        delay = stimulus['response_delay_ms'] + stimulus['passive_delay_ms']
        env['exp'].clock.wait(delay)
                
        write_line({'timestamp': datetime.datetime.now()},['timestamp'])

        env['exp'].clock.wait(env['feedback_delay_ms'])
        
def run_track(env,stimulus,track,write_line):
    env['exp'].screen.clear()
    env['exp'].screen.update()    
    
    env['exp'].clock.wait(1000)

    delays_ms = pd.to_datetime(track.timestamp).diff()
    # HACK!! (could be broken by an update to numpy)
    delays_ms = delays_ms.apply(lambda x: x.astype('float64') / 1e6)
    delays_ms[0] = delays_ms.median()

    for track_index,track_row in track.iterrows():
        # provide an oportunity to exit/pause the program
        env['exp'].keyboard.check()

        signal_interval = track_row['correct_response']
        if signal_interval == 0:
            stim_1 = stimulus['generate'](track_row['delta'])
            stim_2 = stimulus['generate'](0)
            
        else:
            stim_1 = stimulus['generate'](0)
            stim_2 = stimulus['generate'](track_row['delta'])
        
        stim_1.play()
        env['exp'].clock.wait(stimulus['SOA_ms'])
        
        stim_2.play()

        delay = max((stimulus['response_delay_ms']),
                    delays_ms[track_index] - stimulus['SOA_ms'] - \
                    env['feedback_delay_ms'])

        env['exp'].clock.wait(delay)
                
        line_info = {'delta': track_row['delta'],
                     'signal_interval': signal_interval,
                     'timestamp': datetime.datetime.now()}

        order = ['delta','signal_interval','timestamp']
        
        write_line(line_info,order)

        env['exp'].clock.wait(env['feedback_delay_ms'])

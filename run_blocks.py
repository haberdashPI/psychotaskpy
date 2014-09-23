from util import *
import twoAFC
import passive
import time
from psychopy.visual import Window, TextStim
from psychopy.core import wait
from psychopy.event import waitKeys
import pandas as pd


def create_window(env):
    if env['debug']:
        win = Window([400,400])
        win.setMouseVisible(False)
        return win
    else:
        win = Window(fullscr=True)
        win.setMouseVisible(False)
        return win

def blocked_run(sid,group,phase,condition,start_block,num_blocks,stimulus,env):
    env['win'] = create_window(env)
    env['num_blocks'] = num_blocks
    stimulus['generate'] = stimulus['generate_tones_fn'](stimulus,env,condition)
    try: 
        info = {}
        info['sid'] = sid
        info['group'] = group
        info['phase'] = phase
        info['stimulus'] = condition
        info_order = ['sid','group','phase','block','stimulus']

        wait(3.0)

        if phase == 'train':

            twoAFC.examples(env,stimulus,condition)

            for i in range(start_block,num_blocks):
                info['block'] = i
                dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                                time.strftime("%Y_%m_%d_") + phase +
                                "_%02d.dat")

                env['adapter'] = env['generate_adapter'](stimulus,condition)

                twoAFC.run(env,stimulus,LineWriter(dfile,info,info_order))

        # passively present the same sound over and over
        elif phase == 'passive_static':
            start_message = \
              TextStim(env['win'],text='Press any key when you are ready.')

            start_message.draw()
            env['win'].flip()
            waitKeys()

            for i in range(start_block,num_blocks):
                info['block'] = i
                dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                                time.strftime("%Y_%m_%d_") + phase +
                                "_%02d.dat")

                passive.run(env,stimulus,LineWriter(dfile,info,info_order))

        # passively present tracks from the same day
        elif phase == 'passive_today':
            start_message = \
              TextStim(env['win'],text='Press any key when you are ready.')

            start_message.draw()
            env['win'].flip()
            waitKeys()

            for i in range(start_block,num_blocks):
                info['block'] = i
                dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                                time.strftime("%Y_%m_%d_") + phase +
                                "_%02d.dat")

                tfile = nth_file(i,env['data_file_dir'] + '/' + sid + '_' +
                                  time.strftime("%Y_%m_%d_") + 'train' +
                                  "_%02d.dat")

                track = pd.read_csv(tfile)

                print "Running passively from track in file: " + tfile

                passive.run_track(env,stimulus,track,
                                  LineWriter(dfile,info,info_order))

        # passively present tracks from the first day
        elif phase == 'passive_first':
            start_message = \
              TextStim(env['win'],text='Press any key when you are ready.')

            start_message.draw()
            env['win'].flip()
            waitKeys()

            print env['data_file_dir'] + '/' + sid + '_*train*.dat'
            tfiles = glob.glob(env['data_file_dir'] + '/' + sid + '_*train*.dat')
            print tfiles

            # make sure there are actually the right number of blocks
            assert len(tfiles) == env['num_blocks']

            for i in range(start_block,num_blocks):
                info['block'] = i
                dfile = unique_file(env['data_file_dir'] + '/' + sid + '_' +
                                time.strftime("%Y_%m_%d_") + phase +
                                "_%02d.dat")

                track = pd.read_csv(tfiles[i])
                
                print "Running passively from track in file: " + tfiles[i]

                passive.run_track(env,stimulus,track,
                                  LineWriter(dfile,info,info_order))

    finally:
        env['win'].close()


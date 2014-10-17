import expyriment as ex
from util import *
import pygame.mixer as mix

import twoAFC
import passive
import time
import pandas as pd
from functools32 import lru_cache

def blocked_run(env,stimulus,sid,group,phase,condition,start_block,num_blocks):
    env['num_blocks'] = num_blocks

    def as_sound(floats):
        return mix.Sound(np.asarray(floats*(2**15),'int16'))

    @lru_cache(maxsize=None)
    def generate(d):
        return as_sound(stimulus['generate_tones'](env,stimulus,condition,d))
    stimulus['generate'] = generate
    
    info = {}
    info['sid'] = sid
    info['group'] = group
    info['phase'] = phase
    info['stimulus'] = condition
    info_order = ['sid','group','phase','block','stimulus']

    if phase == 'train':

        twoAFC.examples(env,stimulus,condition)

        for i in range(start_block,num_blocks):
            info['block'] = i
            dfile = unique_file(env['data_file_dir'] + '/' + str(sid) + '_' +
                            time.strftime("%Y_%m_%d_") + str(phase) +
                            "_%02d.dat")

            env['adapter'] = env['generate_adapter'](env,stimulus,condition)

            twoAFC.run(env,stimulus,LineWriter(dfile,info,info_order))

    # passively present the same sound over and over
    elif phase == 'passive_static':
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

        for i in range(start_block,num_blocks):
            info['block'] = i
            dfile = unique_file(env['data_file_dir'] + '/' + str(sid) + '_' +
                            time.strftime("%Y_%m_%d_") + str(phase) +
                            "_%02d.dat")

            passive.run(env,stimulus,LineWriter(dfile,info,info_order))

    # passively present tracks from the same day
    elif phase == 'passive_today':
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

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
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

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
    


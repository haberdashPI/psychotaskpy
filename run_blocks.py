import expyriment as ex
from util import *
import pygame.mixer as mix

from phase import run_phase
import time
import pandas as pd
from functools32 import lru_cache

def blocked_run(env,stimulus,sid,group,phase,condition,start_block,num_blocks):
    env['num_blocks'] = num_blocks

    def as_sound(floats):
        return mix.Sound(np.asarray(floats*(2**15),'int16'))

    @lru_cache(maxsize=None)
    def generate(*params):
        return as_sound(stimulus['generate_tones'](env,stimulus,condition,*params))
    stimulus['generate'] = generate
    
    info = {}
    info['sid'] = sid
    info['group'] = group
    info['phase'] = phase
    info['stimulus'] = condition
    info_order = ['sid','group','phase','block','stimulus']

    for block in range(start_block,num_blocks):
        info['block'] = block
        dfile = unique_file(env['data_file_dir'] + '/' + str(sid) + '_' +
                            time.strftime("%Y_%m_%d_") + str(phase) +
                            "_%02d.dat")
        if env.has_key('generate_adapter'):
            env['adapter'] = env['generate_adapter'](env,stimulus,condition)
        run_phase(phase,env,stimulus,condition,block,block == start_block,
                  LineWriter(dfile,info,info_order))


from util import *
from settings import prepare, summarize

import pygame.mixer as mix
import time
from phase import run_phase
from functools32 import lru_cache


def blocked_run(env):
    def as_sound(floats):
        return mix.Sound(np.asarray(floats*(2**15),'int16'))

    if env['cache_stimuli']:
        @lru_cache(maxsize=None)
        def generate(*params):
            result = env['generate_sound'](env,*params)
            # generate_sound can return additional values as part of the stimulus
            # generation (for instance to provide ground truth information relevant
            # to that stimulu).
            if isinstance(result,tuple):
                return (as_sound(result[0]),) + result[1:]
            else:
                return as_sound(result)
    else:
        def generate(*params):
            result = env['generate_sound'](env,*params)
            # generate_sound can return additional values as part of the stimulus
            # generation (for instance to provide ground truth information relevant
            # to that stimulu).
            if isinstance(result,tuple):
                return (as_sound(result[0]),) + result[1:]
            else:
                return as_sound(result)
    env['sound'] = generate

    for block in range(env['start_block'],env['num_blocks']):
        env['block'] = block
        dfile = unique_file(env['data_file_dir'] + '/' + ("%04d" % env['sid']) + '_' +
                            time.strftime("%Y_%m_%d_") + str(env['phase']) +
                            "_%02d.dat")
        print "Writing data to: ",dfile
        env['adapter'] = env['generate_adapter'](env)
        info_order,info = summarize(env,env['write_to_file'])
        run_phase(env['phase'],env,env['block'] == env['start_block'],
                  LineWriter(dfile,info,info_order))

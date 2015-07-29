import copy
import expyriment as ex
import run_blocks
import pygame
import util
from phase import get_phase_defaults
from settings import prepare, UserNumber, request_user_input, Plural


def start(env):

    default = {'start_block': UserNumber('Start Block', 0),
               'booth': util.booth(),
               'conditions': Plural('condition'),
               'debug': False,
               'cache_stimuli': True,
               'write_to_file': ['sid','group','phase','condition','booth',
                                 'block']}
    global_env = prepare(env,default)

    ex.control.defaults.pause_key = pygame.K_F12

    exp = ex.design.Experiment(name=env['title'],
                               foreground_colour=[255,255,255],
                               background_colour=[128,128,128],
                               text_size=40)

    exp.set_log_level(0)

    if global_env['debug']:
        ex.control.set_develop_mode(True)

    ex.control.initialize(exp)

    global_env = request_user_input(global_env)

    ex.control.start(exp,skip_ready_screen=True,subject_id=global_env['sid'])
    try:
        for cond_env in global_env['conditions']:
            defaults = copy.deepcopy(global_env)
            del defaults['conditions']
            defaults['exp'] = exp
            defaults['condition'] = cond_env['name']

            cond_env = prepare(cond_env,defaults)
            cond_env = prepare(cond_env,get_phase_defaults(cond_env),True)
            del cond_env['name']

            run_blocks.blocked_run(cond_env)

        ex.stimuli.TextBox("All Done! Let the experimenter know you are" +
                           " finished!",util.MESSAGE_DIMS).present()
        exp.keyboard.wait()

    finally:
        ex.control.end()

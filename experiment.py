import expyriment as ex
import run_blocks
import pygame
import util
from settings import prepare, UserNumber, request_user_input, Vars


def start(base_env):

    default = {'start_block': UserNumber('Start Block', 0),
               'booth': util.booth(),
               'debug': False}
    env = prepare(base_env,default)

    ex.control.defaults.pause_key = pygame.K_F12

    exp = ex.design.Experiment(name=env['title'],
                               foreground_colour=[255,255,255],
                               background_colour=[128,128,128],
                               text_size=40)

    exp.set_log_level(0)

    env['exp'] = exp
    if env['debug']:
        ex.control.set_develop_mode(True)

    ex.control.initialize(exp)

    env = request_user_input(env)
    env = prepare(env,{'stimuli': [env['stimulus']]})

    ex.control.start(exp,skip_ready_screen=True,subject_id=env['sid'])
    try:
        for stimulus in env['stimuli']:
            env['stimulus'] = stimulus
            run_blocks.blocked_run(env)

        ex.stimuli.TextBox("All Done!. Let the experimenter know you are finished!",
                           util.MESSAGE_DIMS).present()

    finally:
        ex.control.end()

    print env

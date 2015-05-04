import expyriment as ex
import run_blocks
import pygame
import phase
import util

def collect_fields(setup,order):
    for field in order:
        if isinstance(setup[field],list):
            tm = ex.io.TextMenu(field,setup[field],400)
            setup[field] = setup[field][tm.get(0)]
        else:
            ti = ex.io.TextInput(field)
            setup[field] = int(ti.get(str(setup[field])))

    return setup

def start(env,stimulus,phases,conditions=None):
    setup = {'Subject ID': 0,
         'Group': env['groups'], 'Phase': phases,
         'Condition': stimulus['condition_order'],
         'Blocks': env['default_blocks'],
         'Start Block': 0}
         
    if conditions is None:
        order = ['Subject ID','Group','Phase','Condition','Blocks','Start Block']
    else:
        order = ['Subject ID','Group','Phase','Blocks','Start Block']

    if env.has_key('fields'):
        setup.update(env['fields'])
        order += env['field_order']

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

    setup = collect_fields(setup,order)

    ex.control.start(exp,skip_ready_screen = True,subject_id=setup['Subject ID'])
    try:
        if conditions is None:
            run_blocks.blocked_run(env,stimulus,
                exp.subject,setup['Group'],setup['Phase'],
                setup['Condition'],setup['Start Block'],setup['Blocks'])
        else:
            for condition in conditions:
                run_blocks.blocked_run(env,stimulus,
                    exp.subject,setup['Group'],setup['Phase'],
                    condition,setup['Start Block'],setup['Blocks'])
                    
        ex.stimuli.TextBox("All Done!. Let the experimenter know you are finished!",
                            util.MESSAGE_DIMS).present()

    finally:
        ex.control.end()

    print setup


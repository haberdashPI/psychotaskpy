# the possible ways to run blocks of training
from psychopy.gui import DlgFromDict

phases = ['train','passive_static','passive_today','passive_first']

def start(env,stimulus):
    setup = {'User ID': '0000','Group': env['groups'], 'Phase': phases,
         'Condition': stimulus['condition_order'],
         'Blocks': env['default_blocks'],
         'Start Block': 0}
    order = ['User ID','Group','Phase','Condition','Blocks','Start Block']

    if env.has_key('fields'):
        setup.update(env['fields'])
        order += env['field_order']

    dialog = DlgFromDict(dictionary=setup,title=env['title'],
                         order=order)

    if env.has_key('fields'):
        for field in env['fields'].keys():
            env['fields'][field] = setup[field]

    if dialog.OK:
        import run_blocks
        
        run_blocks.blocked_run(env,stimulus,
                        setup['User ID'],setup['Group'],setup['Phase'],
                        setup['Condition'],setup['Start Block'],setup['Blocks'])

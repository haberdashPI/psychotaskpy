import expyriment as ex
from util import tone, Info
import util
import numpy as np

import datetime
from phase import phase

@phase('motor_synch')
def run_synch(env,stimulus,condition,block,is_start,write_line):
    setup(env,stimulus,'motor_synch',condition,block,is_start,write_line)
@phase('motor_monitor')
def run_synch(env,stimulus,condition,block,is_start,write_line):
    setup(env,stimulus,'motor_monitor',condition,block,is_start,write_line)

def setup(env,stimulus,phase,condition,block,is_start,write_line):
    with env['responder'](env['exp']) as responder:
        if is_start:
            ex.stimuli.TextBox(stimulus['instructions'][phase],
                               util.MESSAGE_DIMS).present()
            env['exp'].keyboard.wait()

        # load the intervals 
        ex.stimuli.TextLine('Loading...').present()
        rhythm,deviants = stimulus['generate'](block,phase)

        __run(env,stimulus,phase,condition,responder,rhythm,deviants,
              block,write_line)

def __record_responses(env,timestamp,write_line,events):
    for time,pressure in events:
            # record button press
            write_line({'time': time,
                        'pressure': pressure,
                        'type': 'listener',
                        'block_timestamp': timestamp},
                        ['time','pressure','type','block_timestamp'])

def __run(env,stimulus,phase,condition,responder,rhythm,deviants,block,
          write_line):
    env['exp'].screen.clear()

    # figure how long the trial should run
    if phase == 'motor_monitor': continuation_ms = 0
    else: continuation_ms = stimulus['continuation_ms']

    listen_time_ms = rhythm.get_length()*1000 + \
      env['countdown_interval']*env['countdown_length'] + \
      continuation_ms

    # setup start prompt
    start_message = ex.stimuli.TextBox(env['responder'].message,
                                       util.MESSAGE_DIMS)

    # setup text used in countdown to start
    # countdown = [ex.stimuli.TextLine(str(i)) for i in
    #              range(env['countdown_length'],0,-1)]
    # go_text = ex.stimuli.TextLine('Go!')
    # for c in countdown: c.preload()
    # go_text.preload()

    # setup stage indicators
    timed_image_stims = []
    for i,stim in enumerate(stimulus['timed_images'][condition][phase]):
        image = ex.stimuli.Picture(env['program_file_dir'] + '/' + stim[0])
        image.preload()
        timed_image_stims.append((image,stim[1]))

    timed_image_stims.sort(key=lambda x: x[1])
        
    # prompt the user
    env['exp'].screen.clear()
    start_message.present()

    # note the starting time
    timestamp = datetime.datetime.now()
    
    # give a countdown
    #for c in countdown:
    #    c.present()
    #    env['exp'].clock.wait(env['countdown_interval'],
    #                          env['exp'].keyboard.check)

    # clear any premptive responses
    responder.collect_messages()

    # collect all user responses
    callback = lambda es: __record_responses(env,timestamp,write_line,es)
    with responder.callback(callback):
        # start playing the sound
        rhythm.play()

        # note when the trial started
        start_time_ms = env['exp'].clock.time
    
        # tell the user they can start
        #go_text.present()

        # keep the go_text (signalling that the sound is playing) up for a while
        #env['exp'].clock.wait(500,env['exp'].keyboard.check)
        #env['exp'].screen.clear()
        #env['exp'].screen.update()

        # present timed images
        for image,time in timed_image_stims:
            wait_time = max(0,time - (env['exp'].clock.time - start_time_ms))
            env['exp'].clock.wait(wait_time,
                                  lambda: env['exp'].keyboard.check())
            image.present()

        # wait until the experiment is over
        wait_time = max(0,listen_time_ms - (env['exp'].clock.time - start_time_ms))
        env['exp'].clock.wait(wait_time,
                              lambda: env['exp'].keyboard.check())
        
    ###############
    # save any deviant tones to the data file
    for time in deviants:
        if dir > 0:
            write_line({'time': time,'pressure': 127, 'type': 'ground_truth',
                        'block_timestamp': timestamp},
                        ['time','pressure','type','block_timestamp'])

    # make sure there is at least one line in the file.
    write_line({'time': 0, 'pressure': 0, 'type': 'empty',
                'block_timestamp': timestamp},
                ['time','pressure','type','block_timestamp'])


    ex.stimuli.TextBox("All done! Please, let the expeirmenter"
                       " know you are finished.",util.MESSAGE_DIMS).present()
    env['exp'].keyboard.clear()
    env['exp'].keyboard.wait()

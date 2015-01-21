import expyriment as ex
from util import tone, Info
import util
import numpy as np
import pygame
import datetime
import rtmidi_python as rtmidi
from phase import phase

KEY_UP_CODE = 128
KEY_DOWN_CODE = 144
KEYBOARD_TRIGGER = pygame.locals.K_SPACE
NANO_TRIGGER = 36 #(far left, bottom button)

@phase('motor_synch')
def run_blocks(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextBox(stimulus['instructions'],util.MESSAGE_DIMS).present()
        env['exp'].keyboard.wait()

        ex.stimuli.TextLine('Loading...').present()
        # pregenerate stimuli (results will be cached for future use)
        stimulus['generate'](stimulus['n_synch'])
        env['exp'].screen.clear()

    run(env,stimulus,block,write_line)

@phase('motor_monitor')
def run_monitor(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextBox(stimulus['monitor_instructions'],util.MESSAGE_DIMS).present()
        env['exp'].keyboard.wait()

        # stimuli must be generated for each block

    monitor(env,stimulus,block,write_line)
        

# KeyboardResponder is used for debugging purposes when the nanopad is
# unavailable. It will not provide reliable timing results.
class KeyboardResponder:
    def __init__(self,exp,key = KEYBOARD_TRIGGER):
        self.key = key
        self.exp = exp
    def __enter__(self):
        self.exp.keyboard.clear()
        waiter = ex.misc.Clock()
        key,_ = self.exp.keyboard.wait()
        while key is not self.key:
            key,_ = self.exp.keyboard.wait()
            waiter.wait(10)

        return ResponseCollector(self)

    def _translate_key(self,key):
        return [[KEY_DOWN_CODE,key,0],0.5]

    def collect_messages(self):
        keys = []
        key = self.exp.keyboard.check(self.key)
        while key is not None:
            keys.append(key)
            key = self.exp.keyboard.check(self.key)

        return map(self._translate_key,keys)

    def __exit__(self,type,value,traceback):
        pass

class NanopadResponder:
    def __init__(self,key = NANO_TRIGGER):
        self.dev = rtmidi.MidiIn(queue_size_limit=2**12)
        self.key = key
        
    def __enter__(self):
        self.dev.open_port(0)
        #self.messages = Queue.Queue(4096)
        #self.dev.set_callback(lambda m,_: self._save_message(m))

        waiter = ex.misc.Clock()
        message = self.dev.get_message()
        while message[0] is None or message[0][1] != self.key:
            message = self.dev.get_message()
            waiter.wait(10)

        return ResponseCollector(self)

    #def _save_message(self,message):
    #    if self.listening and self.key == message[0][1]: self.messages.put(message)

    def collect_messages(self):
        # collect all queued events
        # messages = []
        # try:
        #     while True:
        #         events.append(self.responder.messages.get_nowait())
        # except Queue.Empty:
        #     pass

        # return messages
        messages = []
        message = self.dev.get_message()
        while message[0] is not None:
            messages.append(message)
            message = self.dev.get_message()

        return messages

    def __exit__(self,type,value,traceback):
        self.dev.close_port()

class ResponseCollector:
    def __init__(self,responder):
        self.responder = responder
        self.last_collected = 0
        self.last_event = 0
        self.clock = ex.misc.Clock()
        self.clock.reset_stopwatch()
                
    def collect_events(self,until_ms=0):
        # wait some time
        self.last_collected += until_ms
        time_passed = self.clock.stopwatch_time
        if self.last_collected > time_passed:
            self.clock.wait(self.last_collected - time_passed)

        messages = self.responder.collect_messages()
        # oragnize all messages 
        if messages:
            times = np.cumsum(map(lambda m: m[1],messages))*1000.0
            codes = np.array(map(lambda m: m[0][0],messages))
            strengths = np.array(map(lambda m: m[0][2],messages))

            event_offset = self.last_event
            self.last_event = times[len(times)-1] + event_offset

            # filter out anything but keydown messages 
            times = times[(codes == KEY_DOWN_CODE)] + event_offset
            strengths = strengths[(codes == KEY_DOWN_CODE)]

            return zip(times,strengths)
        else:
            return []

def run(env,stimulus,block,write_line):
    env['exp'].screen.clear()

    if env['use_response_pad']:
        start_message = \
            ex.stimuli.TextBox('Press bottom left button to begin.',util.MESSAGE_DIMS)                                       
    else:
        start_message = \
          ex.stimuli.TextBox('Press spacebar to begin.',util.MESSAGE_DIMS)
          
    countdown = [ex.stimuli.TextLine(str(i)) for i in
                 range(env['countdown_length'],0,-1)]
    go_text = ex.stimuli.TextLine('Go!')
    for c in countdown: c.preload()
    go_text.preload()

    env['exp'].screen.clear()
    rhythm = stimulus['generate'](stimulus['n_synch'])
    
    if env['use_response_pad']:
        responder = NanopadResponder()
    else:
        responder = KeyboardResponder(env['exp'])

    start_message.present()
    with responder as r:
        # note the time
        timestamp = datetime.datetime.now()

        # give a countdown
        for c in countdown:
            c.present()
            env['exp'].clock.wait(env['countdown_interval'])
        go_text.present()

        # start playing the sound
        listen_time = rhythm.get_length()*1000 + \
          env['countdown_interval']*env['countdown_length'] +\
          stimulus['continuation_ms']
        rhythm.play()

        # keep the go_text up for a while
        env['exp'].clock.wait(500)
        env['exp'].screen.clear()
        env['exp'].screen.update()

        # record all user taps to a file
        for i in range(int(np.ceil(listen_time / 500.0))):
            for time,pressure in r.collect_events(500):
                write_line({'time': time - env['countdown_interval']*env['countdown_length'],
                            'pressure': pressure,
                            'block_timestamp': timestamp},
                            ['time','pressure','block_timestamp'])
    
def monitor(env,stimulus,block,write_line):
    # load the intervals 
    ex.stimuli.TextLine('Loading...').present()
    rhythm,deviants = \
        stimulus['generate'](stimulus['n_monitor'],stimulus['random_seeds'][block])

    env['exp'].screen.clear()

    # provide start prompt
    if env['use_response_pad']:
        start_message = \
            ex.stimuli.TextBox('Press bottom left button to begin.',util.MESSAGE_DIMS)                                       
    else:
        start_message = \
          ex.stimuli.TextBox('Press spacebar to begin.',util.MESSAGE_DIMS)

    # countdown to start
    countdown = [ex.stimuli.TextLine(str(i)) for i in
                 range(env['countdown_length'],0,-1)]
    go_text = ex.stimuli.TextLine('Go!')
    for c in countdown: c.preload()
    go_text.preload()

    env['exp'].screen.clear()

    ###############
    # record user specified deviants
    if env['use_response_pad']:
        responder = NanopadResponder()
    else:
        responder = KeyboardResponder(env['exp'])

    start_message.present()
    with responder as r:
        # note the time
        timestamp = datetime.datetime.now()

        # give a countdown
        for c in countdown:
            c.present()
            env['exp'].clock.wait(env['countdown_interval'])
        go_text.present()

        # start playing the sound
        rhythm.play()
        listen_time = rhythm.get_length()*1000 + \
          env['countdown_interval']*env['countdown_length']

        # keep the go_text up for a while
        env['exp'].clock.wait(500)
        env['exp'].screen.clear()
        env['exp'].screen.update()

        # record all user taps to a file
        for i in range(int(np.ceil(listen_time / 500.0))):
            for time,pressure in r.collect_events(500):

                # provide an oportunity to exit/pause the program
                env['exp'].keyboard.check()

                # record button press
                write_line({'time': time - env['countdown_interval']*env['countdown_length'],
                            'pressure': pressure,
                            'type': 'listener',
                            'block_timestamp': timestamp},
                            ['time','pressure','type','block_timestamp'])
        
    ###############
    # save all of the actual deviants to the data file
    for time in deviants:
        if dir > 0:
            write_line({'time': time,'pressure': 127, 'type': 'ground_truth',
                        'block_timestamp': timestamp},
                        ['time','pressure','type','block_timestamp'])

    # if there are no deviants its possible there will be no data file,
    # write a single line indicating that there were deviants by using a negative
    # time value
    if len(deviants) == 0:
        write_line({'time': -1, 'pressure': 0, 'type': 'ground_truth',
                    'block_timestamp': timestamp},
                    ['time','pressure','type','block_timestamp'])

    

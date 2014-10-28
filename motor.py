import expyriment
from util import tone, Info
import numpy as np
import Queue
import pygame
from phase import phase

use_response_pad = False

KEY_UP_CODE = 128
KEY_DOWN_CODE = 144
KEYBOARD_TRIGGER = pygame.locals.K_SPACE
NANO_TRIGGER = 36 #(far left, bottom button)

@phase('motor_synch')
def run_blocks(env,stimulus,condition,block,is_start,write_line):
    if is_start:
        ex.stimuli.TextBox(stimulus['instructions']).present()
        env['exp'].keyobard.wait()
    run(env,stimulus,write_line)

# keyboard responder (used for debugging purposes)
class KeyboardResponder:
    def __init__(self,exp,key = KEYBOARD_TRIGGER):
        self.key = key
        self.exp = exp
    def __enter__(self):
        self.exp.keyboard.clear()
        key = self.exp.keyboard.wait()
        while key is self.key:
            key = self.exp.keyboard.wait()

        return ResponseCollector(self)
    def collect_messages(self):
        keys = []
        key = self.exp.keyboard.check(self.key)
        while key is not None:
            keys.append(key)
            key = self.exp.keyboard.check(self.key)

        return keys
    def __exit__(self,type,value,traceback):
        pass

# midi drum pad responder
# TODO: should I just use the built in get_message? (yes
# I think that would be clearer)
class NanopadResponder:
    def __init__(self,key = NANO_TRIGGER):
        self.dev = rtmidi.MidiIn(queue_size_limit=2**12)
        self.key = key
        
    def __enter__(self):
        self.dev.open_port(0)
        #self.messages = Queue.Queue(4096)
        #self.dev.set_callback(lambda m,_: self._save_message(m))

        message = self.dev.get_message()
        while message is None or message == self.key:
            message = self.dev.get_message()

        return ResponseCollector(self)

    #def _save_message(self,message):
    #    if self.listening and self.key == message[0][1]: self.messages.put(message)

    def collect_messages():
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
        while message is not None:
            messaged.append(message)
            message = self.dev.get_message()

        return messages

    def __exit__(self,type,value,traceback):
        self.dev.close_port()
        del self.messages

class ResponseCollector:
    def __init__(self,responder):
        self.responder = responder
        self.last_collected = 0
        self.last_event = 0
        self.clock = expyriment.misc.Clock()
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
            strengths = np.array(map(lambda m: m[0][1],messages))

            event_offset = self.last_event
            self.last_event = times[len(times)-1] + event_offset

            # filter out anything but keydown messages 
            times = times[(codes == KEY_DOWN_CODE)] + event_offset
            strengths = strengths[(codes == KEY_DOWN_CODE)]

            return times,strengths
        else:
            return [],[]

def collect_events(time,cycles):
    with NanoPadResponder() as r:
        for index in range(cycles):
            print "--------------------"
            times,strengths = r.collect_events(time)
            print index
            print times

def run(env,stimulus,write_line):
    # TODO: use another key to start each new trial
    if use_response_pad:
        start_message = \
            ex.stimuli.TextBox('Press anything but the bottom left button to start a block.',(400,400))
    else:
        start_message = \
          ex.stimuli.TextBox('Press anything but space bar to start a block.',(400,400))
    
    rhythm = stimulus['generate'](stimulus['n_synch'])
    
    if use_response_pad:
        responder = NanpadResponder()
    else:
        responder = KeyboardResponder()
    
    for block in range(env['num_blocks']):
        start_message.present()
        listen_time = rhythm.get_length()*1000 + stimulus['continuation_ms']
        
        timestamp = datetime.datetime.now()
        # TODO: wait for user to indicate they're starting
        env['exp'].screen.clear()
        with responder:
            rhtyhm.play()
            
            for i in range(np.ceil(listen_time / 500.0)):
                for time,pressure in responder.collect_events(500):
                    write_line({'block': block,
                                'time': time,
                                'pressure': pressure,
                                'block_timestamp': timestamp},
                                ['block','time','pressure','block_timestamp'])
    

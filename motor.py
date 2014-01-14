import pyxid
from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info

trigger_key = 2 # round center button

# keyboard responder (used for debugging purposes)
class KeyboardResponder:
    def __init__(self,key,short_time_ms = 10):
        self.key = key
        self.short_time = short_time_ms / 1000.0
    def prepare(self):
        clearEvents()
    def wait_for_trigger(self):
        waitKeys([self.key])

    def set_end(self,wait_time_ms):
        self.wait = getTime() + wait_time_ms / 1000.0
    def collect_events_until_end(self,env,block,events):
        while getTime() < self.wait:
            for key_event in getKeys([self.key],timeStamped=True):
                print key_event
                event = Info()
                event.time = "%.6f" % key_event[1]
                event.block = block

                events.append(event)
            time = max(0,min(self.wait - getTime(),self.short_time))
            wait(time,time)

        return events
    def all_events_up_to_end(self,env,block,events):
        # TODO: this might miss a few keyboard presses
        # but since this implementaiton is really just a
        # debugging place holder, I'm not worrying about it right now
        return self.collect_events_until_end(env,block,events)
        

class CedrusPadResponder:
    def __init__(self,key,short_time_ms = 30):
        pyxid.use_response_pad_timer = True
        devices = pyxid.get_xid_devices()
        self.key = key
        self.dev = devices[0]
        self.short_time = short_time_ms
        
    def prepare(self):
        self.dev.clear_response_queue()
        self.dev.reset_base_timer()
        self.dev.reset_rt_timer()
        
    def wait_for_trigger(self):
        triggered = False
        # wait for the trigger button to be pressed
        while not triggered:
            self.dev.poll_for_response()
            while self.dev.response_queue_size() > 0:
                response = self.dev.get_next_response()
                print response
                if response['pressed'] and response['key'] == self.key:
                    triggered = True

        # wait until no more keys are being pressed
        while self.dev.response_queue_size() > 0:
            self.dev.clear_response_queue()
            self.dev.poll_for_response()

    def set_end(self,wait_time_ms):
        self.wait = self.dev.query_base_timer() + wait_time_ms
            
    def collect_events_until_end(self,env,block,events):
        while self.dev.query_base_timer() < self.wait - self.short_time:
            print "hi1"
            self.dev.poll_for_response()

            while self.dev.response_queue_size() > 0 and \
                self.dev.query_base_timer() < self.wait - self.short_time:
                print "hi2"

                print self.dev.query_base_timer()
                
                response = self.dev.get_next_response()
                print response
                event = Info()
                event.time = "%.6f" % (response['time'] / 1000.0)
                event.block = block

                events.append(event)

            print "hi4"
            time = min(self.wait - self.dev.query_base_timer(),self.short_time)
            time = time/1000.0
            wait(time,time)

        if self.dev.query_base_timer() < self.wait:
            print "hi"
            time = (self.wait - self.dev.query_base_timer())/1000.0
            wait(time,time)

        return events

    def all_events_up_to_end(self,env,block,events):
        events = self.collect_events_until_end(env,block,events)
        while self.dev.response_queue_size() > 0:
            print self.dev.query_base_timer()
            
            response = self.dev.get_next_response()
            print response
            event = Info()
            event.time = "%.6f" % (response['time'] / 1000.0)
            event.block = block
            
            events.append(event)

        return filter(lambda e: e.time < self.wait,events)
        

def run(env,stimulus,write_line):
    start_message = TextStim(env.win,text='Press space bar to start a block.')

    beep = Sound(tone(stimulus.freq_Hz,stimulus.beep_ms,
                      stimulus.atten_dB,stimulus.ramp_ms,
                      env.sample_rate_Hz).copy())

    #responder = KeyboardResponder('space')
    responder = CedrusPadResponder(trigger_key)

    for block in range(env.num_blocks):
        start_message.draw()
        env.win.flip()
        responder.wait_for_trigger()
        responder.prepare()
        env.win.flip()

        events = []
        for cycle in range(env.n_synch):
            for interval in stimulus.intervals:
                responder.set_end(interval)
                beep.play()
                events = responder.collect_events_until_end(env,block,events)
                                
        responder.set_end(env.continuation_ms)
        events = responder.all_events_up_to_end(env,block,events)

        for event in events: write_line(event)

        
        
    
        
        

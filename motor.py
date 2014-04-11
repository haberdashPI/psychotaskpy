import pyxid
from psychopy.sound import Sound
from psychopy.visual import TextStim
from psychopy.event import getKeys, waitKeys, clearEvents
from psychopy.core import *
from util import tone, Info

use_response_pad = False
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
    def collect_events_until_end(self,block,events):
        while getTime() < self.wait:
            for key_event in getKeys([self.key],timeStamped=True):
                event = {'time': key_event[1], 'block': block}
                events.append(event)
            time = max(0,min(self.wait - getTime(),self.short_time))
            wait(time,time)

        return events
    def all_events_up_to_end(self,block,events):
        # TODO: this might miss a few keyboard presses
        # but since this implementaiton is really just a
        # debugging place holder, I'm not worrying about it right now
        return self.collect_events_until_end(block,events)
        

class CedrusPadResponder:
    def __init__(self,key,short_time_ms = 10):
        pyxid.use_response_pad_timer = True
        devices = pyxid.get_xid_devices()
        self.key = key
        self.dev = devices[0]
        self.short_time = short_time_ms/1000.0
        
    def prepare(self):
        self.dev.clear_response_queue()
        self.dev.reset_base_timer()
        self.dev.reset_rt_timer()
        self.prepare_time = getTime()/1000.0
        
    def wait_for_trigger(self):
        triggered = False
        self.dev.clear_response_queue()
        
        # wait for the trigger button to be pressed
        self.dev.poll_for_response()
        while (self.dev.response_queue_size() > 0) or (not triggered):
            if self.dev.response_queue_size() > 0:
                response = self.dev.get_next_response()
                if not response['pressed'] and response['key'] == self.key:
                    triggered = True
                    
            wait(self.short_time,self.short_time)
            self.dev.poll_for_response()   

    def set_end(self,wait_time_ms):
        self.wait = getTime() + wait_time_ms/1000.0
        #self.dev.query_base_timer() + wait_time_ms
            
    def collect_events_until_end(self,block,events):
        # get as many responses as we can off of the queue.
        while getTime() < (self.wait - self.short_time):
            if self.dev.response_queue_size() > 0:
                response = self.dev.get_next_response()
                if response['pressed'] and response['key'] == self.key:
                    events.append({'time': response['time'] / 1000.0, 
                                   'block': block})

            #time = min(self.wait - self.dev.query_base_timer(),self.short_time)
            time = min(self.wait - getTime(),self.short_time)
            
            wait(time,time)

            self.dev.poll_for_response()

        # wait the remainder of the time.
        #if self.dev.query_base_timer() < self.wait:
        if getTime() < self.wait:
            #time = (self.wait - self.dev.query_base_timer())/1000.0
            time = self.wait - getTime()
            wait(time,time)

        return events

    def all_events_up_to_end(self,block,events):
        # collect most of the events
        events = self.collect_events_until_end(block,events)

        # get any remaining events off of the queue
        self.dev.poll_for_response()
        while self.dev.response_queue_size() > 0:
            #print self.dev.query_base_timer()
            
            response = self.dev.get_next_response()

            events.append({'time': response['time'] / 1000.0,
                           'block': block})

            self.dev.poll_for_response()

        # only return those events that fall within the 
        # given window of time.
        return filter(lambda e: e['time'] + self.prepare_time < self.wait,events)
        

def run(env,stimulus,write_line):
    if use_response_pad:
        start_message = TextStim(env['win'],text='Press center button to start a block.')
    else:
        start_message = TextStim(env['win'],text='Press space bar to start a block.')
    
    beep = Sound(tone(stimulus['freq_Hz'],stimulus['beep_ms'],
                      stimulus['atten_dB'],stimulus['ramp_ms'],
                      env['sample_rate_Hz']).copy())
    
    if use_response_pad:
        responder = CedrusPadResponder(trigger_key)
    else:
        responder = KeyboardResponder('space')
    
    
    for block in range(env['num_blocks']):
        start_message.draw()
        env['win'].flip()
        responder.wait_for_trigger()
        responder.prepare()
        env['win'].flip()
        
        events = []
        for cycle in range(env['n_synch']):
            for interval in stimulus['intervals']:
                responder.set_end(interval)
                beep.play()
                events = responder.collect_events_until_end(block,events)
                
        responder.set_end(env['continuation_ms'])
        events = responder.all_events_up_to_end(block,events)
                
        for event in events: write_line(event,['block','time'])

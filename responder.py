import expyriment as ex
import threading
import rtmidi
import pygame
import numpy as np

def nanopad(exp):
    return _ResponderContext(_NanopadResponder())
# def keyboard(exp):
#     return _ResponderContext(_KeyboardResponder(exp))

nanopad.message = 'Press bottom left button to begin.'
#keyboard.message = 'Press spacebar to begin.'

class _ResponderContext:
    def __init__(self,responder):
        self.responder = responder
    def __enter__(self):
        self.responder._on_enter()
        return self.responder
    def __exit__(self,type,value,traceback):
        self.responder._on_exit()

KEY_UP_CODE = 128
KEY_DOWN_CODE = 144
CLOCK_RESET_CODE = 250
#KEYBOARD_TRIGGER = pygame.locals.K_SPACE
NANO_TRIGGER = 36 #(far left, bottom button)

# KeyboardResponder is used for debugging purposes when the nanopad is
# unavailable. It will not provide reliable timing results.
# class _KeyboardResponder:
#     def __init__(self,exp,key = KEYBOARD_TRIGGER):
#         self.key = key
#         self.exp = exp
        
#     def _on_enter(self):
#         pass
#     def _on_exit(self):
#         pass

#     def __translate_key(self,key):
#         return [[KEY_DOWN_CODE,key,0],0.5]

#     def callback(self,fn):
#         self.callback = fn
#         return _ResponseCollector(self)

#     def wait_for_press(self):
#         waiter = ex.misc.Clock()
#         key,_ = self.exp.keyboard.wait()
#         while key is not self.key:
#             key,_ = self.exp.keyboard.wait()
#             waiter.wait(10)
        
#     def collect_messages(self):
#         keys = []
#         key = self.exp.keyboard.check(self.key)
#         while key is not None:
#             keys.append(key)
#             key = self.exp.keyboard.check(self.key)

#         return map(self.__translate_key,keys)

class _NanopadResponder:
    def __init__(self,key = NANO_TRIGGER):
        self.dev = rtmidi.MidiIn(queue_size_limit=2**12)
        self.key = key
        self.clock = ex.misc.Clock()
        self.last_message_time = 0
        self.initiate_callback_time = 0

    def __get_message(self,initiate_callback=False):
        message = self.dev.get_message()
        # this is not perfect but it will provide a ballpark estimate of
        # the start time
        message_time = self.clock.time
        if message:
            self.last_message_time += message[1]*1000
            
            if initiate_callback:
                print "YO!"
                self.initiate_callback_time = self.last_message_time

            print "----"
            print "message time: "+str(self.last_message_time)
            print "callback time: "+str(self.initiate_callback_time)
            return message + (self.last_message_time - self.initiate_callback_time,)
        else: return message

    def _on_enter(self):
        self.dev.open_port(0)
                
    def _on_exit(self):
        self.dev.close_port()

    def callback(self,fn):
        self._callback_fn = fn
        print "prepare callback time!"
        self.wait_for_press(True)
        return _ResponderCallback(self)

    def wait_for_press(self,initiate_callback=False):
        waiter = ex.misc.Clock()
        message = self.__get_message(initiate_callback)
        while message is None or message[0][1] != self.key:
            message = self.__get_message(initiate_callback)
            waiter.wait(10)

    def collect_messages(self):
        # return messages
        messages = []
        message = self.__get_message()
        while message is not None:
            messages.append(message)
            message = self.__get_message()

        return messages

class _ResponderCallback:
    def __init__(self,responder):
        self.responder = responder

    def __enter__(self):
        self.responder.done = False
        return _ResponseCollector(self.responder)

    def __exit__(self,type,value,traceback):
        self.responder.done = True
 
class _ResponseCollector:
    def __init__(self,responder):
        self.responder = responder
        self.last_collected = 0
        self.last_event = 0
        self.clock = ex.misc.Clock()
                        
        self.thread = threading.Thread(target=self.__run_thread)
        self.thread.start()

    def __run_thread(self):
        while not self.responder.done:
            if self.responder._callback_fn:
                self.responder._callback_fn(self.__collect_events())
            self.clock.wait(250)

    def __collect_events(self):
        messages = self.responder.collect_messages()
        if messages:
            times = np.array(map(lambda m: m[2],messages))
            codes = np.array(map(lambda m: m[0][0],messages))
            strengths = np.array(map(lambda m: m[0][2],messages))

            # filter out anything but keydown messages 
            times = times[(codes == KEY_DOWN_CODE)]
            strengths = strengths[(codes == KEY_DOWN_CODE)]

            return zip(times,strengths)
        else:
            return []

    # def __collect_events(self):
    #     messages = self.responder.collect_messages()
    #     # oragnize all messages 
    #     if messages:
    #         times = np.cumsum(map(lambda m: m[1],messages))*1000.0
    #         codes = np.array(map(lambda m: m[0][0],messages))
    #         strengths = np.array(map(lambda m: m[0][2],messages))

    #         event_offset = self.last_event
    #         self.last_event = times[len(times)-1] + event_offset

    #         # filter out anything but keydown messages 
    #         times = times[(codes == KEY_DOWN_CODE)] + event_offset
    #         strengths = strengths[(codes == KEY_DOWN_CODE)]

    #         return zip(times,strengths)
    #     else:
    #         return []

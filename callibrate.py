from psychopy.gui import DlgFromDict
from util import *
from psychopy.sound import Sound
from psychopy.core import *

setup = {'frequency': 1000,'attenuation': 0}
dialog = DlgFromDict(dictionary=setup,title='Calibration',
            order=['frequency','attenuation'])
if dialog.OK:
    print setup['attenuation']
    beep = left(tone(setup['frequency'],5000,setup['attenuation'],5,44100))
    sound = Sound(beep.copy())
    sound.play()
    wait(5,5)
                

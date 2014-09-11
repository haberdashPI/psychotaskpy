from psychopy.gui import DlgFromDict
from util import *
from psychopy.sound import Sound
from psychopy.core import *

setup = {'frequency': [1000,4000],'attenuation': 0,'ear': ['left','right']}
dialog = DlgFromDict(dictionary=setup,title='Calibration',
            order=['frequency','attenuation','ear'])
if dialog.OK:
    print setup['attenuation']
    if setup['ear'] == 'left':
        beep = left(tone(float(setup['frequency']),5000,setup['attenuation'],5,44100))
    else:
        beep = right(tone(float(setup['frequency']),5000,setup['attenuation'],5,44100))
    sound = Sound(beep.copy())
    sound.play()
    wait(5,5)

# left attenuation: 35.6
# right attenuation: 38.7
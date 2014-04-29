from psychopy.gui import DlgFromDict

setup = {'frequency': 1000,'attenuation': 0}
dialog = DlgFromDict(dictionary=setup,title='Calibration',
            order=['frequency','attenuation'])
if dialog.OK:
    beep = tone(setup['frequency'],5000,setup['attenuation'],5,44100)

    sound = Sound(beep.copy())
    sound.play()
                
                

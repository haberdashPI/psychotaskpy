from util import *
import pygame
import pygame.mixer as mix
import sys
import time

if len(sys.argv) >= 4:
    atten = int(sys.argv[1])
    freq = int(sys.argv[2])
    length = int(sys.argv[3])
    side = sys.argv[3]
else:
    atten = 30.4
    freq = 1000
    length = 5000
    side = 'left'

mix.pre_init(channels=2)
pygame.init()

if side == 'left':
    floats = left(tone(freq,length,atten,5,44100))
else:
    floats = right(tone(freq,length,atten,5,44100))
sound = mix.Sound(np.asarray(floats*(2**15),'int16'))
sound.play()
time.sleep(length/1000)
# left 31.1
# right 30.4
from util import *
import pygame
import pygame.mixer as mix
import sys

if len(sys.argv) >= 4:
    atten = int(sys.argv[1])
    freq = int(sys.argv[2])
    length = int(sys.argv[3])
    side = sys.argv[3]
else:
    atten = 20
    freq = 1000
    length = 1000
    side = 'left'

pygame.init()

if side == 'left':
    floats = left(tone(freq,length,atten,5,44100))
else:
    floats = right(tone(freq,length,atten,5,44100))
sound = mix.Sound(np.asarray(floats*(2**15),'int16'))
sound.play()

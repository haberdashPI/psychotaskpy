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
    atten = 9.3
    freq = 1000
    length = 10000
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

# 70 is 20 dB SPL 250
# 71.3 is 20 dB SPL 500
# 75 is 20 dB SPL 1k
# 67.5 is 20 dB SPL 2k
# 66 is 20 dB SPL 4k
# 65 is 20 dB SPL 8k
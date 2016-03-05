from util import *
import pygame
import pygame.mixer as mix
import sys
import time

# HOW TO USE THIS FILE:
# Run the file to test out a given attenuation  (by setting that attenuation
# using the appropriate parameters listed below).
# Then save that attenuation in the appropriate global variable,
# to be accessed by other modules.

atten_20dB_by_freq = \
    {'left': {'250': 70, '500': 71.3, '1k': 75, '2k': 67.5,
              '4k': 66, '8k': 65},  # calibrated on 05-20-15
     'middle': {'250': 71.2, '500': 73.2, '1k': 79.4,
                '2k': 76.8, '4k': 70.9, '8k': 71.7},  # calibrated on 08-12-15

     'right': {'250': 77.2, '500': 73.6, '1k': 78.2,
               '2k': 76.6, '4k': 78.6, '8k': 71.9},  # calibrated on 08-12-15
     'corner': {'250': 74.5, '500': 79.2, '1k': 78.6,
                '2k': 76.2, '4k': 72.2, '8k': 71.2},  # calibrated on 08-12-15
     'none': {'250': 70, '500': 71.3, '1k': 75, '2k': 67.5,
              '4k': 66, '8k': 65}}

atten_86dB_for_left = \
    {'corner': 13,  # calibrated on 08-12-15
     'left': 9.3,     # calibrated on 05-20-15
     'middle': 14.9,  # calibrated on 08-12-15
     'right': 13.8,   # calibrated on 08-12-15
     'none': 26}

atten_70dB_for_LR = \
    {'corner': {'right': {500: 25.6, 4000: 25.6, 6000: 24.0},
                'left': {500: 22.7, 4000: 22.7, 6000: 23.1}},  # calibrated on 08-12-15
     # calibrated on 08-12-15
     'left': {'right': {500: 18.0, 4000: 18.0, 6000: 20.5},
              'left': {500: 20.2, 4000: 20.2, 6000: 14.1}},
     # calibrated on 08-12-15
     'middle': {'right': {500: 22.3, 4000: 22.3, 6000: 19.3},
                'left': {500: 24.6, 4000: 24.6, 6000: 23.9}},
     # calibrated on 08-12-15
     'right': {'right': {500: 31.6, 4000: 31.6, 6000: 23.5},
               'left': {500: 32.4, 4000: 32.4, 6000: 23.3}},
     'none': {'right': {500: 45, 4000: 45, 6000: 20},
              'left': {500: 45, 4000: 45, 6000: 20}}}

if __name__ == "__main__":

    if len(sys.argv) >= 4:
        atten = int(sys.argv[1])
        freq = int(sys.argv[2])
        length = int(sys.argv[3])
        side = sys.argv[3]
    else:
        atten = 20.5
        freq = 6000
        length = 10000
        side = 'left'

    mix.pre_init(channels=2)
    pygame.init()

    if side == 'left':
        floats = left(tone(freq, length, atten, 5, 44100))
    else:
        floats = right(tone(freq, length, atten, 5, 44100))
    sound = mix.Sound(np.asarray(floats * (2**15), 'int16'))
    sound.play()
    time.sleep(length / 1000)
    # left 31.1
    # right 30.4

    # 70 is 20 dB SPL 250
    # 71.3 is 20 dB SPL 500
    # 75 is 20 dB SPL 1k
    # 67.5 is 20 dB SPL 2k
    # 66 is 20 dB SPL 4k
    # 65 is 20 dB SPL 8k

#!/usr/bin/env python3
# Tap_A_Sound by Mike Cook August 2020
# using external CalTap class
# Takes sounds from the "samples" directory

import time
from os import walk
from pygame import mixer
import board
import neopixel
from caltap import CalTap
tap = CalTap()

pixel_pin = board.D18
num_pixels = 128
# RGB or GRB. Some NeoPixels have red and green reversed
ORDER = neopixel.GRB
BRIGHTNESS = 0.1 # 0.6 is maximum brightness for 3A external supply
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
         brightness = BRIGHTNESS, auto_write = False,
         pixel_order = ORDER)
mixer.pre_init(44100, -16, 12, 512)
mixer.init()
soundNames = []
f = []
for (dirpath, dirnames, soundNames) in walk("samples/"):
     f.extend(soundNames)
     break
soundNames.sort()    
#print(soundNames)    
print(len(soundNames))
sounds = [ mixer.Sound("samples/"+soundNames[i])
           for i in range(0, len(soundNames))]
mixer.set_num_channels(16)

print("Tap to here a sound")
# put your own colours here
colours = [(255, 0, 0), (255, 72, 0), (255, 145, 0),
           (255, 218, 0), (218, 255, 0), (145, 255, 0),
           (72, 255, 0), (0, 255, 0), (255,255,255) ]
pixels.fill((32, 32, 32))
pixels.show()
tapCount = 0
while 1:
    if tap.touched():
        pos = tap.getPos()
        if pos[3] : # a valid measurement
            if pixels[pos[2]] != [32, 32, 32]:
               pixels[pos[2]] = (32, 32, 32) # turn off
            else:
               pixels[pos[2]] = colours[tapCount]
               sounds[pos[2]].play()
               print("Playing",soundNames[pos[2]])
            pixels.show()
            tapCount += 1
            if tapCount >= len(colours) : tapCount = 0
            while tap.touched() : pass    
            


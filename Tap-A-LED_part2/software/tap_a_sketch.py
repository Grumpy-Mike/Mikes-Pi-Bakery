#!/usr/bin/env python3
# Tap_A_Sketch by Mike Cook August 2020
# using external CalTap class
import time
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

print("Tap to change an LED")
# put your own colours here
colours = [(255, 0, 0), (255, 72, 0), (255, 145, 0),
           (255, 218, 0), (218, 255, 0), (145, 255, 0),
           (72, 255, 0), (0, 255, 0), (255,255,255) ]
pixels.fill((0, 0, 0))
for i in range(8):
    pixels[i] = colours[i % len(colours)]
    pixels[i+120] = colours[i % len(colours)]
pixels.show()
tapCount = 0
while 1:
    if tap.touched():
        pos = tap.getPos()
        if pos[3] : # a valid measurement
            if pixels[pos[2]] != [0, 0, 0]:
               pixels[pos[2]] = (0, 0, 0) # turn off
            else:
               pixels[pos[2]] = colours[tapCount]
            pixels.show()
            tapCount += 1
            if tapCount >= len(colours) : tapCount = 0
            while tap.touched() : pass    
            


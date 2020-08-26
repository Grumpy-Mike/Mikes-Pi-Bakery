#!/usr/bin/env python3
# LED Matrix test - Mike Cook July 2020
# Needs to run in supervisor mode
# sudo /usr/bin/idle-python3.7
# or modify the "Desktop entry" to what IDE you use to include sudo at the start

import time
import board
import neopixel
import random

def main():
    init()
    print("Neopixel LED test run an LED round the matrix")
    mPass = 6
    while True:
        mPass += 1
        if mPass > 7 : mPass = 1
        colour(mPass)
        displayTAP(0.05, 0.8, True, False)

def init():
    global defineT, defineA, defineP, tap
    global pixels
    defineT = [ 6, 14, 22, 30, 38, 21, 20, 19, 18, 17 ]
    defineA = [ 62, 70, 53, 77, 52, 76, 51, 59, 67, 75, 50, 74, 49, 73 ]
    defineP = [ 89, 90, 91, 92, 93, 94, 102, 110, 117, 116, 107, 99 ]
    tap = [ defineT, defineA, defineP ]
    random.seed()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.6 # this is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                               brightness = BRIGHTNESS,
                               auto_write=False, pixel_order = ORDER)

def displayTAP( pixelDelay, letterDelay, wipe, keepCol):
    global col
    for i in range(3):
        if not keepCol:
            newCol = col
            while newCol == col :
                colour(random.randint(1,7))
        for j in range(len(tap[i])):
            pixels[tap[i][j]] = col
            pixels.show()
            time.sleep(pixelDelay)
        time.sleep(letterDelay)
    #junk = input(" ")
    if wipe :
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(letterDelay)
                                              
def colour(n): # different colour on each pass
    global col
    col = ((n & 1) * 255, ((n & 2)>>1) * 255, ((n & 4)>>2) * 255)
    
# Main program logic:
if __name__ == '__main__':
   main()

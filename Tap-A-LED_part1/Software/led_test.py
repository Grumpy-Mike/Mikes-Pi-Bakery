#!/usr/bin/env python3
# LED Matrix test - Mike Cook July 2020
# Needs to run in supervisor mode
# sudo /usr/bin/idle-python3.7
# or modify the "Desktop entry" to what IDE you use to include sudo at the start

import time
import board
import neopixel

pixel_pin = board.D18
num_pixels = 128
# RGB or GRB. Some NeoPixels have red and green reversed
ORDER = neopixel.GRB
BRIGHTNESS = 0.6 # this is maximum brightness for 3A external supply
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
         brightness = BRIGHTNESS, auto_write=False,
         pixel_order = ORDER)

def main():
    print("Neopixel LED test run an LED round the matrix")
    mPass = 6
    while True:
        mPass += 1
        if mPass > 7 : mPass = 1
        colour(mPass)
        for i in range(num_pixels):
            pixels[i] = col
            pixels.show()
            time.sleep(0.1)
            pixels.fill((0, 0, 0))

def colour(n): # different colour on each pass
    global col
    col = ((n & 1) * 255, ((n & 2)>>1) * 255, ((n & 4)>>2) * 255)
    
# Main program logic:
if __name__ == '__main__':
   main()

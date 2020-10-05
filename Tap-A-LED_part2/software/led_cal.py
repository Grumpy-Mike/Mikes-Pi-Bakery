#!/usr/bin/env python3
# calibration - Mike Cook July 2020
# Tap three LEDs, paste the output into the caltap.py program
# Needs to run in supervisor mode
# sudo /usr/bin/idle-python3.7
# or modify the "Desktop entry" to what IDE you use to include sudo at the start

import time
import board
import neopixel
from stmpe610 import Stmpe610

pixel_pin = board.D18
num_pixels = 128
# RGB or GRB. Some NeoPixels have red and green reversed
ORDER = neopixel.GRB
BRIGHTNESS = 0.2 # 0.6 is maximum brightness for 3A external supply
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
         brightness = BRIGHTNESS, auto_write=False,
         pixel_order = ORDER)

def main():
    print("Touch sensor / LED calibration")
    touch = Stmpe610()
    print("Tap the screen in the far most left hand bottom corner")
    arrow = [ 0, 1, 2, 3, 8, 16, 24, 9, 18, 27, 36 ]
    draw(arrow)
    print("corner1 =", end =" ")
    getTap(touch)
    print("Now tap the top right corner")
    arrow = [ 91, 100, 109, 118, 127, 126, 125, 124, 119, 111, 103 ]
    draw(arrow)
    print("corner2 =", end =" ")
    getTap(touch)
    print("next tap in the CENTER of each lit pixel")
    pix = [ 0, 7, 120 ]    
    for i in range(0, 3):
        pixels.fill((0, 0, 0))
        pixNum = pix[i]
        pixels[pixNum] = (255, 0, 0)
        pixels.show()
        name = "led"+str(pixNum)
        print(name, "=", end =" ")
        taps = 0
        while taps < 1:
            if touch.touched():
                print(touch.readPos())
                while touch.touched() : pass
                taps += 1
        pixels.fill((0, 0, 0))
        pixels.show()
    print("Finished, thank you")
    
def draw(shape):
    pixels.fill((0, 0, 0))
    for i in range(len(shape)):
        pixels[shape[i]] = (255, 0, 0)
    pixels.show()    
        
def getTap(touch):
    noTap = True
    while noTap :
        if touch.touched():
            print(touch.readPos())
            noTap = False
            while touch.touched() : pass


    
# Main program logic:
if __name__ == '__main__':
   main()

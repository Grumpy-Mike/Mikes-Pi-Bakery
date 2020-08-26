#!/usr/bin/env python3
# LED Matrix test Pal- Mike Cook July 2020
# using  pallette file
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
    global pixels, pallet
    defineT = [ 6, 14, 22, 30, 38, 21, 20, 19, 18, 17 ]
    defineA = [ 62, 70, 53, 77, 52, 76, 51, 59, 67, 75, 50, 74, 49, 73 ]
    defineP = [ 89, 90, 91, 92, 93, 94, 102, 110, 117, 116, 107, 99 ]
    tap = [ defineT, defineA, defineP ]
    random.seed()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.4 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                               brightness = BRIGHTNESS,
                               auto_write=False, pixel_order = ORDER)
    pallet = [(0, 0, 0)]*16
    loadPallet("pallets/hsv16.pal")
    #loadPallet("pallets/first16.pal")
    #loadPallet("pallets/first16hsv.pal")
    #oadPallet("pallets/hsv8.pal")
    #loadPallet("pallets/hsv6.pal")

def displayTAP( pixelDelay, letterDelay, wipe, keepCol):
    global col
    for i in range(3):
        for j in range(len(tap[i])):
            pixels[tap[i][j]] = colour(j)
            pixels.show()
            time.sleep(pixelDelay)
        time.sleep(letterDelay)
    #junk = input(" ")
    if wipe :
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(letterDelay)
        
def loadPallet(name):
    global pallet, palletLength 
    file = open(name, "r")
    if file.mode == 'r' :
        lines = file.readlines()
        i = 0;
        for line in lines :
            if i == 0 and line != "JSC-PAL\n" :
                print('Not a valid .pal file')
                terminate()
            if i == 2 :
                #print('pallet size ' + (line))
                palletLength = int(line)
                
            if i > 2 :
                entry = line.split(" ", 4)
                pallet[i-3] = (int(entry[0]), int(entry[1]), int(entry[2]))
            i += 1
    file.close()
                                              
def colour(n): # chose colour from Pallette
    if n >= palletLength :
        n = n % palletLength
    return pallet[n]
    
# Main program logic:
if __name__ == '__main__':
   main()

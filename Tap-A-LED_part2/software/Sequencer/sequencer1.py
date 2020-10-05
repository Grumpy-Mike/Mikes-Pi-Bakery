#!/usr/bin/env python3
# Sequencer1 by Mike Cook August 2020
#Plays samples from a file

import time
from pygame import mixer
import board
import neopixel
from caltap import CalTap

def main():
    global markTime, stepTime
    init()
    print("Sequencer - playing samples through the audio output")
    print("Tap to add or remove samples")
    t = float(input("Please enter the speed in BPM "))
    stepTime = 1/((t/60)*4) # assume 4 beats in a bar
    tapCount = 0
    beingTouched = False
    while 1:
        if time.time() - markTime >= stepTime :
            markTime = time.time()
            nextStep()
        if tap.touched() and not beingTouched:
            pos = tap.getPos()
            if pos[3] : # a valid reading
                if pixels[pos[2]] != [0, 0, 0]:
                   pixels[pos[2]] = (0, 0, 0) # turn off
                else:
                   pixels[pos[2]] = colours[pos[1]]
                tapCount += 1
                if tapCount >= len(colours) : tapCount = 0
                beingTouched = True   
                pixels.show()
        else :
            if not tap.touched() : beingTouched = False  
            
def init():
    global colours, tap, pixels, posScan , stepTime, markTime
    global colBuffer, sounds
    # put your own colours here
    colours = [(255, 0, 0), (255, 72, 0), (255, 145, 0),
               (255, 218, 0), (218, 255, 0), (145, 255, 0),
               (72, 255, 0), (0, 255, 0), (255,255,255) ]
    tap = CalTap()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.1 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)
    pixels.fill((0, 0, 0))
    posScan = 0 ; stepTime = 0.3 ; markTime = time.time()
    colBuffer = [(0,0,0)] * 8
    mixer.pre_init(44100, -16, 12, 512)
    mixer.init()
    # change these to other sample names
    soundNames = ["0", "1",
            "2", "3",
            "4", "5",
            "6", "7" ]
    # change Marimba to another directory containing your samples 
    sounds = [ mixer.Sound("Marimba/"+
               soundNames[i]+".wav")
               for i in range(0,len(soundNames))]
    mixer.set_num_channels(16)

def nextStep():
    global posScan
    putCol(posScan)
    posScan +=1
    if posScan > 15 : posScan = 0
    getCol(posScan)
    for i in range(8):
        pixels[i + posScan * 8] = dimCol(i)
    pixels.show()    

def dimCol(i):
    thresh = 40
    r = colBuffer[i][0]
    g = colBuffer[i][1]
    b = colBuffer[i][2]
    if r > thresh :
        r -= thresh
    else: r += thresh    
    if g > thresh :
        g -= thresh
    else: g += thresh    
    if b > thresh :
        b -= thresh
    else: b += thresh
    return ( r, g, b )

def putCol(pos): # restore old column of colours
    for i in range(8):
        pixels[i + pos * 8] = colBuffer[i] 
        
def getCol(pos):
    for i in range(8):
        colBuffer[i] = pixels[i + pos * 8]
        #print(colBuffer[i])
        if (colBuffer[i] != [0, 0, 0]):
            sounds[i].play()  
    
# Main program logic:
if __name__ == '__main__':    
    main()

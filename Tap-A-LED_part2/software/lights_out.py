#!/usr/bin/env python3
# Lights out a game by Mike Cook October 2020
# Turn out all the LEDs by tapping them but a tap also inverts the state
# of all adjecent LEDs, with wrap round on the eges
import time
import board
import neopixel
import random
from pygame import mixer
from caltap import CalTap

def main() :
    init()
    print("Turn out all the LEDs")
    over = True
    while 1:
        while not over:
            if tap.touched():
                pos = tap.getPos()
                if pos[3] : # a valid measurement
                    toggel(posToxy(pos[2]), True)
                    over = checkForWin()
                    if over :
                        print("YOU WIN!")
                        finish.play()
                        displayWin()
            else:
                time.sleep(0.05)
        print("Try and clear this")        
        newBoard()
        over = False
        
def toggel(place, sound):
    global pixels, tapCount
    incX = [0, 1, -1, 0, 0]
    incY = [0, 0, 0, 1, -1]
    for i in range(5) :
        x = place[0] + incX[i]
        x &= 0x0F
        y = place[1] + incY[i]
        y &= 0x07
        pix = y + (x * 8)
        tapCount += 1
        if tapCount >= len(colours) : tapCount = 0
        if pixels[pix] != [0, 0, 0]:
            pixels[pix] = (0, 0, 0) # turn off
            pixels.show()
            if sound : sound1.play() ; time.sleep(0.4)
        else:
            pixels[pix] = colours[tapCount]
            pixels.show()
            if sound : sound2.play() ; time.sleep(0.4)       
    while tap.touched() : pass
        
def posToxy(pos):
    y = pos % 8
    x = pos // 8
    return (x , y)

def newBoard():
    global pixels
    for i in range(random.randint(8, 18)):    
        toggel(posToxy(random.randint(0, 127)), False)
    pixels.show()    
    
def init():
    global colours, tapCount, pixels, tap, sound1, sound2, finish
    global win
    win = [ 2, 3, 4, 5, 6, 7, 9, 18, 19, 20, 25, 34, 35, 36, 37,
            38, 39, 49, 55, 57, 58, 59, 60, 61, 62, 63, 65, 71,
            81, 82, 83, 84, 85, 86, 87, 93, 100, 107, 113, 114,
            115, 116, 117, 118, 119 ]
    tap = CalTap()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.15 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)    
    colours = [(255, 0, 255), (170, 0, 255),(84, 0, 255),
               (0, 0, 255), (0, 84, 255),(0, 169, 255), (0, 255, 255),
               (0, 255, 169), (0, 255, 5), (0, 255, 0), (84, 255, 0),
               (170, 255, 0), (254, 255, 0), (255, 170, 0), (255, 84, 0),
               (255, 0, 0)] 
    pixels.fill((0, 0, 0))
    pixels.show()
    tapCount = 0
    random.seed()
    mixer.pre_init(44100, -16, 12, 512)
    mixer.init()
    sound1 = mixer.Sound("samples/AA2.wav")
    sound2 = mixer.Sound("samples/AA7.wav")
    finish = mixer.Sound("samples/Triumph.wav")

def checkForWin():
    win = True
    for i in range(128):
        if pixels[i] != [0, 0, 0]: win = False
    return win

def displayWin():
    startTime = time.time()
    duration = 5.0
    while time.time() - startTime < duration :
        col = colours[random.randint(0,len(colours)-1)]
        for i in range(len(win)):
            pixels[win[i]] = col
        pixels.show()
        time.sleep(0.4)    
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.3)
    
# Main program logic:
if __name__ == '__main__':    
    main()          


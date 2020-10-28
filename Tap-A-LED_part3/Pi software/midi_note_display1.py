#!/usr/bin/env python3
# coding=utf-8
# GPIO port Serial monitor talking MIDI
# displays the notes on an LED keyboard, received by the Arduino
# By Mike Cook August 2020

import serial
import time
import board
import neopixel
                       
comPort = serial.Serial(port = "/dev/serial0", baudrate = 250000,
                        parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)
# values in frame
# 0 = event type | 1 = event type with channel
# 2 = control number (0-119) | 3 = control value
frame = [0, 0, 0, 0]

def main():
    init()
    drawKeys()
    print("Draw notes sent, colour -> velocity")
    while 1:   
        readMIDI()
        if frame[0] == 0x9 or frame[0] == 0x8:
            keyToDraw = frame[2] % 12                          
            if frame[0] == 0x8:
                drawKey(keyToDraw, (128, 128, 128), ( 0, 0, 0)) # note off
            else :
                col = frame[3] // 8
                drawKey(keyToDraw, colours[col], colours[col]) # note on
            pixels.show()
                

def drawKeys():
    for k in range(12) : drawKey(k, (128, 128, 128), ( 0, 0, 0))
    i = 0
    for c in range(8) : pixels[c] = colours[i] ; i += 2
    i = 0
    for c in range(120,128) : pixels[c] = colours[i]  ; i += 2  
    pixels.show()        

def drawKey(keyNum, whiteCol, blackCol):
    whiteKey = True
    for k in range(len(blackKeys)):
        if keyNum == blackKeys[k] : whiteKey = False
    if whiteKey :
        offset = - 1
        if rightWhite[keyNum] : offset = 1
        for h in range(8): # draw the full bar
            pixels[((keyNum + 2) * 8) + h] = whiteCol
            
            for h in range(4): # fill the bar on one side
                pixels[(((keyNum + 2) + offset) * 8) + h] = (128, 128, 128)
                
    else :
        for h in range(4,8):
            pixels[((keyNum + 2) * 8) + h] = blackCol # black keys colour
   
def init():
    global pixels, blackKeys, rightWhite, colours
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.2 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)
    blackKeys = [ 1, 3, 6, 8, 10, 13]
    rightWhite = [True] * 12
    rightWhite[4] = False ; rightWhite[11] = False
    # put your own colours here
    colours = [(255, 0, 255), (170, 0, 255),(84, 0, 255),
               (0, 0, 255), (0, 84, 255),(0, 169, 255), (0, 255, 255),
               (0, 255, 169), (0, 255, 5), (0, 255, 0), (84, 255, 0),
               (170, 255, 0), (254, 255, 0), (255, 170, 0), (255, 84, 0),
               (255, 0, 0)] 

def readMIDI():
    global frame
    frame = [0, 0, 0, 0]
    string = ""
    i = 0
    done = False
    timeout = time.time()
    while time.time() - timeout < 0.01 and not done:
        if comPort.inWaiting() > 0:
            timeout = time.time()
            ch = comPort.read(1)
            if ch == b'\n' :
                if len(string) > 3:
                    frame = [int(s) for s in string.split() if s.isdigit()]
                done = True
            elif ch != b'\r' :
                string = string + ch.decode()

    
if __name__ == '__main__':
    main()

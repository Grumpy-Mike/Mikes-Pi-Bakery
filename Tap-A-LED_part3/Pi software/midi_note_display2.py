#!/usr/bin/env python3
# coding=utf-8
# displays the notes on an LED display, received by the Arduino
# each note an individual LED with velocity colour
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
    drawSides()
    print("Draw notes sent, one row per octave colour -> velocity")
    while 1:   
        readMIDI()
        if frame[0] == 0x9 or frame[0] == 0x8:
            noteNumber = frame[2]
            if frame[0] == 0x8:
                paintLED(noteNumber, ( 0, 0, 0)) # note off
            else :  
                col = frame[3] // 8
                paintLED(noteNumber, colours[col]) # note on
            pixels.show()
                
def paintLED(num, col):
    x = num % 12
    note = num
    y = 0
    while(note > 12) : note -= 12 ; y += 1 # find octave
    if x == 0 : y+=1 # keep on the same line for first note
    y -= 2 # shift down 
    if y >= 0 : # don't show lowest notes, you can't hear most
        pixels[(x + 2) * 8 + y] = col
        
def drawSides():
    i = 0
    for c in range(8) : pixels[c] = colours[i] ; i += 2
    i = 0
    for c in range(120,128) : pixels[c] = colours[i]  ; i += 2  
    pixels.show()        
   
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

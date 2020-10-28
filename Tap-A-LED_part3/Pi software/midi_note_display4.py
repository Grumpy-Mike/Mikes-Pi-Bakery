#!/usr/bin/env python3
# coding=utf-8
# displays the notes on screen, received by the Arduino
# channels 1, 2, 3, & 4 have their own keyboard
# all higher channels displayed on the bottom row
# each note an individual LED with velocity colour
# By Mike Cook September 2020

import serial
import os
import time
import pygame
                       
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
    drawScreen()
    while 1:
        checkForEvent()
        readMIDI()
        channel = frame[1] & 0xF
        if channel > 4 : channel = 4 # maximum display
        if frame[0] == 0x8:
            paint(frame[2], (0, 0, 0),channel) # note off
        if frame[0] == 0x9:  # note on
            if frame[3] == 0 : 
                paint(frame[2], (0, 0, 0),channel) # alternate note off value
            else:
                col = frame[3] // 8 
                paint(frame[2], colours[col],channel) # note on
        if frame[0] == 0xB :
            if frame[2] == 123 : drawScreen() # ; print("stop") # clear all note
                
def drawScreen():
    global actionRect, frameRect, maxFrameRect 
    screen.fill(backCol)
    for c in range(4):
        for i in range(len(display[c])):
            k = i % 12
            if kCol[k] == 0 :
                pygame.draw.polygon(screen, black, display[c][i], 0)
            else :
                pygame.draw.polygon(screen, white, display[c][i], 0)
                pygame.draw.polygon(screen, black, display[c][i], 1) # outline
    pygame.display.update()

def paint(num, col, c):
    num = num + 108 * c
    if num > 539 : num = 539
    k = num % 12
    if col == (0, 0, 0) : # means restore the key
        if kCol[k] == 0 :
            pygame.draw.polygon(screen, black, display[c][num], 0)
        else :
            pygame.draw.polygon(screen, white, display[c][num], 0)
            pygame.draw.polygon(screen, black, display[c][num], 1) # outline
    else :        
        pygame.draw.polygon(screen, col, display[c][num], 0)
        if kCol[k] != 0 : pygame.draw.polygon(screen, black, display[c][num], 1) # outline
    pygame.display.update()
    

def init():
    global colours, tap, pixels, backGround, drawCol, bgList
    global backCol, black, screen, ledRect, colRect, pallRect
    global textHeight, font, currentFrame, maxFrame
    global keys, white, kCol, ksp, display
    colours = [(255, 0, 255), (170, 0, 255),(84, 0, 255),
               (0, 0, 255), (0, 84, 255),(0, 169, 255), (0, 255, 255),
               (0, 255, 169), (0, 255, 5), (0, 255, 0), (84, 255, 0),
               (170, 255, 0), (254, 255, 0), (255, 170, 0), (255, 84, 0),
               (255, 0, 0)] 
    backGround = (8, 8, 8) ; black = (0, 0, 0)
    bgList = [backGround[0], backGround[1], backGround[2]]
    drawCol = 0
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT,
                              pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP])

    pygame.display.set_caption("Display MIDI channels 1 to 4 and higher channels all on the bottom row")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    sWide = 1280 ; sHigh = 600
    screen = pygame.display.set_mode([sWide,sHigh],
                                     0, 32)
    textHeight=26 ; font = pygame.font.Font(None, textHeight)
    backCol = (160,160,160) ; white = (255, 255, 255)
    kCol = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
    ksp = [0, 12, 20, 36, 40, 60, 72, 80, 94, 100, 116, 120] # ksp - keyStartPosition
    keys = [[ (0,0) ]] * 108 * 5  # 12 * 9 = 108 nine octaves
    display = []
    for chn in range(5):
        for i in range(108):
            octive = i // 12
            keys[i+ chn*108] = makeKeys(i, octive, chn)
        display.append(keys)    

def makeKeys(num, octNum, channel):
    y = 100 + 120 * channel
    note = num % 12
    x = 8 + ksp[note] + octNum * 140 
    if note == 0 or note == 5 : # key type 1
       poly = [ (x,y), (x, y-80), (x+12, y-80), (x+12, y -32), (x+20, y - 32),
                (x+20, y)]
    elif note == 2 or note == 7 : #key type 2
       poly = [ (x,y), (x, y - 32), (x + 4, y - 32), (x+4, y-80), (x+16, y-80),
                (x+16, y-32), (x+20, y-32), (x+20, y) ]
    elif note == 4 or note == 11 : # key type 3
        poly = [ (x, y), (x, y-32), (x+8, y-32), (x+8, y-80), (x+20, y-80),
                 (x+20, y)]             
    elif note == 9 : # key type 4
         poly = [ (x, y), (x, y-32), (x+6, y-32), (x+6, y-80), (x+18, y-80),
                  (x+18, y-32), (x+20, y-32), (x+20, y)]
    else : # key type 5
         poly = [ (x, y-32), (x, y-80), (x+11, y-80), (x+11, y-32)]
    return poly     
    
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
    
def terminate(): # close down the program
    pygame.quit() # close pygame
    os._exit(1)

def checkForEvent():   
    global timeInterval
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_EQUALS :
          timeInterval -= 0.1
          if timeInterval < 0 : timeInterval = 0.1
       if event.key == pygame.K_MINUS :
          timeInterval += 0.1
    '''     
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())    
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())
    '''    

# Main program logic:
if __name__ == '__main__':    
    main()        


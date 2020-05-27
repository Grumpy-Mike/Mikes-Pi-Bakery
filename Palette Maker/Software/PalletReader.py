#!/usr/bin/env python3
# coding=utf-8
# Pallet Reader
# simply reads the pallets made by Pallet Maker
# By Mike Cook April 2020

import pygame
import os
import time
from ky040 import Ky040

def main():
    init()
    loadPallet("pallets/first16hsv.pal")
    drawScreen()
    time.sleep(2.0)
    while 1 :
        checkForEvent()
        time.sleep(0.3)

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
    #print(pallet)
    
def init():
    global screen, screenWidth, screenHight, pallet
    pygame.init()
    pygame.display.set_caption("Pallet Reader")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,
                              pygame.QUIT])
    screenWidth = 820 ; screenHight = 80
    cp = (screenWidth // 2, screenHight // 2)
    screen = pygame.display.set_mode([screenWidth,
                                screenHight], 0, 32)
    pallet = [(0, 0, 0)]*16
    # this is the biggest pallet that my pallet Maker can produce
    # change the 16 to the biggest pallet you are expecting
    
def drawScreen() :
    screen.fill((255, 255, 255))
    for i in range(0,palletLength) :
        pygame.draw.rect(screen, pallet[i], (20 + i*50, 20, 30, 40 ), 0)
    pygame.display.update()
                              
def terminate(): # close down the program
    print('Closing down - it does nothing else')
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()

if __name__ == '__main__':
    main()

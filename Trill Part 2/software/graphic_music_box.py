#!/usr/bin/env python3
# Graphic Music Box by Mike Cook January 2020
# a wind up music box - using the Trill Ring
# double touch on ring changes the cylinder

import time
import os
import pygame
from trill_lib import TrillLib
import math
import colorsys

def main():
    global startTime, changCyl
    init()
    drawScreen()
    beingTouched = False
    startTime = time.time()
    tickTime = 0.5
    windTime = time.time()
    while 1:
        checkForEvent()
        if changeCyl : loadCylinder(cylinderNumber) # change tune
        playTune()
        if time.time() - windTime > tickTime:
            windTime = time.time()
            updateHalo(1)

def playTune():
    global tunePointer, startTime
    testTime = time.time()
    if testTime - startTime >= float(tune[tunePointer][0]) / tempo : # time for a sample?
        while testTime - startTime >= float(tune[tunePointer][0]) / tempo and energy != 0:
            #print(int(tune[tunePointer][1]) - 35)
            #print(tune[tunePointer][0]," ", testTime - startTime)
            sounds[int(tune[tunePointer][1]) - 35].play() 
            tunePointer += 1 
            if tunePointer >= len(tune) :
                tunePointer = 1
                time.sleep(2.0) # delay before start again
                startTime = time.time()    
        #print("looking for hold")
        ringSensor.readTrill()
        holdTime = time.time()
        if ringSensor.getNumTouches() !=0:
            while ringSensor.getNumTouches() !=0:
                if ringSensor.getNumTouches() > 1: changeCylinder()
                updateRingTouch()
                updateHalo(0)
                time.sleep(0.3)
                ringSensor.readTrill()
            startTime += time.time() - holdTime # move start time back so time.time() still follows the event time
            drawRing()
        if energy < 12: # if winding down add an increasing large gap
            holdTime = time.time()
            time.sleep((12 - energy) / 10)
            startTime += time.time() - holdTime
                                        
            
def init():
    global screen, textHeight, font
    global lastRingTouch, sounds, tune, tunePointer 
    global lineCol, hiCol, backCol, colours, tempo
    global ringSensor, trillCol, rx, ry, halo, energy
    global cylinderNumber, cylNames, changeCyl
    colours = [(160,160,160), (255, 0, 0), (255, 170, 0),
              (0, 255, 0), (0, 168, 255), (172, 0, 255), (255, 255, 255) ]
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
    pygame.display.set_caption("Music Box")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    sWide = 400 ; sHigh = 400
    padCo = (sWide//2 - 100, 48) # top of screen
    screen = pygame.display.set_mode([sWide,sHigh],
                                     0, 32)
    textHeight=24 ; font = pygame.font.Font(None, textHeight)
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.mixer.init()    
    sounds = [ pygame.mixer.Sound("music_box_sounds/"+str(i+35)+".wav")
           for i in range(50)]
    pygame.mixer.set_num_channels(16) 
    rawRect = pygame.Rect((338,160),(338,101))
    lineCol = (0,128,255) ; backCol = (160,160,160)
    hiCol = (0,255,255) # highlight colour
    trillCol = (32, 32, 32) ; textCol = (0, 0, 0)
    ringSensor = TrillLib(1, "ring", 0x38)
    ringSensor.setPrescaler(3)
    ringSensor.readTrill()
    ry = 200 ; rx = 200
    # set up halo ring
    halo = []
    xc = rx ; yc = ry ; r = 150
    thInc = (2* 3.142) / 24.0
    ang = -thInc
    for i in range(24) : # center of halo LED
        ang += thInc
        xp = xc + r*math.cos(ang) ; yp = yc + r*math.sin(ang)
        halo.append((int(xp), int(yp)))
    energy = 24
    lastRingTouch = 0
    changeCyl = False
    cylinderNumber = 0 # initial cylinder to play
    cylNames = ["blue_danube", "baa_baa", "green_sleeves", "god_save", "bach_air",
                "lullaby", "rock-a-bye", "twinkle"]
    loadCylinder(cylinderNumber)

def changeCylinder():
    global cylinderNumber, changeCyl
    oldCyl = cylinderNumber
    cylinderNumber += 1
    if cylinderNumber >= len(cylNames) : cylinderNumber = 0 # wrap round
    #print("cylinder number is now", cylinderNumber)
    pygame.display.set_caption("Cylinder - " + cylNames[cylinderNumber])
    while ringSensor.getNumTouches() > 1:
        time.sleep(0.2)
        ringSensor.readTrill()
    if oldCyl != cylinderNumber : changeCyl = True    

def loadCylinder(number):
    global tempo, tunePointer, tune, startTime, changeCyl
    nameF = open("cylinders/" + cylNames[number] + ".cyl","r") # cylinder file - with notes in it
    tune = []
    for i in nameF.readlines():
       n = i[:-1] # remove CR at end of name
       t, p, v = n.split(',') # separate the three numbers on each line
       if v != "0" : tune.append((t, p, v)) # time, pitch, velocity           
    nameF.close()   
    pygame.display.set_caption("Music Box - " + tune[0][0])
    for i in range(1, len(tune)): # check range of notes
        if int(tune[i][1]) > 84 or int(tune[i][1]) < 35:
            print("note value of", int(tune[i][1]), " is outside the range 35 to 84 at time", tune[i][0])                                      
    tempo = float(tune[0][1]) # set speed
    tunePointer = 1
    changeCyl = False
    startTime = time.time()
    #print(tune)
  
def drawScreen():
    global addressRect, resetBaseRect, thresNumRect, valueRect, resetBaseRect
    global addressRect
    screen.fill(backCol)
    updateRingTouch()
    updateHalo(0)
    
def updateHalo(drain):
    global energy
    for i in range(24) :
        left = constrain(energy - i, 0, 144) // 24
        if i <= energy - 1: pygame.draw.circle(screen, colours[left+1], halo[i], 12, 0)
        else: pygame.draw.circle(screen, colours[0], halo[i], 12, 0)
    if energy > 0 : energy -= drain
    for i in range(24) : # draw outline
        pygame.draw.circle(screen, trillCol, halo[i], 12, 1)
    pygame.display.update()    

def drawRing():
    pygame.draw.circle(screen, trillCol, (rx, ry), 126, 0)
    pygame.draw.circle(screen, backCol, (rx, ry), 68, 0)
    
def updateRingTouch():
    global lastRingTouch, energy    
    #draw ring
    pygame.draw.circle(screen, trillCol, (rx, ry), 126, 0)
    pygame.draw.circle(screen, backCol, (rx, ry), 68, 0)
    if ringSensor.getNumTouches() !=0:                
        th = (2* 3.142) / 24
        xc = rx ; yc = ry ; r = 96
        ang = ringSensor.touchLocation(0) * 24 * th
        xp = xc + r*math.cos(ang) ; yp = yc + r*math.sin(ang)
        pygame.draw.circle(screen, colours[1], (int(xp), int(yp)), 12, 0)        
        if lastRingTouch != int(ringSensor.touchLocation(0) * 24):
            lastRingTouch = int(ringSensor.touchLocation(0) * 24)
            if energy < 143: energy += 1
    pygame.display.update()
    
def drawWords(words, x, y, col, backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect
   
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def terminate(): # close down the program
    global ringSensor
    del ringSensor # delete the class instance
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)

def checkForEvent():
    global energy 
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
        if event.key == pygame.K_ESCAPE :
            terminate()
        if event.key == pygame.K_w :
            energy = 143
        if event.key == pygame.K_c :
            changeCylinder()    
        if event.key == pygame.K_SPACE :
            pass 
            #os.system("scrot")          
                
# Main program logic:
if __name__ == '__main__':    
    main()

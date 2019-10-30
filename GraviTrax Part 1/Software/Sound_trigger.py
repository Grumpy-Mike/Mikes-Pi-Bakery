#!/usr/bin/env python3
# GraviTrax Sound Trigger
# By Mike Cook September 2019

import time
import pygame
import os
import RPi.GPIO as io

pygame.init()
pygame.display.set_caption("GraviTrax Sound Trigger")
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.mixer.quit()
pygame.mixer.init(frequency = 22050, size =- 16, channels = 2, buffer = 512)   
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN,
                          pygame.MOUSEBUTTONUP]
                         )
textHeight=18
font = pygame.font.Font(None, textHeight)
backCol = (160, 160, 160) ; lineCol = (128, 128, 0)
hiCol = (0, 255, 255) 

def main():
    global screen, lastIn, rows
    initIO()
    rows = len(inPins)
    screen = pygame.display.set_mode([390, 34 + 40*rows], 0, 32)
    init() ; pendPlay = [0]*rows
    nowIn = [0]*rows; pendTime = [0.0]*rows
    drawScreen()
    while True:  # repeat forever
        checkForEvent()
        for i in range(0, rows):
            nowIn[i] = io.input(inPins[inPin[i]])
            if lastIn[i] != nowIn[i]:
                lastIn[i] = nowIn[i]
                tmatch = trigNum[i]-1  # match trigger
                if tmatch == 2:
                    tmatch = nowIn[i] 
                if trigNum[i] != 0 and nowIn[i] == tmatch:
                    pendPlay[i] = soundFX[soundNumber[i]]            
                    pendTime[i] = time.time() + delayTime[i]
        for i in range(0, rows):  # check what to play now
            if pendTime[i] > 0.0 and time.time()>=pendTime[i]:
                pendPlay[i].play() ; pendTime[i] = 0.0         
    
def init():
    global incRect, decRect, icon, decRect, voiceRect 
    global inPin, soundNumber, delayTime, triggerRect
    global lastIn, trigNum, trigIcon   
    lastIn = [0]*rows
    loadResources()
    icon=[pygame.image.load("icons/"+str(i)+".png").convert_alpha()
                            for i in range(0,2)
          ]      
    incRect = [pygame.Rect((0,0),(15,15))]*rows*3
    decRect = [pygame.Rect((0,0),(15,15))]*rows*3
    for j in range(0,3):
        for i in range(0, rows):
            incRect[i+j*rows] = pygame.Rect((76 + j*80, 30 + i*40),(15, 15))
            decRect[i+j*rows] = pygame.Rect((76 + j*80, 50 + i*40),(15, 15))
    triggerRect = [pygame.Rect((0, 0), (20, 20))]*rows
    trigNum = [0]*rows
    trigIcon = [pygame.image.load("icons/trig"+str(i)+".png").convert_alpha()
                                  for i in range(0,4)
               ]
    voiceRect = [pygame.Rect((0,0), (15,15))]*rows
    for i in range(0, rows):
        triggerRect[i] = pygame.Rect((10, 36 + 40*i,20, 20))
        voiceRect[i] = pygame.Rect((268, 39 + i*40),(100, 20))
    sounds = rows + len(soundNames)   
    inPin = [1]*rows ; soundNumber = [0]*sounds
    for i in range(0, rows):
        inPin[i] = i
    for i in range(0, len(soundNames)):  
        soundNumber[i] = i             
    delayTime = [0.0]*rows

def initIO():
    global inPins
    inPins = [24, 23, 22, 27, 17, 4, 15, 14]
    io.setmode(io.BCM); io.setwarnings(False)    
    io.setup(inPins, io.IN, pull_up_down = io.PUD_UP)    

def loadResources():
    global soundFX, soundNames
    soundNames = ["owl", "Breaking Glass", "ComputerBeeps1",
                 "CymbalCrash", "Fairydust", "Dog1", "Zoop", "Ya", "Pop"
                  ]
    soundFX = [pygame.mixer.Sound("sounds/"+ soundNames[effect]+".wav")
                                  for effect in range(0,len(soundNames))
              ]
  
def drawScreen():
    screen.fill(backCol)
    for i in range(0,len(incRect)):  # increment / decrement icons
        screen.blit(icon[0], (incRect[i].left,incRect[i].top))
        pygame.draw.rect(screen, lineCol, incRect[i],1)
        screen.blit(icon[1], (decRect[i].left, decRect[i].top))
        pygame.draw.rect(screen, lineCol, decRect[i], 1)  
    for i in range(0,rows):  # draw all triggers
        screen.blit(trigIcon[trigNum[i]], (triggerRect[i].left,
                                           triggerRect[i].top)
                    )  
    drawWords("Trigger", 5, 8, (0, 0, 0), backCol)
    drawWords("GPIO", 70, 8, (0, 0, 0), backCol)
    drawWords("Delay", 138, 8, (0, 0, 0), backCol)
    drawWords("Sound", 218, 8, (0, 0, 0), backCol)
    updateValues()    

def updateValues():
    for i in range(0,rows): 
        drawWords(str(inPins[inPin[i]]) + "   ", 48, 39 + i*40, (0, 0, 0),
                  backCol
                  )
        drawWords("  " + str(round(delayTime[i], 1)) + "   ", 112, 39 + i*40,
                  (0, 0, 0), backCol
                  )        
        pygame.draw.rect(screen, backCol, voiceRect[i], 0)
        drawWords(str(soundNames[soundNumber[i]]), 270, 39 + i*40, (0, 0, 0),
                  backCol
                  )
    pygame.display.update()

def drawWords(words, x, y, col, backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x  # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def handleMouse(pos):  # look at mouse down
    global pramClick, pramInc, trigClick
    #print(pos) 
    trigClick = -1
    for i in range(0, rows):
        if triggerRect[i].collidepoint(pos) :
            trigClick = i
            pygame.draw.rect(screen, hiCol, triggerRect[i], 0)
            pygame.display.update()
    pramClick = -1
    pramInc = 0
    for i in range(0, len(incRect)):
      if incRect[i].collidepoint(pos):
         pramClick = i ; pramInc = 1         
         pygame.draw.rect(screen, hiCol, incRect[pramClick], 1)
         pygame.display.update()
    for i in range(0, len(decRect)):
        if decRect[i].collidepoint(pos):
            pramClick = i ; pramInc = -1         
            pygame.draw.rect(screen, hiCol, decRect[pramClick], 1)
            pygame.display.update()
       
def handleMouseUp(pos):  # look at mouse up
    global soundNumber, delayTime, inPin
    if trigClick != -1:
     trigNum[trigClick] += 1
     if trigNum[trigClick] > 3:
         trigNum[trigClick] = 0
     pygame.draw.rect(screen, backCol, triggerRect[trigClick], 0)
     screen.blit(trigIcon[trigNum[trigClick]], (triggerRect[trigClick].left,
         triggerRect[trigClick].top))
     updateValues()
    if pramClick != -1: 
        if pramClick < rows:  # GPIO Coloumn
            inPin[pramClick] += pramInc
            inPin[pramClick] = constrain(inPin[pramClick], 0, rows-1)
        elif pramClick < rows*2:  # Delay Coloumn
            delayTime[pramClick-rows] += (pramInc / 10)
            delayTime[pramClick-rows] = constrain(delayTime[pramClick - rows],
                                                  0, 5
                                                  )
            if delayTime[pramClick - rows] < 0.01:
                delayTime[pramClick - rows] = 0
        elif pramClick < rows*3:  # Sound coloum
            soundNumber[pramClick - rows*2] += pramInc
            soundNumber[pramClick - rows*2] = constrain(soundNumber[pramClick
                - rows*2], 0, len(soundNames)-1)
        if pramInc !=0:
            if pramInc < 0:
                screen.blit(icon[1], (decRect[pramClick].left,
                    decRect[pramClick].top))
                pygame.draw.rect(screen, lineCol, decRect[pramClick],1)
            else:   
                screen.blit(icon[0], (incRect[pramClick].left,
                    incRect[pramClick].top))
                pygame.draw.rect(screen, lineCol, incRect[pramClick], 1)
            updateValues()

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def terminate():  # close down the program
    pygame.mixer.quit()
    pygame.quit()  # close pygame
    os._exit(1)
   
def checkForEvent():  # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
        terminate()
    if event.type == pygame.KEYDOWN :
        if event.key == pygame.K_ESCAPE :
            terminate()
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())                  
            
if __name__ == '__main__':
    main()

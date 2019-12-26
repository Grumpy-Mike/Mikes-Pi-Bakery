#!/usr/bin/env python
# TraxScript
# By Mike Cook November 2019

import Neo_Thread as ws
import FL3731_Thread as fl
import RPi.GPIO as io
from copy import deepcopy
from tkinter import filedialog
from tkinter import *
import pygame
import time
import sys
import os
root = Tk()

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("GraviTrax Script player")
screen = pygame.display.set_mode([320,40], 0, 32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size = -16,
                  channels = 2, buffer = 512)   
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT,
                          pygame.MOUSEBUTTONDOWN,
                          pygame.MOUSEBUTTONUP]
                         )
textHeight=24 ; black = (0, 0, 0)
font = pygame.font.Font(None, textHeight)
backCol = (120, 120, 120) ; lineCol = (196, 196, 0)

ws.initIO()
fl.initI2C()

def main():
    initIO()
    loadResources()
    drawScreen()
    getFile()
    loadFile(scriptName)
    setupScript()    
    while 1 :
        traxRun()
    
def initIO():
    global inPins, restartRec, loadRect, stopScript 
    inPins = [17, 24, 23, 4, 5, 6, 13, 19, 26, 12, 16,
              20]
    io.setmode(io.BCM); io.setwarnings(False)    
    io.setup(inPins, io.IN, pull_up_down = io.PUD_UP)
    restartRec = pygame.Rect((238,7),(66,23))
    loadRect = pygame.Rect((10,7),(97,23))
    stopScript = 0

def loadResources():
    global soundFX, soundNames
    soundNames = ["owl", "Breaking Glass",
                  "ComputerBeeps1", "CymbalCrash",
                  "Fairydust", "Dog1", "Zoop", "Ya",
                  "Pop", "Duck", "Gong", "Laser1",
                  "Laser2", "running", "Screech",
                  "SpaceRipple", "Zoop", "Dog2",
                  "DirtyWhir", "ComputerBeeps2",
                  "AlienCreak2", "AlienCreak1"
                  ]
    soundFX = [pygame.mixer.Sound("sounds/"
                                  + soundNames[effect]
                                  + ".wav")
                                  for effect in range(
                                  0, len(soundNames))
              ]

def getFile():
    global scriptName, root
    success = False
    while not success:
        root.withdraw()
        scriptName = filedialog.askopenfilename(
            initialdir = "/home/pi",
            title = "Select GraviTrax script",
            filetypes = (("txt files", "*.txt"),
            ("all files", "*.*")))        
        if ".txt" in scriptName :
            success = True
        else :
            print("not a valid text file")
       
def loadFile(fileName):
    global thingsToDo
    nameF = open(fileName, "r")
    thingsToDo = nameF.readlines()
    nameF.close()

def setupScript():
    global pinToWatch, changeToMonitor, soundToPlay
    global actionDelay, wsToPlay, flToPlay, pendTime
    global nowIn, lastIn, trigNum, monitor, pendPlay
    pinToWatch = []
    changeToMonitor = []
    soundToPlay = []
    actionDelay = []
    wsToPlay = [] ; flToPlay = []
    print("\nloading the script", len(thingsToDo),
          "lines")
    for move in range(0,len(thingsToDo)):
        line = str(thingsToDo[move])
        now = False
        for val in line.split(","):
            if "when" in val:
                pin = int(val[-2:])
                if not(pin in inPins) :
                    print("Pin",pin,"is not valid")
                pinToWatch.append(pin)
            elif"now" in val:
                now = True
            elif "falls" in val and not now:
                changeToMonitor.append(1)
            elif "rises" in val and not now:
                changeToMonitor.append(2)
            elif "changes" in val and not now:
                changeToMonitor.append(3)
            elif "delay" in val and not now:                
                actionDelay.append(float(val[-3:]))
            elif "sound" in val or "ws" in val or "fl" in val:
                pram = int(val[-2:])
                if "sound" in val:
                    if not now:
                        soundToPlay.append(pram)
                        wsToPlay.append(-1)
                        flToPlay.append(-1)
                    else:
                       soundFX[pram].play() 
                elif "ws" in val:
                    if not now:
                        soundToPlay.append(-1)
                        wsToPlay.append(pram)
                        flToPlay.append(-1)
                    else:
                        ws.startWs2812Thread(pram)
                elif "fl" in val:
                    if not now:
                        soundToPlay.append(-1)
                        wsToPlay.append(-1)
                        flToPlay.append(pram)
                    else:
                        fl.startFL3731Thread(pram)
            checkForEvent()
    '''        
    print("pin", pinToWatch)
    print("change", changeToMonitor)
    print("delay", actionDelay)
    print("sound", soundToPlay)
    print("ws animation", wsToPlay)
    print("fl animation", flToPlay)
    '''
    monitor = len(pinToWatch)
    nowIn = [0] * monitor
    lastIn = [0] * monitor
    pendPlay = [0] * monitor
    pendTime = [0.0] * monitor
    for i in range(0, monitor):
        lastIn[i] = io.input(pinToWatch[i])
    print("Current pin states",lastIn)    

def traxRun():
    global nowIn, lastIn, stopScript 
    while stopScript == 0 : 
        checkForEvent()
        for i in range(0, monitor):
            nowIn[i] = io.input(pinToWatch[i])
            if lastIn[i] != nowIn[i] :
                #print("Current pin states", lastIn)
                lastIn[i] = nowIn[i]
                tmatch = changeToMonitor[i]-1  # match
                if tmatch == 2:
                    tmatch = nowIn[i]
                if changeToMonitor[i] != 0 and nowIn[i] == tmatch:
                    if soundToPlay[i] != -1 :
                        pendPlay[i] = soundToPlay[i]
                    if wsToPlay[i] != -1 :
                        pendPlay[i] = wsToPlay[i] 
                    if flToPlay[i] != -1 :
                        pendPlay[i] = flToPlay[i]                         
                    pendTime[i] = time.time() + actionDelay[i]      
        for i in range(0, monitor):  # what to play now
            if pendTime[i] > 0.0 and time.time() >= pendTime[i]:
                if soundToPlay[i] != -1 : 
                    soundFX[soundToPlay[i]].play()
                if wsToPlay[i] != -1 :
                    ws.startWs2812Thread(wsToPlay[i])
                if flToPlay[i] != -1 :
                    if flToPlay[i] == 99 : # stop clock
                        fl.stopCount()
                    else:    
                        fl.startFL3731Thread(flToPlay[i])   
                pendTime[i] = 0.0
    if stopScript == 1 :        
        getFile()
        loadFile(scriptName)    
    setupScript()
    stopScript = 0
                    
def drawScreen():
    screen.fill(backCol)
    pygame.draw.rect(screen, lineCol, loadRect, 1)
    pygame.draw.rect(screen, lineCol, restartRec, 1)  
    drawWords("Load script", 14, 8, black, backCol)
    drawWords("Restart", 244, 8, black, backCol)
    pygame.display.update()

def drawWords(words, x, y, col, backCol) :
    textSurface = font.render(words, True, col,
                              backCol)
    textRect = textSurface.get_rect()
    textRect.left = x  # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def handleMouseDown(pos):  # look at mouse down
    if loadRect.collidepoint(pos) :
        pygame.draw.rect(screen, lineCol, loadRect, 0)  
    elif restartRec.collidepoint(pos) :
        pygame.draw.rect(screen, lineCol,
                         restartRec, 0)
    pygame.display.update()    

def handleMouseUp(pos):  # look at mouse up
    global stopScript
    if loadRect.collidepoint(pos) :
        stopScript = 1   
    if restartRec.collidepoint(pos) :
        stopScript = 2           
    drawScreen()
    
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def terminate():  # close down the program
    global root
    root.destroy
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
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())        
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouseDown(pygame.mouse.get_pos())        
            
if __name__ == '__main__':
    main()
    

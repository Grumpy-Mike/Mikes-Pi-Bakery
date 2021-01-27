#!/usr/bin/env python3
# Graphic Trill by Mike Cook December 2020
# shows touch positions and mode data for all types of sensor
# shows touch size for the bar sensor

import time
import os
import pygame
from trill_lib import TrillLib
import math
import colorsys

def main():
    init()
    findSensors()
    drawScreen()
    updatePrams()
    beingTouched = False
    while 1:
        checkForEvent()
        time.sleep(0.05) # 20 times a second
        trillSensor.readTrill()
        updateValues()       
            
def init():
    global screen, typeRect, modeRect, textHeight, font, speedRect
    global rawRect, bitsRect, prescaleRect, currentBits, currentSpeed 
    global lineCol, hiCol, backCol, colours, clearRect, tick
    global trillType, currentPrescale, trillCol, currentMode, modeTypes
    global incRect, decRect, inc, dec, thresNumRect, thresNum, addr
    global valueRect, resetBaseRect, addressRect, textCol, craftRect
    global craftCol, gTouchVerticalLocations, gTouchHorizontalLocations
    global gTouchSize, vt , ht 

    colours = [(255, 0, 0), (255, 170, 0),
              (0, 255, 0), (0, 168, 255), (172, 0, 255) ]
    craftCol = []
    for i in range(101):
        c = colorsys.hsv_to_rgb(i / 100, 0.6 + i / 340, 1.0)
        craftCol.append((int(c[0] * 255), int(c[1] *255), int(c[2] * 255)))
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT,
                              pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP])
    pygame.display.set_caption("Graphic Trill")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    sWide = 900 ; sHigh = 360
    padCo = (sWide//2 - 100, 48) # top of screen
    screen = pygame.display.set_mode([sWide,sHigh],
                                     0, 32)
    textHeight=24 ; font = pygame.font.Font(None, textHeight)
    tick =pygame.image.load("icons/tick.png").convert_alpha()
    inc = pygame.image.load("icons/0.png").convert_alpha()
    dec = pygame.image.load("icons/1.png").convert_alpha()
    typeRect = [] ; modeRect = [] ;  prescaleRect = []  
    bitsRect = [] ; speedRect = [] ; craftRect = []  
    incRect = pygame.Rect((486,137),(15,15))
    decRect = pygame.Rect((516,137),(15,15))
    for i in range(0,5):
        typeRect.append(pygame.Rect((41 + i*60, 300),(15,15)))
    for i in range(0,4):
        modeRect.append(pygame.Rect((360 + i*100, 300),(15,15)))
    for i in range(0,8):
        prescaleRect.append(pygame.Rect((438 + i*30, 38),(15,15)))
    for i in range(0,8):
        bitsRect.append(pygame.Rect((473 + i*30, 84),(15,15)))
    for i in range(0,4):
        speedRect.append(pygame.Rect((758 + i*30, 38),(15,15)))
    for j in range(5):    
        for i in range(6):
            craftRect.append(pygame.Rect((50 + i* 42, 21 + j* 52), (25,25)))
    clearRect = pygame.Rect((0,0),(334,273))
    rawRect = pygame.Rect((338,160),(338,101))
    lineCol = (0,128,255) ; backCol = (160,160,160)
    hiCol = (0,255,255) # highlight colour
    modeTypes = ["CENTROID", "RAW", "BASELINE", "DIFF"]
    trillType = ["none", "bar", "square", "craft", "ring", "hex"]
    currentMode = 0 ; currentPrescale = 2 
    currentBits = 12 ; currentSpeed = 0    
    # dummy rectangles for screen draw to define
    thresNumRect = pygame.Rect((0, -84),(15,15))
    valueRect = pygame.Rect((0, -84),(15,15))
    addressRect = pygame.Rect((0, -84),(15,15))
    resetBaseRect = pygame.Rect((0, -84),(15,15))
    thresNum = 10 # default value
    gTouchVerticalLocations = [0.0, 0.0, 0.0, 0.0]
    gTouchHorizontalLocations = [0.0, 0.0, 0.0, 0.0]
    gTouchSize = [0.0, 0.0, 0.0, 0.0]
    vt = 0
    ht = 0
    trillCol = (32, 32, 32) ; textCol = (0, 0, 0)

def findSensors():
    global trillSensor, attachedSensors, availableSensors, currentType, addr
    attachedSensors = []
    availableSensors = []
    for device in range(0x20, 0x41) : # look at all possible addresses 
        test = TrillLib(1, "none", 256)
        if test.testForI2CDevice(device, 0, 1): # a device is found
            #print("Device found at address", hex(device))
            del test
            test = TrillLib(1, "none", device) # initialise with valid address
            testType = test.getTypeNumber()
            #print("Device identifies as", testType, trillType[testType])
            attachedSensors.append([trillType[testType], device])
            availableSensors.append(testType)
        del test
    currentType = availableSensors[0]
    initNewSensor(0, attachedSensors[0][0] in trillType) # first sensor found
    trillSensor.printDetails()    

def changeSensor(new):
    global trillSensor, currentType, addr
    del trillSensor # remove old instance of trill
    if new == currentType :
        if entryValue + 1 < len(attachedSensors) and trillType[currentType] == availableSensors[entryValue + 1]:
            initNewSensor(entryValue + 1, currentType)
            return
    i = 0
    while( i < len(attachedSensors)): # search for new sensor type
        if attachedSensors[i][0] == trillType[new] :
            i = initNewSensor(i, new)
        else: i += 1    

def initNewSensor(i, newSensor) :
    global trillSensor, currentType, addr, entryValue, currentMode
    trillSensor = TrillLib(1, attachedSensors[i][0], attachedSensors[i][1])
    addr = attachedSensors[i][1]
    currentType = availableSensors[i]
    entryValue = i # the entry in the scanned list we found
    if currentType == 3 : currentMode = 3
    trillSensor.setMode(modeTypes[currentMode])
    trillSensor.setPrescaler(currentPrescale) 
    trillSensor.setScanSettings(currentSpeed, currentBits)
    updateThreshold()
    trillSensor.updateBaseLine()
    updatePrams() # change address
    updateType() # tick in right box
    pygame.display.update()
    trillSensor.readTrill()
    return len(attachedSensors) # exit while loop

def drawScreen():
    global addressRect, resetBaseRect, thresNumRect, valueRect, resetBaseRect
    global addressRect
    screen.fill(backCol)
    updateType() # draw chose type & mode rectangles        
    drawWords("bar", 35, 275, textCol, backCol)
    drawWords("square", 80, 275, textCol, backCol)
    drawWords("craft", 150, 275, textCol, backCol)
    drawWords("ring", 213, 275, textCol, backCol)
    drawWords("hex", 275, 275, textCol, backCol)
    drawWords("CENTROID" ,330, 275,textCol, backCol)
    drawWords("RAW", 446, 275, textCol, backCol)
    drawWords("BASELINE", 524, 275, textCol, backCol)
    drawWords("DIFF", 646, 275, textCol, backCol)
    drawWords("Trill Sensor Type", 90, 326, textCol, backCol)
    drawWords("Trill Operating Mode", 420, 326,textCol, backCol)
    drawWords("Sensor address", 342, 11, textCol, backCol)
    resetBaseRect = drawWords("Reset baseline", 677, 11, textCol, backCol)
    resetBaseRect.inflate_ip(8,4)
    pygame.draw.rect(screen,lineCol,resetBaseRect, 1)
    addressRect = drawWords(str(hex(attachedSensors[0][1])), 474, 11, textCol, backCol)
    addressRect.inflate_ip(8,4)
    drawWords("Noise threshold", 346, 135,textCol, backCol)
    drawWords("Number", 540, 135, textCol, backCol)
    thresNumRect = drawWords(str(thresNum), 611, 135, textCol, backCol)
    thresNumRect.inflate_ip(8,4)
    drawWords("Value", 660, 135, textCol, backCol)
    valueRect = drawWords("1", 717, 135, textCol, backCol)
    valueRect.width = 183
    valueRect.inflate_ip(8,4)
    drawWords("Prescaler", 346, 37, textCol, backCol)
    for i in range(1,9):
        drawWords(str(i), 442 + (i-1) *30, 55, textCol, backCol)
    drawWords("Number of bits", 346, 84, textCol, backCol)
    for i in range(9,17):
        drawWords(str(i), 474 + (i-9) *30, 106, textCol, backCol)
    drawWords("Speed", 690, 37, textCol, backCol)
    drawWords("Fast", 748, 55, textCol, backCol)
    drawWords("Slow", 840, 55, textCol, backCol)
    updateThreshold()
    updateValues()

def updateValues():
    global gTouchSize, vt, ht, gTouchHorizontalLocations, gTouchVerticalLocations 
    pygame.draw.rect(screen, backCol, clearRect, 0) # clear drawing area
    pygame.draw.rect(screen, backCol, rawRect, 0) # clear graph area
    
    if currentMode == 0 : # is it CENTROID mode
        if currentType == 1: #draw bar
            pygame.draw.rect(screen,trillCol, (41, 106, 252, 65), 0)
            if trillSensor.getNumTouches() !=0:
                for t in range(trillSensor.getNumTouches()) :
                    dis = constrain(52 + trillSensor.touchLocation(t) * 230, 52, 282)
                    #size = int((trillSensor.touchSize(t))* 5 + 2) // 16
                    size = int((trillSensor.touchSize(t)) + 2)
                    if size > 33 : size = 33
                    #print(size)
                    pygame.draw.circle(screen, colours[t], (int(dis), 138), size, 0)
            
        if currentType == 2 or currentType == 5: #draw square or hex
            if currentType == 2 :
                pygame.draw.rect(screen,trillCol, (41, 11, 252, 252), 0)
            else: # draw hex
                pygame.draw.polygon(screen, trillCol, [(216, 243), (94, 243),
                (33, 137), (94, 31), (216, 31), (277, 137), (216, 243)], 0)
            vt = trillSensor.getNumTouches()
            ht = trillSensor.getNumHorizontalTouches()
            if vt > 4 : vt = 4
            if ht > 4 : ht = 4
            # set all locations and size to zero
            for i in range(0, 4):
                gTouchVerticalLocations[i] = 0.0
                gTouchSize[i] = 0.0
                gTouchHorizontalLocations[i] = 0.0
            for i in range(ht):
                gTouchHorizontalLocations[i] = trillSensor.touchHorizontalLocation(i)
            #print("H location",gTouchHorizontalLocations)
            for i in range(vt):
                gTouchVerticalLocations[i] = trillSensor.touchLocation(i) 
                gTouchSize[i] = trillSensor.touchSize(i)
            #print("V location", gTouchVerticalLocations)                
            if vt !=0 and ht !=0:
                j = 0 ; k = 0
                big = ht
                if vt > big: big = vt
                for t in range(big+1) :                  
                    if j >= ht : j = 0
                    if k >= vt : k = 0
                    disY = constrain(24 + (gTouchHorizontalLocations[j] * 230), 24, 250)
                    disX = constrain(52 + (gTouchVerticalLocations[k] * 228 ), 52, 282)
                    pygame.draw.circle(screen, colours[t], (int(disX), int(disY)), 12, 0)
                    j += 1 ; k += 1
                    
        if currentType == 4: #draw ring
            pygame.draw.circle(screen, trillCol, (167, 137), 126, 0)
            pygame.draw.circle(screen, backCol, (167, 137), 68, 0)
            if trillSensor.getNumTouches() !=0:                
                th = (2* 3.142) + 0.1
                xc = 167 ; yc = 137 ; r = 96
                for t in range(trillSensor.getNumTouches()) :
                    ang = trillSensor.touchLocation(t) * th
                    xp = xc + r*math.cos(ang) ; yp = yc + r*math.sin(ang)
                    pygame.draw.circle(screen, colours[t], (int(xp), int(yp)), 12, 0)
    else : # Draw graph
        pygame.draw.rect(screen, trillCol, rawRect, 1) # clear graph area        
        for i in range(trillSensor.getNumChannels()):
            v = trillSensor.rawData[i]
            pygame.draw.rect(screen, craftCol[int(v*100)], (345 + 10*i, 260, 8, int(-v*100)), 0)
        if currentType == 3 and currentMode == 3: #draw craft when in DIF mode
            for i in range(30):
               pygame.draw.rect(screen, trillCol, craftRect[i], 0)
               v = trillSensor.rawData[i] * 100
               if v > 1:
                   pygame.draw.circle(screen, craftCol[int(v)], (craftRect[i].left+12, craftRect[i].top+12), 10, 0)    
    
    pygame.display.update()

def updateThreshold():
    pygame.draw.rect(screen, backCol, thresNumRect, 0)
    pygame.draw.rect(screen, backCol, valueRect, 0)
    drawWords(str(thresNum), 611, 135, textCol, backCol)
    drawWords(str(thresNum/(1 << currentBits)), 717, 135, textCol, backCol)
    trillSensor.setNoiseThreshold(thresNum / (1 << currentBits))
    
def updateType() :    
    for i in range(5): # draw choose type rectangles
        pygame.draw.rect(screen, backCol, typeRect[i], 0)
        if i+1 in availableSensors:
            pygame.draw.rect(screen, lineCol, typeRect[i], 1)
        else:
            pygame.draw.rect(screen,(255, 255, 255),typeRect[i],1)
        if i == currentType-1 :
            screen.blit(tick,(typeRect[i].left,typeRect[i].top))
    for i in range(4): # draw choose mode rectangles
        pygame.draw.rect(screen, backCol, modeRect[i], 0)
        pygame.draw.rect(screen, lineCol, modeRect[i], 1)
        if i == currentMode :
            screen.blit(tick,(modeRect[i].left,modeRect[i].top))
    for i in range(8): # draw prescale rectangles
        pygame.draw.rect(screen, backCol, prescaleRect[i], 0)
        pygame.draw.rect(screen, lineCol, prescaleRect[i], 1)
        if i == currentPrescale -1 :
            screen.blit(tick,(prescaleRect[i].left, prescaleRect[i].top))
    for i in range(8): # draw bits rectangles
        pygame.draw.rect(screen, backCol, bitsRect[i], 0)
        pygame.draw.rect(screen, lineCol, bitsRect[i], 1)
        if i == currentBits - 9 :
            screen.blit(tick,(bitsRect[i].left, bitsRect[i].top))
    for i in range(4): # draw speed rectangles
        pygame.draw.rect(screen, backCol, speedRect[i], 0)
        pygame.draw.rect(screen, lineCol, speedRect[i], 1)
        if i == currentSpeed :
            screen.blit(tick,(speedRect[i].left, speedRect[i].top))
    pygame.draw.rect(screen, lineCol, incRect, 1)
    screen.blit(inc,(incRect.left, incRect.top))
    pygame.draw.rect(screen, lineCol, decRect, 1)
    screen.blit(dec,(decRect.left, decRect.top))

def updatePrams(): #  update parameters
    pygame.draw.rect(screen, backCol, addressRect, 0) # sensor address
    drawWords(str(hex(addr)), 474, 11, textCol, backCol)
    
def drawWords(words, x, y, col, backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect
   
def handleMouse(pos): # look at mouse down
    global currentType, currentMode, currentPrescale, currentBits
    global currentSpeed, thresNum
    #print(pos)
    if resetBaseRect.collidepoint(pos):
        pygame.draw.rect(screen,(0, 180, 0), resetBaseRect,1)
    for i in range(5):
        if typeRect[i].collidepoint(pos) and i + 1 in availableSensors:
            changeSensor(i + 1) # set the current type to this new one
            print("current type", currentType)
            #updateType() # draw chose type rectangles
            #updateValues()
    for i in range(4):
        if modeRect[i].collidepoint(pos):
            currentMode = i 
            updateType() # draw chose mode rectangles
            trillSensor.setMode(modeTypes[currentMode])
            trillSensor.readTrill() # get fresh data
            updateValues()
    for i in range(8):
        if prescaleRect[i].collidepoint(pos):
            currentPrescale = i + 1
            trillSensor.setPrescaler(currentPrescale)
            trillSensor.updateBaseLine()
            updateType() # draw chose type rectangles
            updateValues()
    for i in range(8):
        if bitsRect[i].collidepoint(pos):
            currentBits = i + 9
            trillSensor.setScanSettings(currentSpeed, currentBits)
            updateThreshold()
            trillSensor.updateBaseLine()
            #trillSensor.readTrill()
            updateType() # draw chose type rectangles
            updateValues()
    for i in range(4):
        if speedRect[i].collidepoint(pos):
            currentSpeed = i
            trillSensor.setScanSettings(currentSpeed, currentBits)
            updateType() # draw chose type rectangles
            updateValues()
    if incRect.collidepoint(pos):
        thresNum += 1
        if thresNum > 255 : thresNum = 255
        updateThreshold()
    if decRect.collidepoint(pos):
        thresNum -= 1
        if thresNum < 0 : thresNum = 0
        updateThreshold()
                               
def handleMouseUp(pos): # look at mouse up
    global mute
    if resetBaseRect.collidepoint(pos):
        pygame.draw.rect(screen,lineCol, resetBaseRect,1)
        trillSensor.updateBaseLine()
        pygame.display.update()

def pointsForHex():
    xc = 155 ; yc = 137 ; thInc = (2* 3.142) / 6 ; th = thInc
    xp = [] ; yp = [] ; r = 122
    for point in range(7):
        xp.append(xc + r*math.cos(th)) ; yp.append(yc + r*math.sin(th))
        if point > 0 : pygame.draw.line(screen,trillCol, (xp[point-1], yp[point-1]) , (xp[point], yp[point]), 1)
        print(xp[point], yp[point])
        th += thInc
      
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def terminate(): # close down the program
    global trillSensor
    del trillSensor # delete the class instance
    pygame.quit() # close pygame
    os._exit(1)

def checkForEvent():   
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
                
# Main program logic:
if __name__ == '__main__':    
    main()

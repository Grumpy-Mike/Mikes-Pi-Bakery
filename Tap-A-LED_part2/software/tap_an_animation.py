#!/usr/bin/env python3
# tap aimation by Mike Cook October 2020

import time
import board
import copy
import neopixel
import pygame
import os
from caltap import CalTap
from tkinter import filedialog
from tkinter import *

def main():
    global animateRun, timeInterval, currentFrame
    print("Tap to change an LED")
    init()
    drawScreen()
    startTime = time.time()
    timeInterval = 0.5
    while 1:
        checkForEvent()
        if animateRun and time.time() - startTime > timeInterval:
            startTime = time.time()
            currentFrame += 1
            if currentFrame >= maxFrame : currentFrame = 0
            restoreFrame(currentFrame)
            upDateFrameNumber()
            pygame.display.update()
        else :    
            tapLED()
                    
def tapLED():
    if tap.touched():
        pos = tap.getPos()
        if pos[3] : # a valid measurement
            #print("pixel", pos[2])
            if pixels[pos[2]] != bgList:
               pixels[pos[2]] = backGround # turn off
               pygame.draw.rect(screen, pixels[pos[2]], ledRect[pos[2]], 0)
               pygame.display.update()
            else:
               pixels[pos[2]] = colours[drawCol]
            pixels.show()
            pygame.draw.rect(screen, pixels[pos[2]], ledRect[pos[2]], 0)
            pygame.display.update()
            while tap.touched() : pass    
   
def drawScreen():
    global actionRect, frameRect, maxFrameRect 
    screen.fill(backCol)
    nextFrame = drawWords("Next frame", 20, 300, black, backCol)
    nextFrame = nextFrame.inflate(6, 4)
    pygame.draw.rect(screen, black, nextFrame, 1)
    lastFrame = drawWords("Last frame", 138, 300, black, backCol)
    lastFrame = lastFrame.inflate(6, 4)
    pygame.draw.rect(screen, black, lastFrame, 1)
    frameNum = drawWords("Frame", 246, 300, black, backCol)
    copyFrame = drawWords("Copy from last frame", 20, 340, black, backCol)
    copyFrame = copyFrame.inflate(6, 4)
    pygame.draw.rect(screen, black, copyFrame, 1)
    clearFrame = drawWords("Clear frame", 234, 340, black, backCol)
    clearFrame = clearFrame.inflate(6, 4)
    pygame.draw.rect(screen, black, clearFrame, 1)    
    frameRect = drawWords(str(currentFrame+1), 308, 300, black, backCol)
    frameRect = frameRect.inflate(6, 4)
    maxFrameRect = drawWords(" of  "+str(maxFrame),
                             frameRect[0] + frameRect[2], 300, black, backCol)
    maxFrameRect = maxFrameRect.inflate(6, 4)
    shiftLeft = drawWords("Shift left", 20, 380, black, backCol)
    shiftLeft = shiftLeft.inflate(6, 4)
    pygame.draw.rect(screen, black, shiftLeft, 1)
    shiftRight = drawWords("Shift right", 112, 380, black, backCol)
    shiftRight = shiftRight.inflate(6, 4)
    pygame.draw.rect(screen, black, shiftRight, 1)
    shiftUp = drawWords("Shift up", 216, 380, black, backCol)
    shiftUp = shiftUp.inflate(6, 4)
    pygame.draw.rect(screen, black, shiftUp, 1)
    shiftDown = drawWords("Shift down", 304, 380, black, backCol)
    shiftDown = shiftDown.inflate(6, 4)
    pygame.draw.rect(screen, black, shiftDown, 1)
    saveRect = drawWords("Save .led", 20, 420, black, backCol)
    saveRect = saveRect.inflate(6, 4)
    pygame.draw.rect(screen, black, saveRect, 1)
    loadRect = drawWords("Load .led", 112, 420, black, backCol)
    loadRect = loadRect.inflate(6, 4)
    pygame.draw.rect(screen, black, loadRect, 1)
    saveRectgif = drawWords("Save .jpg", 216, 420, black, backCol)
    saveRectgif = saveRectgif.inflate(6, 4)
    pygame.draw.rect(screen, black, saveRectgif, 1)    
    runRect = drawWords("Run", 304, 420, black, backCol)
    runRect = runRect.inflate(6, 4)
    pygame.draw.rect(screen, black, runRect, 1)
    newRect = drawWords("New animation", 20, 460, black, backCol)
    newRect = newRect.inflate(6, 4)
    pygame.draw.rect(screen, black, newRect, 1)

    actionRect = [nextFrame, lastFrame, copyFrame, clearFrame,
                  shiftLeft, shiftRight, shiftUp, shiftDown,
                  saveRect, loadRect, saveRectgif, runRect,
                  newRect]
    drawPixels()    
    drawPall()
    pygame.display.update()    

def drawPixels():
    #print("Drawing pixels")
    pygame.draw.rect(screen, black, (20, 12, 390, 210), 0)
    for i in range(128):
        pygame.draw.rect(screen, pixels[i], ledRect[i],0)
    
def drawPall() : # draw the pallette of colours
    pygame.draw.rect(screen, black, pallRect, 0)
    for i in range(len(colours)):
        pygame.draw.rect(screen, colours[i], colRect[i], 0)
        if i == drawCol :
            pygame.draw.rect(screen, black, colRect[i].inflate(-14,-14), 0)

def upDateFrameNumber():
    global frameRect, maxFrameRect
    pygame.draw.rect(screen, backCol, frameRect,0)
    pygame.draw.rect(screen, backCol, maxFrameRect,0)
    frameRect = drawWords(str(currentFrame+1), 308, 300, black, backCol)
    frameRect = frameRect.inflate(6, 4)
    maxFrameRect = drawWords(" of  "+str(maxFrame),
                             frameRect[0] + frameRect[2], 300, black, backCol)
    maxFrameRect = maxFrameRect.inflate(6, 4)
    #pygame.display.update()

def restoreRect():
    for i in range(len(actionRect)):
        pygame.draw.rect(screen, black, actionRect[i], 1)
    pygame.display.update()             

def drawWords(words, x, y, col, backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect
    
def init():
    global colours, tap, pixels, backGround, drawCol, bgList
    global backCol, black, screen, ledRect, colRect, pallRect
    global textHeight, font, currentFrame, maxFrame, animation
    global animateRun, fileName
    fileName = "/home/pi/MagPi/Tap-a-led/part_2/frames/frame.png"
    tap = CalTap()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.2 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)
    # put your own colours here
    colours = [(255, 0, 0), (255, 170, 0), (169, 255, 0),
               (0, 255, 0), (0, 255, 171), (0, 168, 255),
               (1, 0, 255), (172, 0, 255), (100, 100, 100),
               (190, 190, 190), (255, 255, 255) ]
    backGround = (8, 8, 8) ; black = (0, 0, 0)
    bgList = [backGround[0], backGround[1], backGround[2]]
    drawCol = 0
    pixels.fill(backGround)
    pixels.show()
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT,
                              pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP])

    pygame.display.set_caption("Tap-A-LED - Animation")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    sWide = 430 ; sHigh = 500
    screen = pygame.display.set_mode([sWide,sHigh],
                                     0, 32)
    textHeight=26 ; font = pygame.font.Font(None, textHeight)
    backCol = (160,160,160)
    # rectangles
    ledRect = [pygame.Rect((0,0),(20,20))]*128
    for x in range(16):
        for y in range(8):
            ledRect[y + (x * 8)] = pygame.Rect((40 + x*22, 184 - y*22),(20,20))
    colRect = [pygame.Rect((0,0),(20,20))]*len(colours)
    for i in range(len(colours)):
        colRect[i] = pygame.Rect((40 + i*22, 253), (20,20))
    pallRect = pygame.Rect((20, 248), (390, 30))
    currentFrame = 0 ; maxFrame = 0 ; animation = [] # list to hold animation
    animateRun = False

def handleMouse(pos):
    global action, drawCol
    action = -1
    #print(pos)
    if pallRect.collidepoint(pos):
       for i in range(len(colours)):
         if colRect[i].collidepoint(pos):
             drawCol = i
             drawPall()
             pygame.display.update()
    else :
        for i in range(len(actionRect)):
            if actionRect[i].collidepoint(pos):
                pygame.draw.rect(screen, (255, 170, 0), actionRect[i], 1)
                action = i
                pygame.display.update()
                
def handleMouseUp(pos):
    global action, animateRun
    if action != -1 :
        if actionRect[action].collidepoint(pos):
            # now do actions
            if action == 0 : nextFrame()
            if action == 1 : lastFrame()
            if action == 2 : restoreFrame(currentFrame - 1)
            if action == 3 : clearAll()
            if action == 4 : shiftLeft()
            if action == 5 : shiftRight()
            if action == 6 : shiftUp()
            if action == 7 : shiftDown()
            if action == 8 : savePixels()
            if action == 9 : loadPixels()
            if action == 10 : saveImages()
            if action == 11 and maxFrame > 1: animateRun = not animateRun
            if action == 12 : newAnimation()
            if action != 11 or not animateRun: # if running remove outline
                pygame.draw.rect(screen, black, actionRect[action], 1)
        else :
            print("no action")
            pygame.draw.rect(screen, black, actionRect[action], 1)
        pygame.display.update()
        
def nextFrame():
    global currentFrame, animation, pixels
    currentFrame += 1
    if currentFrame >= maxFrame :
        addFrame()
    else :
        saveFrame(currentFrame-1)
        restoreFrame(currentFrame)
        drawPixels()
    upDateFrameNumber()
    
def lastFrame():
    global currentFrame, animation, pixels
    if currentFrame != 0 :
        if currentFrame >= maxFrame :
            addFrame()
        else :    
            saveFrame(currentFrame)
        currentFrame -= 1
        restoreFrame(currentFrame)
        upDateFrameNumber()
    elif maxFrame != 0 :  # wrap round to last frame
        saveFrame(0)
        currentFrame = maxFrame - 1
        restoreFrame(currentFrame)
        upDateFrameNumber()

         

def saveFrame(n):
    animation[n] = copy.deepcopy(pixels)
    
def restoreFrame(n):
    global pixels
    if n >= 0:
        for i in range(128):
            temp = copy.deepcopy(animation[n][i])
            pixels[i] = (temp[0], temp[1], temp[2])
        drawPixels()
        pixels.show()
    
def addFrame():
    global maxFrame, animation
    maxFrame += 1
    animation.append(copy.deepcopy(pixels))

def clearAll():
    pixels.fill(backGround)
    drawPixels()
    pixels.show()

def shiftLeft():
    global pixels
    for i in range(120):
        pixels[i] = pixels[i+8]
    for i in range(120, 128):
        pixels[i] = backGround
    drawPixels()
    pixels.show()

def shiftRight():
    global pixels
    for i in range(127, 7, -1):
        #print(i)
        pixels[i] = pixels[i-8]
    for i in range(8):
        pixels[i] = backGround
    drawPixels()
    pixels.show()
    
def shiftUp():
    global pixels
    for j in range(0, 120, 8):
        for i in range(j+7, j, -1 ):
            pixels[i] = pixels[i-1]
    for i in range(0, 128, 8):
        pixels[i] = backGround
    drawPixels()
    pixels.show()

def shiftDown():
    global pixels
    for j in range(0, 127, 8):
        for i in range(j+1, j+8 ): 
            pixels[i-1] = pixels[i]
    for i in range(7, 128, 8):
        pixels[i] = backGround
    drawPixels()
    pixels.show()

def newAnimation():
    global maxFrame, currentFrame, animation
    maxFrame = 0
    currentFrame = 0
    blank = []
    animation = copy.deepcopy(blank)
    clearAll()
    animation.append(pixels)
    upDateFrameNumber()

def savePixels():
    global fileName
    root = Tk()
    path = os.path.dirname(fileName)
    root.filename = filedialog.asksaveasfilename(initialdir = path,
        title = "file to save .led animation",
        filetypes = (("animation","*.led"),
                     ("all files","*.*")))
    temp = root.filename
    root.withdraw()
    if len(temp) >3 :
        fileName = os.path.splitext(temp)[0]
        file = open(fileName + ".led", "w")
        #file.write(str(maxFrame) + "\n")
        for k in range(maxFrame):
            for i in range(0,128):
                temp = copy.deepcopy(animation[k][i])
                file.write(str(temp[0]) +"," + str(temp[1]) +"," + str(temp[2]))
                if i != 127 : file.write(",")
            file.write("\n")   
        file.close()
    
def loadPixels():
    global fileName, maxFrame, animation, currentFrame
    root = Tk()
    path = os.path.dirname(fileName)
    root.filename = filedialog.askopenfilename(initialdir = path,
        title = "file to load in .led animation",
        filetypes = (("animation","*.led"),
                     ("all files","*.*")))
    temp = root.filename
    root.withdraw()
    if len(temp) >3 :
        fileName = temp
        fileToOpen = os.path.splitext(temp)[0]
        file = open(fileToOpen + ".led", "r")        
        inLines = file.readlines()
        file.close()
        blank = []
        animation = copy.deepcopy(blank)
        maxFrame = len(inLines)
        pix = [0]*384
        for k in range(maxFrame):    
            frame = inLines[k]
            pix = frame.split(",")
            newFrame = []
            for i in range(0, 384, 3):
                led = [int(pix[i]), int(pix[i+1]), int(pix[i+2])]
                newFrame.append(led)  
            animation.append(copy.deepcopy(newFrame))
        currentFrame = 0
        restoreFrame(currentFrame)
        upDateFrameNumber()
    
def saveImages():
    global fileName
    root = Tk()
    path = os.path.dirname(fileName)
    root.filename = filedialog.asksaveasfilename(initialdir = path,
        title = "file to save .jpg frames",
        filetypes = (("frames","*.jpg"),
                     ("all files","*.*")))
    temp = root.filename
    root.withdraw()
    if len(temp) >3 :
        fileName = os.path.splitext(temp)[0]
        for i in range(0, maxFrame) :
            restoreFrame(i)
            # save image
            saveRect = pygame.Rect(20, 12, 390, 210)
            imageFrame = screen.subsurface(saveRect)
            pygame.image.save(imageFrame, fileName+str(i)+".jpg")                       
        
def terminate(): # close down the program
    global midiout
    pixels.fill((0, 0, 0))
    pixels.show()
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
         
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())    
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())    

# Main program logic:
if __name__ == '__main__':    
    main()        


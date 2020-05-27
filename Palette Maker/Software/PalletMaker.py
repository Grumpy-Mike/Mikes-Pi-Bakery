#!/usr/bin/env python3
# coding=utf-8
# Pallet Maker
# By Mike Cook April 2020

import time
import pygame
import pigpio
import os
import colorsys
import copy
from ky040 import Ky040
from tkinter import filedialog
from tkinter import *

os.system("sudo pigpiod")
time.sleep(1.0)

def main():
    global update, sequence
    init()
    drawScreen()
    time.sleep(2.0)
    while 1 :
        checkForEvent()
        time.sleep(0.3)
   
def init():
    global screen, knob, fileName, font, backCol, pRect, black, saveRect
    global numberOfSteps, maxSteps, screenWidth, screenHight, hiLight
    global cLab, contPram, lhP, rhP, whatColRect, whatCol, whatColName
    global sampleRect, adjustCol, hsvInt, intLab, intLabS, intRect, palSt
    fileName = "/home/pi/pallet.png"
    pygame.init()
    pygame.display.set_caption("Pallet Maker")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,
                              pygame.QUIT,
                             pygame.MOUSEBUTTONDOWN])
    screenWidth = 800 ; screenHight = 300
    cp = (screenWidth // 2, screenHight // 2)
    screen = pygame.display.set_mode([screenWidth,
                                screenHight], 0, 32)
    maxSteps = 16
    numberOfSteps = 8
    loadImages()
    font = pygame.font.Font(None, 34)
    backCol = (196, 196, 196) ; black = (0,0,0) ; hiLight = (0,192,0)
    pRect = [0,0,0,0]
    # rectangles for left hand knob
    for i in range(0, 4) :
      pRect[i] = drawWords("255", 60, 20+ i*50, black, backCol)
    # for red outline - left hand knob
    pRect[0].inflate_ip(8, 4) ; pRect[1].inflate_ip(8, 4)
    pRect[2].inflate_ip(8, 4) ; pRect[3].inflate_ip(8, 4)
    cLab = [('R', 'G', 'B', 'S')]
    sampleRect = pygame.Rect(140, 60, 600, 100)
    # adjustCol - initial values - background - First colour - Last colour
    adjustCol = [(255,255,255), (255,0,0), (0,255,0)]
    labS = [20, 200, 340, 440] # label spacing
    contPram = [adjustCol[1][0], adjustCol[1][1], adjustCol[1][2], 8] # set up for first colour
    whatCol = 1
    whatColName = ['Background', 'First', 'Last', 'Invert background']
    whatColRect = [0,0,0,0]
    for i in range(0,4) :
        whatColRect[i] = drawWords(whatColName[i], labS[i], 210, black, backCol)
        whatColRect[i].inflate_ip(8, 4)
    intLab = ['Interpolate', 'RGB', 'HSV']
    intLabS = (440, 600, 680)
    intRect = [0,0,0]
    for i in range(0,3) :
        intRect[i] = drawWords(intLab[i], intLabS[i], 20, black, backCol)
        intRect[i].inflate_ip(8, 4)
    palSt = [(0, 0, 0 )] * 16    
    lhP = 0 ; rhP = 1 # initial values of left hand and right hand controls
    hsvInt = False # interpolate in hsv
    saveRect = drawWords("Save Pallet", 650, 260, black, backCol)
    knobL = Ky040(clk=22, dt=27, cbrot = cbRotL,
            sw = 17, cbr=cbSwRL, cbf=cbSwL)
    knobR = Ky040(clk=24, dt=23, cbrot = cbRotR,
            sw = 18, cbr=cbSwRR, cbf=cbSwR)    
           
def loadImages():
    global logo
    logo = pygame.image.load(
       "images/logo.png").convert_alpha()

def drawScreen() :
    screen.fill(backCol)
    screen.blit(logo, (0, screenHight - 50))
    drawWords("Save Pallet", saveRect.x, saveRect.y,
                  black, backCol)
    for i in range(0, 4) : # draw controls
        drawWords(cLab[0][i], 20, 20 + i*50, black, backCol)
    for i in range(0, 4) :
        drawWords(whatColName[i], whatColRect[i].x + 4, whatColRect[i].y + 2,
                  black, backCol)
    for i in range(0, 3) :
        drawWords(intLab[i], intRect[i].x + 4, intRect[i].y + 2,
                  black, backCol)
    
    updateWhatCol()
    updateControlValues()
    updateSamples()
    
def updateSamples():
    adjustCol[whatCol] = (contPram[0], contPram[1], contPram[2]) # change colour to update
    x = sampleRect.x + 15 ; y = sampleRect.y
    space = (sampleRect.w - 15) // contPram[3]
    pygame.draw.rect(screen, adjustCol[0], sampleRect, 0) # background
    pygame.draw.rect(screen, black, sampleRect, 3)
    for i in range(0,contPram[3]) :
        col = makeCol(i)
        palSt[i] = col
        pygame.draw.rect(screen, col, (x+i*space, y+30, 30, 50 ), 0)
    pygame.display.update()    
        
def makeCol(place) :
    if place == 0 :
        #print(adjustCol[1])
        return adjustCol[1]
    if place == contPram[3] -1 :
        #print(adjustCol[2])
        return adjustCol[2]
    if hsvInt :
        col = hsvShift(place)
    else :    
        r = (adjustCol[1][0] - adjustCol[2][0]) * place // (contPram[3] - 1)
        g = (adjustCol[1][1] - adjustCol[2][1]) * place // (contPram[3] - 1)
        b = (adjustCol[1][2] - adjustCol[2][2]) * place // (contPram[3] - 1)
        col = ((adjustCol[1][0] - r, adjustCol[1][1] - g, adjustCol[1][2] - b))
    #print(col)
    return col

def updateWhatCol():
    for i in range(0,3):
        pygame.draw.rect(screen, backCol, whatColRect[i], 1)
    pygame.draw.rect(screen, hiLight, whatColRect[whatCol], 1)
    for i in range(1,3):
        pygame.draw.rect(screen, backCol, intRect[i], 1)
    if hsvInt :    
        pygame.draw.rect(screen, hiLight, intRect[2], 1)
    else :
        pygame.draw.rect(screen, hiLight, intRect[1], 1)
    
def updateControlValues() :
    for i in range(0, 4):
        pygame.draw.rect(screen, backCol, pRect[i], 0)
        drawWords(str(int(contPram[i])), 60, 20 + i* 50, black, backCol)
    pygame.draw.rect(screen, (196, 0, 0), pRect[lhP], 1) # draw back select rectangles
    pygame.draw.rect(screen, (0, 0, 196), pRect[rhP], 1)
    
def drawWords(words, x, y, col, backCol) :
    txtSurface = font.render(words, True, col, backCol)
    textRect = txtSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(txtSurface, textRect)
    return textRect    
   
def cbRotL(inc):
    global contPram
    contPram[lhP] -= inc
    if lhP == 3 :
        if contPram[lhP] > 16 : contPram[lhP] = 16
        if contPram[lhP] < 3 : contPram[lhP] = 3
        updateSamples()
    else :  
        if contPram[lhP] > 255 : contPram[lhP] = 0
        if contPram[lhP] < 0 : contPram[lhP] = 255    
    updateControlValues()
    updateSamples()
    
def cbRotR(inc):
    global contPram
    contPram[rhP] -= inc
    if contPram[rhP] > 255 : contPram[rhP] = 0
    if contPram[rhP] < 0 : contPram[rhP] = 255
    updateControlValues()
    updateSamples()

def cbSwL(pin, level, tick):
    global lhP
    if lhP == 0 : lhP = 2
    else : lhP = 0
    updateControlValues()
    pygame.display.update()

def cbSwR(pin, level, tick):
    global lhP
    if lhP == 3 : lhP = 2
    else : lhP = 3
    updateControlValues()
    pygame.display.update()
    
    
def cbSwRR(pin, level, tick):
    # Right switch release 
    pass    
    
def cbSwRL(pin, level, tick):
    # Left switch release
    pass

def hsvShift(place):
    start = colorsys.rgb_to_hsv(adjustCol[1][0]/255, adjustCol[1][1]/255,
                                 adjustCol[1][2]/255)     
    end = colorsys.rgb_to_hsv(adjustCol[2][0]/255, adjustCol[2][1]/255,
                                 adjustCol[2][2]/255)
    #print(start, end, place)
    dh = (end[0] - start[0]) * place / (contPram[3] - 1)
    ds = (end[1] - start[1]) * place / (contPram[3] - 1)
    dv = (end[2] - start[2]) * place / (contPram[3] - 1)
    #print((dh,ds,dv))
    col = colorsys.hsv_to_rgb(start[0] + dh, start[1] + ds, start[2] + dv)
    #print(col)
    return(int(col[0] * 255.0), int(col[1] * 255.0), int(col[2] * 255.0))

def handleMouse(pos):
    global whatCol, contPram, hsvInt
    #print(pos)
    for i in range(0,3) :
        if whatColRect[i].collidepoint(pos) :
            adjustCol[whatCol] = (contPram[0], contPram[1], contPram[2]) # save last
            for j in range(0,3) :
                    contPram[j] = adjustCol[i][j]
            whatCol = i
            updateWhatCol()
            updateControlValues()
            updateSamples() ; return

    if whatColRect[3].collidepoint(pos) :
        adjustCol[0] =( 0xFF ^ adjustCol[0][0], 0xFF ^ adjustCol[0][1], 0xFF ^ adjustCol[0][2])
        if whatCol == 0 :
            contPram[0] = adjustCol[0][0]
            contPram[1] = adjustCol[0][1]
            contPram[2] = adjustCol[0][2]
        updateControlValues()
        updateSamples() ; return
    for i in range(1,3) :
        if intRect[i].collidepoint(pos) :
            hsvInt = not hsvInt
            updateWhatCol()
            updateSamples() ; return
    if saveRect.collidepoint(pos) :
        savePallet()
        
def savePallet():
    global fileName
    root = Tk()
    path = os.path.dirname(fileName)
    root.filename = filedialog.asksaveasfilename(initialdir = path,
        title = "file to save pallet in",
        filetypes = (("pal files","*.pal"),
                     ("all files","*.*")))
    temp = root.filename
    if len(temp) >3 :
        fileName = temp
        file = open(fileName, "w")
        file.write("JSC-PAL\n")
        file.write("0100\n")
        file.write(str(contPram[3]) + "\n")
        for i in range(0,contPram[3]) :
            for j in range(0,3) :
                file.write(str(palSt[i][j]) + " ")
            file.write("\n")    
        file.close()
    root.withdraw()
                               
def terminate(): # close down the program
    knobL.cancel() ; knobR.cancel()
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        

if __name__ == '__main__':
    main()

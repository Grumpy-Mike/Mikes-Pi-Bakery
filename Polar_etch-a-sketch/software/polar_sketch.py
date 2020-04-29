# #!/usr/bin/env python3
# coding=utf-8
# Polar Etch-a-sketch
# By Mike Cook March 2020
'''
This code is copyright Mike Cook 2020 and this notice should not be removd
from this code.
It may be freeley used by any individual or education establishment.
It can be linked to on GitHub but must not be stored on any publically
accessable network.
It is posted in good fath, but Mike Cook is not responcible for anything this
software does, or fails to do.
Given the constantly changing nature of Linux, it might at some future time
stop working Mike Cook does not garuntee to update this softerware.
'''

import time
import pygame
import pigpio
import math as maths
import os
import random
from ky040 import Ky040
from tkinter import filedialog
from tkinter import *

os.system("sudo pigpiod")
time.sleep(1.0)

def main():
    init()
    updateControls()
    time.sleep(0.2)
    while 1 :
        checkForEvent()
        time.sleep(0.2)
   
def init():
    global totR, totTh, screen, knobL, knobR, cp, grid
    global drawArea, sW, sH, drawCol, yel, control
    global colRect, colours, font, black, back
    global dMode, drawFrom, drawTo, cursor, drawing 
    global fileName, lineW, drawF, lastUpR, lastUpTh
    global plotStart, plotEnd
    plotStart = 0 ; plotEnd = 1
    fileName = "/home/pi/sketch.png"
    totR = 0 ; totTh = 0 ; dMode = True
    lastUpR = 0 ; lastUpTh = 0
    drawFrom = (0, 0) ; drawTo = (0, 0)
    pygame.init()
    pygame.display.set_caption("Polar Etch-A-Sketch")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,
                              pygame.QUIT,
                              pygame.MOUSEBUTTONDOWN])
    sW = 786 ; sH = 640 ; yel = (200, 200, 0)
    cp = (sH // 2, sH // 2)
    screen = pygame.display.set_mode([sW, sH], 0, 32)
    drawArea = pygame.Rect((0, 0), (sH, sH))                  
    grid = pygame.Surface([sH, sH]) ; drawGrid(grid)
    drawing = pygame.Surface([sH, sH])
    drawing.set_colorkey((1, 1, 1)) # nearly balck
    pygame.Surface.fill(drawing, (1, 1, 1))    
    cursor = pygame.Surface([15, 15])
    cursor.set_colorkey((1, 1, 1))
    pygame.Surface.fill(cursor, (1, 1, 1))
    pygame.draw.line(cursor, yel, (0, 7), (14, 7), 1)
    pygame.draw.line(cursor, yel, (7, 0), (7, 14), 1)
    colRect = [pygame.Rect((0, 0), (15, 15))] * 32
    for j in range(0, 8):
        for i in range(0, 4) :
            colRect[i + j * 4] = pygame.Rect((
                        22 + i*30, 7 + j*30),(15, 15)) 
    black = (0, 0, 0) ; back = (230, 230, 230)
    colours = [black] * 32
    font = pygame.font.Font(None, 34)
    knobL = Ky040(clk=22, dt=27, cbrot = cbRotL,
            sw = 17, cbr=cbSwRL, cbf=cbSwL)
    knobR = Ky040(clk=24, dt=23, cbrot = cbRotR,
            sw = 18, cbr=cbSwRR, cbf=cbSwR)    
    loadPallet() ; drawCol = 5 ; lineW = 3
    control = pygame.Surface([sW-sH, sH])
    # default function use s & e (shift or not) keys to set plotting range
    drawF = "r * (maths.sin((th + cTh) * 3))"
    #drawF = "r*maths.sin(th) + r*maths.sin(5*th/2)**3"
    #drawF = "r*maths.sin(cTh* th/4)"
    #drawF = "r*maths.sin(2**(th)) - r* 1.7"
    drawControls(control)

def loadPallet() :
    global colours
    from palettable.colorbrewer.qualitative import Set1_8
    for i in range(0, 8) :
         colours[i] = Set1_8.colors[i]
    from palettable.cartocolors.qualitative import Prism_8
    for i in range(0, 8) :
         colours[i+8] = Prism_8.colors[i]
    from palettable.cartocolors.qualitative import Safe_8
    for i in range(0, 8) :
         colours[i+16] = Safe_8.colors[i]
    from palettable.cmocean.sequential import Gray_8
    for i in range(0, 8) :
         colours[i+24] = Gray_8.colors[i]

def drawCircle():
    r = totR
    lastPos = polarToCart(r, 0)
    for th in range(0, 361) :
        pos = polarToCart(r, th)
        pygame.draw.line(drawing, colours[drawCol],
                         pos, lastPos, lineW)
        lastPos = pos
    updateControls()

def drawFunction(): 
    r = totR ; cTh = maths.radians(totTh)
    first = True ; step = 1
    if plotEnd - plotStart < 0 : step = -1
    for angle in range(plotStart * 360, plotEnd * 360 + 1, step) :
        th = maths.radians(angle)
        point = eval(drawF)
        pos = polarToCartFunc(point, angle)
        if first :
            pygame.draw.line(drawing, colours[drawCol],
                             pos, pos, lineW)
            first = False
        else :    
            pygame.draw.line(drawing, colours[drawCol],
                             pos, lastPos, lineW)
        lastPos = pos
    updateControls()    
        
def drawTrack() :
    rFrom = drawFrom[0] ; rTo = totR
    thFrom = drawFrom[1] ; thTo = totTh
    if abs(thFrom - thTo) > 180 and abs(thFrom - thTo) < 360 :
        thTo -= 360  
        #print("taking short cut")
    if thTo < thFrom :
        thTo, thFrom = thFrom, thTo
        rTo, rFrom = rFrom, rTo
    if thFrom - thTo == 0 : # stop divide by zero
        rInc = rFrom - rTo
    else :    
        rInc = (rTo - rFrom) / (abs(thFrom - thTo))
    rPlot = rFrom
    lastPos = polarToCart(rFrom, thFrom)
    if thFrom == thTo : # same theta value
        pos = polarToCart(rTo, thTo)
        pygame.draw.line(drawing, colours[drawCol],
                         pos, lastPos, lineW)
    else :
        for th in range(thFrom, thTo + 1):
            pos = polarToCart(rPlot, th)
            rPlot += rInc
            pygame.draw.line(drawing, colours[drawCol],
                             pos, lastPos, lineW)
            lastPos = pos
    
def updateControls():
    global font, lastUpR, lastUpTh
    hi = (255, 64, 0)
    screen.blit(control, (sH, 0))
    font = pygame.font.Font(None, 34)
    pygame.draw.rect(screen, (10, 10, 10),
                     colRect[drawCol].move(sH, 0), 2)
    drawWords(str(totTh) + "\u00b0", 52 + sH, 294,
              black, back, screen)
    drawWords(str(totR), 52 + sH, 258, black, back,
              screen)
    font = pygame.font.Font(None, 24)
    drawWords(str(lineW), 110 + sH, 350, black, back,
              screen)    
    drawWords(str(drawFrom[0]) + ", " + str(int(drawFrom[1])) + "\u00b0", 60 + sH, 440, black, back, screen)
    screen.blit(grid, (0, 0))
    if dMode :
        pygame.draw.rect(screen, hi, modeS, 1)
        if lastUpR != totR or lastUpTh != totTh :
            lastP = polarToCart(lastUpR, lastUpTh)
            newP  = polarToCart(totR, totTh)
            pygame.draw.line(drawing, colours[drawCol],
                             lastP, newP, lineW)         
    else :
        pygame.draw.rect(screen, hi, modeM, 1)
    lastUpR = totR ; lastUpTh = totTh
    screen.blit(drawing, (0, 0))
    pos = polarToCart(totR, totTh)
    screen.blit(cursor, (pos[0] - 7, pos[1] - 7))    
    pygame.draw.line(screen, (200, 200, 0), (sH, 0),
                     (sH, sH), 3)    
    pygame.display.update()

def drawControls(s):
    global font, saveRect, modeM, modeS, lineRect 
    global drawRect, circleRect, fromRect, saveRect
    global eFuncRect, functionRect, ndRect   
    s.fill(back) ; font = pygame.font.Font(None, 34)
    for i in range(0, 32):
        pygame.draw.rect(s, colours[i],
                         colRect[i] , 0)
    drawWords(chr(0x3B8), 24, 294, black, back, s) 
    drawWords("R", 24, 258, black, back, s)
    font = pygame.font.Font(None, 24)
    lineRect = drawWords("Line width", 10, 350, black,
                         back, s).move(sH, 0)    
    modeS = drawWords("Sketch", 10, 380, black,
                      back, s).move(sH, 0)    
    modeM = drawWords("Move", 10, 410, black,
                      back, s).move(sH, 0)    
    fromRect = drawWords("From", 10, 440, black
                         , back, s).move(sH, 0)    
    drawRect = drawWords("Draw", 10, 470, black,
                         back, s).move(sH, 0)
    circleRect = drawWords("R Circle", 10, 500, black,
                           back, s).move(sH, 0)
    functionRect = drawWords("Draw function", 10, 530,
                            black, back, s).move(sH, 0)    
    eFuncRect = drawWords("Enter function", 10, 560,
                          black, back, s).move(sH, 0)    
    ndRect = drawWords("New drawing", 10, 590, black,
                       back, s).move(sH, 0)       
    saveRect = drawWords("Save Drawing", 10, 617, black,
                         back, s).move(sH, 0)
    lineRect.inflate_ip(6, 0) ; ndRect.inflate_ip(6, 0)
    modeM.inflate_ip(6, 0) ; fromRect.inflate_ip(6, 0)
    eFuncRect.inflate_ip(6, 0) ; modeS.inflate_ip(6, 0)
    functionRect.inflate_ip(6, 0)    
    pygame.draw.line(s, yel, (0, 246), (sW-sH, 246), 3)
    pygame.draw.line(s, yel, (0, 337), (sW-sH, 337), 3)
        
def drawGrid(s):
    gridCol = (120, 120, 120)
    pygame.draw.rect(s, (128, 128, 128),
                        drawArea , 0)
    for th in range(40, sH, 40) :
        pygame.draw.circle(s, gridCol, cp, th, 1)
    d = 450 # max R    
    for r in range(0, 360, 9) :
        x = d * maths.cos(maths.radians(r))
        y = d * maths.sin(maths.radians(r))
        pygame.draw.line(s, gridCol, cp,
                     (cp[0]+x, cp[1]+y), 1)    

def drawWords(words, x, y, col, backCol, s) :
    txtSurface = font.render(words, True, col, backCol)
    textRect = txtSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    s.blit(txtSurface, textRect)
    return textRect

def cbRotL(inc):
    global totTh
    totTh -= inc
    updateControls()

def cbRotR(inc):
    global totR
    totR -= inc
    updateControls()

def cbSwL(pin, level, tick):
    global totTh
    totTh += 360
    updateControls()

def cbSwR(pin, level, tick):
    global totTh
    totTh -= 360
    updateControls()
    
def cbSwRR(pin, level, tick):
    # Right switch release 
    pass

def cbSwRL(pin, level, tick):
    # Left switch release
    pass
    
def handleMouse(pos): # look at mouse down
    global totTh, totR, dMode, drawFrom
    global drawCol, lineW, drawF, drawing
    #print(pos)
    if pos[0] < sH :
        carToPolar(cp[0] - pos[0], cp[1] - pos[1])
        return
    if pos[1] < 244 and pos[0] > sH :
        x = pos[0] - sH ; y = pos[1]
        cs = 0 ; found = False
        while cs < 32 and not found :
            if colRect[cs].collidepoint((x, y)) :
                drawCol = cs
                found = True
                updateControls()
            cs += 1    
        return                         
    if pos[1] > 244 :
        if lineRect.collidepoint(pos) :
            lineW += 1
            if lineW > 4 : lineW = 1
            updateControls()
        if modeS.collidepoint(pos) :
            dMode = True ; updateControls()
        if modeM.collidepoint(pos) :
            dMode = False ; updateControls()
        if fromRect.collidepoint(pos) :
            drawFrom = (totR, totTh)
            updateControls()
        if drawRect.collidepoint(pos) :
            drawTrack()
            updateControls()
        if circleRect.collidepoint(pos) :
            drawCircle()
        if functionRect.collidepoint(pos) :
            try :
                drawFunction()
            except:
                print("Your function contained an error")
        if eFuncRect.collidepoint(pos) :
            print("Your last function was ", drawF)
            drawF = input("Function to plot R = ")
            print("Your function is ", drawF)
        if ndRect.collidepoint(pos) :
            pygame.Surface.fill(drawing, (1, 1, 1))
            updateControls() 
        if saveRect.collidepoint(pos) :
            saveDrawing()
                     
def carToPolar(x, y):
    global totTh, totR, lastUpTh, lastUpR
    totR = int(maths.sqrt(x**2 + y**2))
    totTh =  maths.degrees(maths.atan2(y, x))
    if totTh < 0.0 :
        totTh += 360.0
    totTh = int(totTh)
    lastUpR = totR ; lastUpTh = totTh
    updateControls()

def polarToCart(r, th):
    if th > 180 : th -= 360
    x = -r * maths.cos(maths.radians(th)) + cp[0]
    y = -r * maths.sin(maths.radians(th)) + cp[0]
    return (x, y)

def polarToCartFunc(r, th):
    x = -r * maths.cos(maths.radians(th)) + cp[0]
    y = -r * maths.sin(maths.radians(th)) + cp[0]
    return (x, y)

def saveDrawing():
    global fileName
    root = Tk()
    path = os.path.dirname(fileName)
    root.filename = filedialog.asksaveasfilename(initialdir = path,
        title = "file to save sketch in",
        filetypes = (("png files","*.png"),
                     ("all files","*.*")))
    temp = root.filename
    if len(temp) >3 :
        fileName = temp
        file = open(fileName, "w")
        sDraw = pygame.Surface.convert_alpha(drawing)
        pygame.image.save(sDraw, fileName)
        file.close()
    root.withdraw()
    
def plotRange():
    print("Function plot from",plotStart * 360,"to",plotEnd * 360,"degrees")
    
def terminate(): # close down the program
    knobL.cancel() ; knobR.cancel()
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    global plotStart, plotEnd
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
        if event.key == pygame.K_ESCAPE :
          terminate()
        if event.mod == pygame.KMOD_NONE :        
            if event.key == pygame.K_s:
                plotStart += 1
                plotRange()
            if event.key == pygame.K_e and event.mod != pygame.KMOD_SHIFT :
                plotEnd += 1
                plotRange()  
        else :
            if event.key == pygame.K_s :
                plotStart -= 1
                plotRange()
            if event.key == pygame.K_e :
                plotEnd -= 1
                plotRange()         
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        
                 
if __name__ == '__main__':
    main()

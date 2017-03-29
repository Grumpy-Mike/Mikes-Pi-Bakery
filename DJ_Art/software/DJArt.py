#!/usr/bin/env python
# DJ Hero Art generator
# Mike Cook Feb 2017
from smbus import SMBus
import pygame, time, os , math
from cStringIO import StringIO
from Tkinter import Tk
from tkFileDialog import asksaveasfilename

Tk().withdraw()
pygame.init()                   # initialise graphics interface
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Scratch Art")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.QUIT])
screenSize = 560 ; controlBar = 100
pCenterY = screenSize / 2 ; pCenterX = pCenterY + controlBar
scale = pCenterY / 2
screen = pygame.display.set_mode([screenSize+controlBar,screenSize],0,32)
textHeight = 18 
font = pygame.font.Font(None, textHeight)

background = 0
bgCol = (0,0,0) ; fgCol = (255,255,255)
pRed = 255 ; pGreen = 130 ; pBlue = 0
menuCol = [fgCol,fgCol,fgCol,fgCol,fgCol]
highlightCol = [(0,255,255),(255,64,32),(0,255,0),(0,64,192),(255,255,0)]
menuHead = [" Pendulum X1"," Pendulum X2"," Pendulum Y1"," Pendulum Y2"," Track"]
lastX= 0.0; lastY= 0.0; currentX=0.0 ; currentY=0.0
tickStop = 10 ; short = 10
tickInc = 0.005 # controls track smoothness
update = True ; pramChanged = True
updateButton = 0 ; bBackLast = 0
pramSelect = 0 ; pPramS = 0
shotNumber =0 ; savePath = ""

def main():
    global update,pramChanged
    init()
    print "DJ Hero - Art Machine"
    while 1:
      checkForEvent()
      checkControls()
      if update:
         swing(tickStop)
         update = False
      if pramChanged:
          showPrams()
          pramChanged = False

def checkControls():
    global tickStop,update,updateButton,pramSelect,pPramS,pramChanged,bBackLast
    global savePath,shotNumber
    block = readDJ()
    if block[0] & 0x3F <10 : # X joystick
        saveScreen(0) # just pattern
    if block[1] & 0x3F >50 : #Y joystick
        saveScreen(1) # all screen
    if block[1] & 0x3F <10 or block[0] & 0x3F >50:
        savePath = ""
        shotNumber = 0
    draw = buttonFix(block[5] & 0x10)   
    if draw and updateButton == 0 : #draw button
       update = True
       pramChanged = True
       tickStop = 10 + (((block[2] >> 1) & 0x0f)+1) * 30
    updateButton = draw # for edge detection
    
    bBack = buttonFix(block[4] & 0x10)
    if bBackLast == 0 and bBack : # toggle background
        toggleBackground()
        #update = True #swap with line below for full draw
        swing(short) # short fast display
        pramChanged = True
    bBackLast = bBack # for edge detection
    
    buttonP = buttonFix(block[4] & 0x04)
    if pPramS == 0 and buttonP == 1 :
       pramSelect += 1
       pramChanged = True
       if pramSelect >4:
           pramSelect = 0
    pPramS = buttonP
    butRed = buttonFix(block[4] & 0x02)
    butGreen = buttonFix(block[5] & 0x20)
    butBlue = buttonFix(block[5] & 0x04)
    if pramSelect < 4 :
        adjustPends(butRed,butGreen,butBlue,block)
    else:
        adjustDraw(butRed,butGreen,butBlue,block)
        
def toggleBackground():
    global background, bgCol,fgCol,menuCol,highlightCol
    if background :
        background = 0
        bgCol = (0,0,0)
        fgCol = (255,255,255)
        menuCol = [fgCol,fgCol,fgCol,fgCol,fgCol]
        highlightCol[4] = (255,255,0)
    else:
        background = 1
        bgCol = (255,255,255)
        fgCol = (0,0,0)
        menuCol = [fgCol,fgCol,fgCol,fgCol,fgCol]
        highlightCol[4] = (192,192,0)
        
def adjustDraw(br,bg,bb,block):
    global pRed,pGreen,pBlue
    while br == 1:
       pRed = wrapColour(getTurn(block),pRed)
       showPrams()
       swing(short) # short fast display
       block = readDJ()
       br = buttonFix(block[4] & 0x02)
    while bg == 1:
       pGreen = wrapColour(getTurn(block),pGreen)
       showPrams()
       swing(short) # short fast display
       block = readDJ()
       bg = buttonFix(block[5] & 0x20)
    while bb == 1:
       pBlue = wrapColour(getTurn(block),pBlue)
       showPrams()
       swing(short) # short fast display
       block = readDJ()
       bb = buttonFix(block[5] & 0x04)

def wrapColour(inc,col): # constrain 0 to 255
    col += inc
    if col < 0 :
        col = 0
    if col > 255:
        col = 255
    return col    
    
def adjustPends(br,bg,bb,block):        
    while br == 1 and bg == 0:
        inc = getTurn(block) * 0.01
        freq[pramSelect] += inc
        if freq[pramSelect] < 1.0:
           freq[pramSelect] = 1.0 
        showPrams()
        swing(short) # short fast display
        block = readDJ()
        br = buttonFix(block[4] & 0x02)
        bg = buttonFix(block[5] & 0x20)
    while bg == 1 and br == 0:
        inc = getTurn(block) * 0.05
        phase[pramSelect] += inc
        if phase[pramSelect] < 0.0:
            phase[pramSelect] = 6.2
        if phase[pramSelect] > 6.2:
            phase[pramSelect] = 0.0
        showPrams()
        swing(short) # short fast display
        block = readDJ()
        bg = buttonFix(block[5] & 0x20)
        br = buttonFix(block[4] & 0x02)
    while bb == 1:
        inc = getTurn(block) * 0.001
        damping[pramSelect] += inc
        if damping[pramSelect] < 0.0:
            damping[pramSelect] = 0.0
        showPrams()
        swing(short) # short fast display
        block = readDJ()
        bb = buttonFix(block[5] & 0x04)
    while bg == 1 and br == 1:
        inc = getTurn(block) * 0.01
        amp[pramSelect] += inc
        amp[pramSelect] += inc
        if amp[pramSelect] < 0.0:
            amp[pramSelect] = 0.0
        if amp[pramSelect] > 1.0:
            amp[pramSelect] = 1.0    
        showPrams()
        swing(short) # short fast display
        block = readDJ()
        bg = buttonFix(block[5] & 0x20)
        br = buttonFix(block[4] & 0x02)

# Currently an issue with the I2C drivers or something throws up an occasional error - this is the sticking plaster
# See this thread:- https://www.raspberrypi.org/forums/viewtopic.php?f=44&t=178000
def readDJ():
    try:
       bus.write_byte(0x52,0)
    except:
       #print"bus restart" 
       init()
       bus.write_byte(0x52,0)
    dj = [(bus.read_byte(0x52)) for i in range(6)]
    return dj
        
def getTurn(block): # work out turntable change
      table = (block[2] >> 7) | ((block[1] & 0xC0)>> 5) | ((block[0] &0xC0) >> 3)
      if block[2] & 0x01 == 0x01: # the sign bit
         table = -(table ^ 0x1F)-1
      return table

def buttonFix(value):
    pressed = 1
    if(value != 0):
        pressed = 0
    return pressed
        
def swing(stop):
    tick = 0    
    pygame.draw.rect(screen,bgCol,(controlBar,0,screenSize,screenSize),0)
    nextUpdate = time.time()+0.04
    while tick < stop :
      calcNewPoint(tick)
      tick += tickInc
      if tick > tickInc:
        pygame.draw.line(screen,(pRed,pGreen,pBlue),(lastX,lastY),(currentX,currentY),1)
      if time.time()> nextUpdate :
         pygame.display.update()
         nextUpdate = time.time()+0.04
         checkForEvent()
    pygame.display.update() # mop up any un-shown track

def calcNewPoint(tick):
    global lastX, lastY,currentX,currentY
    lastX = currentX
    lastY = currentY
    damping0 = math.exp(-(tick*damping[0]))
    damping1 = math.exp(-(tick*damping[1]))
    damping2 = math.exp(-(tick*damping[2]))
    damping3 = math.exp(-(tick*damping[3]))    
    currentX = amp[0]*math.sin((tick*freq[0])+phase[0])*damping0
    currentX += amp[1]*math.sin((tick*freq[1])+phase[1])*damping1
    currentX = pCenterX+scale*currentX
    currentY = amp[2]*math.sin((tick*freq[2])+phase[2])*damping2
    currentY += amp[3]*math.sin((tick*freq[3])+phase[3])*damping3
    currentY = pCenterY+scale*currentY

def init():
    global bus
    i2c_bus = 1 # change to 0 for original Pi
    bus = SMBus(i2c_bus)
    bus.write_byte_data(0x52,0xF0,0x55)
    initValues()
    
def initValues(): # change for starting point
    global damping,freq,phase,amp
    damping = [0.0,0.01,0.01,0.01]
    freq = [1.0,2.0,4.0,6.0]
    phase = [0.0,0.0,0.0,0.0]
    amp = [1.0,0.8,1.0,0.8]

def saveScreen(s):
    global shotNumber,savePath
    if savePath == "":
        savePath = getSavePath()
    if s == 0: # just pattern   
       rect = pygame.Rect(controlBar,0,screenSize,screenSize)
    else: # whole screen
       rect = pygame.Rect(0,0,screenSize+controlBar,screenSize)
    sub = screen.subsurface(rect)
    pygame.image.save(sub, savePath+"_"+str(shotNumber)+".jpg")
    shotNumber +=1
    joyRelease()

def getSavePath():
    path = asksaveasfilename()
    return path
    
def joyRelease():
    block = readDJ()
    while block[0] & 0x3F <10 or block[1] & 0x3F >50 :
        block = readDJ()
    drawWords("  Saved",fgCol,0,screenSize-18)
    pygame.display.update()

def showPrams():
    pygame.draw.rect(screen,bgCol,(0,0,controlBar,screenSize),0)
    pos = 20
    for p in range(0,5):
       if p == pramSelect:
          if p== 4:
              printDraw(pos,p,highlightCol)
          else:    
             printPens(pos,p,highlightCol)
       else :
          if p == 4:
              printDraw(pos,p,menuCol)
          else:    
             printPens(pos,p,menuCol)  
       pos +=110       
    pygame.display.update()

def printDraw(Y,p,col):
    drawWords(menuHead[p],col[0],0,Y)
    drawWords("  Red "+str(pRed),col[1],0,20+Y)
    drawWords("  Green "+str(pGreen),col[2],0,40+Y)
    drawWords("  Blue "+str(pBlue),col[3],0,60+Y)
    if p == pramSelect:
       pygame.draw.line(screen,(255,130,0),(3,Y+20),(3,Y+70),1)
   
def printPens(Y,p,col):
    drawWords(menuHead[p],col[0],0,Y)
    drawWords("  Frequency "+str(freq[p]),col[1],0,20+Y)
    drawWords("  Phase "+str(phase[p]),col[2],0,40+Y)
    drawWords("  Damping "+str(damping[p]),col[3],0,60+Y)
    drawWords("  Amplitude "+str(amp[p]),col[4],0,80+Y)
    if p == pramSelect:
       pygame.draw.line(screen,(255,130,0),(3,Y+20),(3,Y+90),1)
    
def drawWords(words,col,x,y) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        textSurface = font.render(words, True, col, bgCol)
        screen.blit(textSurface, textRect)

def terminate(): # close down the program
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()

# Main program logic:
if __name__ == '__main__':    
    main()
    

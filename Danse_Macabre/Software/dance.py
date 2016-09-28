# Raspberry Pi - Danse Macabre
# Using the spectrum display hardware from MagPi 46
# By Mike Cook - August 2016

import pygame, time, os, math
from pygame.locals import *
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
screen = pygame.display.set_mode((0, 0)) # with window bar - use for debugging
pygame.display.iconify() # hide window
xPovitBodyLarm = 17   ; yPovitBodyLarm = 153
xPovitBodyLleg = 37   ; yPovitBodyLleg = 306
xPovitBodyRarm = 126  ; yPovitBodyRarm = 159
xPovitBodyRleg = 98   ; yPovitBodyRleg = 322
xPovitBodyThighL = 37 ; yPovitBodyThighL = 306
xPovitBodyThighR = 98 ; yPovitBodyThighR = 321
noiseFloor = [[200, 200, 200, 200, 200, 200, 200], [200, 200, 200, 200, 200, 200, 200]]
leftData = [ 0.1,0.1,0.1,0.1,0.1,0.1,0.1 ]
rightData = [ 0.1,0.1,0.1,0.1,0.1,0.1,0.1 ]

def main():
   print"Danse Macabre skeleton initialising"
   initGPIO()
   loadImages()
   initWindow()
   xbase =((xs/2.2)-100.0)
   print"Now click on iconified Danse tab"
   print"the space bar controls full screen display"
   foreArmMax = 36; ArmMax = 36   
   thighMax = 40; legMax = 36   
   moveThresh = 0.08
   while True:
      getSpectrumData()
      pan = int(xbase+float(xs/16)*(leftData[0]-rightData[0]))
      tilt = int((ys/4)*(leftData[1]-rightData[1]))+40
      ArmPosL = ArmMax/2
      if rightData[2] > moveThresh: 
         ArmPosL = int(float(ArmMax/2) + float(ArmMax)*(leftData[2]-0.5))
      foreArmPosL = int(float(foreArmMax/2) + float(foreArmMax)*(leftData[3]-0.5))
      thighPosL = thighMax/2
      if leftData[4] > moveThresh:
         thighPosL = int(float(thighMax/2) + float(thighMax)*(leftData[4]-0.5))
      legPosL = legMax/2
      if leftData[5] >moveThresh:
         legPosL = int(float(legMax/2) + float(legMax)*(leftData[5]-0.5))

      ArmPosR = ArmMax/2
      if rightData[2] >moveThresh:
         ArmPosR = int(float(ArmMax/2) + float(ArmMax)*(rightData[2]-0.5))
      foreArmPosR = int(float(foreArmMax/2) + float(foreArmMax)*(rightData[4]-0.5))
      thighPosR = thighMax/2
      if rightData[3] > moveThresh:
         thighPosR = int(float(thighMax/2) + float(thighMax)*(rightData[3]-0.5))
      legPosR = legMax/2
      if rightData[5] >moveThresh:
         legPosR = int(float(legMax/2) + float(legMax)*(rightData[5]-0.5))

      showPicture(ArmPosL,ArmPosR,foreArmPosL,foreArmPosR,thighPosL,thighMax-thighPosR-1,legPosL,legPosR,pan,tilt)
      checkForEvent()
      
def getSpectrumData():
    global leftData, rightData
    io.digitalWrite(pinReset,1)
    io.digitalWrite(pinClock,1)
    time.sleep(0.001)
    io.digitalWrite(pinClock,0)
    time.sleep(0.001)
    io.digitalWrite(pinReset,0)
    io.digitalWrite(pinClock,1)
    time.sleep(0.004)
    for s in range(0,7):
       io.digitalWrite(pinClock,0)
       time.sleep(0.004) # allow output to settle
       leftData[s] =  scaleReading(io.analogRead(70),s,0)
       rightData[s]=  scaleReading(io.analogRead(71),s,1)
       io.digitalWrite(pinClock,1)
              
def showPicture(armLpos,armRpos,farmLpos,farmRpos,thighRpos,thighLpos,legLpos,legRpos, x,y):
    #pygame.draw.rect(screen,(0,0,0),(0,0,xs,ys),0) # fast alternitave to background plot 
    screen.blit(background,(0,0))
    screen.blit(bodyFrame,(x,y))
    screen.blit(thighFrames[thighRpos],(x - thighPlot+xPovitBodyThighR,y-thighPlot+yPovitBodyThighR))  
    screen.blit(rightLegFrames[legRpos],(x - rightLegPlot + xPovitBodyThighR+dXthigh[thighRpos],y-rightLegPlot+yPovitBodyThighR+dYthigh[thighRpos]))

    screen.blit(thighFrames[thighLpos],(x - thighPlot+xPovitBodyThighL,y-thighPlot+yPovitBodyThighL))
    screen.blit(leftLegFrames[legLpos],(x - leftLegPlot + xPovitBodyThighL+dXthigh[thighLpos],y-leftLegPlot+yPovitBodyThighL+dYthigh[thighLpos]))
 
    screen.blit(armFramesL[armLpos],(x - armPlot+xPovitBodyLarm,y-armPlot+yPovitBodyLarm))  
    screen.blit(foreArmFramesL[farmRpos],(x - foreArmPlot + xPovitBodyLarm+dXarmL[armLpos],y-foreArmPlot+yPovitBodyLarm+dYarmL[armLpos]))
   
    screen.blit(armFramesR[armRpos],(x - armPlot+xPovitBodyRarm,y-armPlot+yPovitBodyRarm))   
    screen.blit(foreArmFramesR[farmRpos],(x - foreArmPlot+xPovitBodyRarm+dXarmR[armRpos],y-foreArmPlot+yPovitBodyRarm+dYarmR[armRpos]))
    pygame.display.update()

def loadImages():
    global foreArmFramesR,foreArmFramesL,foreArmPlot,armFramesR,armFramesL,armPlot,dXarmR,dYarmR,dXarmL,dYarmL
    global thighFrames, thighPlot, dYthigh, dXthigh, leftLegFrames, leftLegPlot,rightLegFrames, rightLegPlot, bodyFrame
    print"creating and scaling images"
    bodyFrame  = pygame.image.load("skImages/body.png").convert_alpha()
    print"creating legs"
    leftLegFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/leftLegzero.png").convert_alpha(),angle),(360,360))
                  for angle in range(90,-90,-5)]
    leftLegPlot = leftLegFrames[0].get_width()/2    
    rightLegFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/rightLegzero.png").convert_alpha(),angle),(360,360))
                  for angle in range(-90,90,5)]
    rightLegPlot = rightLegFrames[0].get_width()/2

    print"creating thighs"
    thighFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/thighzero.png").convert_alpha(),angle),(267,267))
                  for angle in range(100,-100,-5)]
    thighPlot = thighFrames[0].get_width()/2
    dYthigh = [ 101.56*math.cos(math.radians(angle))  for angle in range(100,-100,-5)]              
    dXthigh = [ 101.56*math.sin(math.radians(angle))  for angle in range(100,-100,-5)]

    print"creating arms"
    armFramesR = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/armzero.png").convert_alpha(),angle),(224,224))
                  for angle in range(150,-30,-5)]
    armPlot = armFramesR[0].get_width()/2
    dYarmR = [ 85.2*math.cos(math.radians(angle))  for angle in range(150,-30,-5)]              
    dXarmR = [ 85.2*math.sin(math.radians(angle))  for angle in range(150,-30,-5)]
    armFramesL = [ pygame.transform.flip(armFramesR[i], True,False)
                  for i in range(0,36)]
    dYarmL = [ 85.2*math.cos(math.radians(angle))  for angle in range(150,-30,-5)]              
    dXarmL = [ -85.2*math.sin(math.radians(angle))  for angle in range(150,-30,-5)]

    print"creating forearms"
    foreArmFramesL = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/forearmzero.png").convert_alpha(),angle),(334,334))
                  for angle in range(60,240,5)]
    foreArmPlot = foreArmFramesL[0].get_width()/2
    foreArmFramesR = [  pygame.transform.flip(foreArmFramesL[i], True,False)
                  for i in range(0,36)]

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def initWindow():
    global screen,xs, ys,debug,fullScreen,background
    debug = True
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    xs, ys = screen.get_size()
    fullScreen = False
    if not debug :   
       pygame.display.toggle_fullscreen()
       fullScreen = True
    pygame.display.set_caption("Danse Macabre")
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
    background = pygame.transform.smoothscale(pygame.image.load("skImages/background.jpg"),(xs,ys))

def scaleReading(reading,band,side):
    reading -= noiseFloor[side][band]
    if reading <0 :
       reading = 0
    scaled = (float(reading) / (1024.0 - float(noiseFloor[side][band])))
    return scaled

def initGPIO():
    global pinReset,pinClock
    pinReset = 23
    pinClock = 24
    try :
       io.wiringPiSetupGpio()
    except :
       print"start IDLE with 'gksudo idle' from command line"
       os._exit(1)
    io.pinMode(pinReset,1)
    io.pinMode(pinClock,1)
    io.mcp3002Setup(70,0)   
    
def terminate(): # close down the program
    print "Closing down please wait"
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global fullScreen
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_SPACE:
          pygame.display.toggle_fullscreen()
          fullScreen = not fullScreen

# Main program logic:
if __name__ == '__main__':
   main()

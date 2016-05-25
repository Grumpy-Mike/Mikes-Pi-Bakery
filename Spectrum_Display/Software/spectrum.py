# Spectrum - Sound visuliser
# By Mike Cook - April 2016

import pygame, time, os, random
from pygame.locals import *
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
enclosureSound= [ pygame.mixer.Sound("sounds/"+str(c)+".ogg") for c in range(0,10)]   

debug = False # debug with window bar, display numbers & raw data gather
screen = pygame.display.set_mode((0, 0)) # with window bar - use for debugging
xs, ys = screen.get_size()
fullScreen = False
if not debug :   
   pygame.display.toggle_fullscreen()
   fullScreen = True
else :
   ys -= 66
pygame.display.set_caption("Spectrum Sound Show")

posX = xs / 16
back1 = pygame.Surface(screen.get_size())
errase = pygame.Surface(screen.get_size())

pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
  
pinReset = 23
pinClock = 24
random.seed()
leftData = [ 6,7,8,90,80,70,60 ]
rightData = [ 60,70,80,90,80,70,60 ]
colour = [(255,0,0),(255,64,0),(128,255,0),(255,255,0),(0,114,141),(18,0,237),(255,0,255)]
if debug :
   noiseFloor = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
else :
   noiseFloor = [[57, 55, 58, 60, 71, 103, 124], [47, 72, 85, 86, 101, 136, 201]]
rawData = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]

textHeight = 36
font = pygame.font.Font(None, textHeight)

def main():
   initGPIO()
   while True:
     checkForEvent()
     getSpectrumData()
     plotData()
     
def getSpectrumData():
    # set up the chip ot read in the data
    global leftData, rightData
    io.digitalWrite(pinReset,1)
    io.digitalWrite(pinClock,1)
    time.sleep(0.001)
    io.digitalWrite(pinClock,0)
    time.sleep(0.001)
    io.digitalWrite(pinReset,0)
    io.digitalWrite(pinClock,1)
    time.sleep(0.004)
    # now read in each channel in turn
    for s in range(0,7):
       io.digitalWrite(pinClock,0)
       time.sleep(0.004) # allow output to settle
       leftData[s] = scaleReading(io.analogRead(70),s,0)
       rightData[s]= scaleReading(io.analogRead(71),s,1)
       io.digitalWrite(pinClock,1)

def scaleReading(reading,band,side):
    # adjust for screen size and noise floor 
    global rawData
    if debug :
       rawData[side][band] = reading
    reading -= noiseFloor[side][band]
    if reading <0 :
       reading = 0
    scaled = (float(reading) / (1024.0 - float(noiseFloor[side][band]))) * ys
    return int(scaled)
   
def plotData():
    # display volume bars
    global leftData, rightData
    pygame.draw.rect(screen,(0,0,0),(0,0,xs,ys),0)
    for band in range(0,7):
       pygame.draw.rect(screen,colour[6-band],((band+1)*posX,ys-leftData[6-band],posX-20,ys),0)
       pygame.draw.rect(screen,colour[band],((band+8)*posX,ys-rightData[band],posX-20,ys),0)
       if debug :
          drawWords(str(leftData[6-band]),(band+1)*posX,0)
          drawWords(str(rightData[band]),(band+8)*posX,0)          
    pygame.display.update()

def drawWords(words,x,y) :
        textSurface = pygame.Surface((len(words)*12,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        pygame.draw.rect(screen,(81,133,133), (x,y,len(words)*12,textHeight-10), 0)
        textSurface = font.render(words, True, (180,180,180), (81,133,133))
        screen.blit(textSurface, textRect)
   
def initGPIO():
    try :
       io.wiringPiSetupGpio()
    except :
       print"start IDLE with 'gksudo idle' from command line"
       os._exit(1)
    io.pinMode(pinReset,1)
    io.pinMode(pinClock,1)
    io.mcp3002Setup(70,0)   
          
def terminate(): # close down the program
    print ("Closing down please wait")
    if debug :
       print rawData
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
       if event.key == pygame.K_SPACE and not debug:
          pygame.display.toggle_fullscreen()
          fullScreen = not fullScreen
          
# Main program logic:
if __name__ == '__main__':
  try:   
     main()
  except:
    if fullScreen :
        pygame.display.toggle_fullscreen()  


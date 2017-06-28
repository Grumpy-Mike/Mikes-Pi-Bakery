#!/usr/bin/python3
# Wind Chimes using a HMC5883 magnetometer by Mike Cook
import sys, smbus
import pygame, os, time

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Wind Chimes")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT,pygame.MOUSEBUTTONDOWN])

gSpace = 70 # size of square
gSide = 9 # number of squares per side
screenSize = gSpace * gSide
screen = pygame.display.set_mode([screenSize+2,screenSize+2],0,32)
sampleC = [ (0,0,0),(175,175,130),(130,175,175),(175,130,175),(130,130,175),
            (175,130,130),(130,130,130),(183, 46, 72),(219, 55, 36),(175,130,60)]
selected = [ 0 for i in range(0,gSide*gSide)]
# default note selection
selected[0] = 1 ; selected[8] = 3 ; selected[72] = 4 ; selected[80] = 5
address = 0x1e ; sample = 1 # note to seed on click

def main():
   init()
   while 1:
     checkForEvent()
     getReading()
     findSquare()
     drawGrid()
     if fillTarget:
        time.sleep(0.4) # change this to 0.0 for more fluent response 

def drawGrid():
    rSize = gSpace-2
    hG = gSpace / 2
    pygame.draw.rect(screen,(0,0,0),(0,0,screenSize,screenSize),0) 
    for s in range (0,gSide*gSide):
        if selected[s] != 0 : # if square selected
           xp = (s % gSide)*gSpace # note modulus, or remainder, from a division %
           yp = (s//gSide)*gSpace # note the integer division //
           pygame.draw.rect(screen,sampleC[selected[s]],(xp+2,2+yp,rSize,rSize),0)
    if fillTarget:
       xp = (endSquare % gSide)*gSpace 
       yp = ( endSquare //gSide)*gSpace    
       pygame.draw.rect(screen,(0,255,0),(xp+2,yp+2,rSize,rSize),0) 
    for y in range(0,gSide+1):
       pygame.draw.line(screen,(255,255,0),(gSpace*y,0),(gSpace*y,screenSize+2),2)
    for x in range(0,gSide+1):
       pygame.draw.line(screen,(255,255,0),(0,gSpace*x),(screenSize+2,gSpace*x),2)   
    pygame.draw.line(screen,(255,0,0),(cp,cp),(endX*gSpace+hG,endY*gSpace+hG),4)
    pygame.display.update()      
                          
def findSquare():
    global endSquare,endX,endY,fillTarget
    endX = (cp-xRead)
    endY = (cp-yRead)   
    if endX <=0:
       endX = 2
    if endX >= screenSize:
       endX = screenSize -2
    if endY <= 0:
       endY = 2
    if endY >= screenSize:
       endY = screenSize -2
    endX //= gSpace
    endY //= gSpace       
    endSquare = int(endX + endY*gSide)
    if selected[endSquare] != 0:
       sounds[selected[endSquare]-1].play()
       fillTarget = True # highlight note square
    else:
       fillTarget = False
    
def toggleSquare(): # seed note from mouse click
    global selected
    mouse = pygame.mouse.get_pos()
    clickX = mouse[0] // gSpace
    clickY = mouse[1] // gSpace
    square = int(clickX + clickY*gSide)
    if selected[square] == sample:
       selected[square] = 0
    else:
       selected[square] = sample  

def init():
    global bus,cp,scale,sounds
    bus = smbus.SMBus(1) # change to 0 for original Pi
    writeI2Cbyte(0, 0x78) # Set to 8 samples @ 75Hz
    writeI2Cbyte(1, 0xC0) # 5.6 Ga full scale - gain 330
    writeI2Cbyte(2, 0x00) # Continuous sampling
    cp = screenSize/2
    scale = (cp*25)/(2047)
    soundFiles = [62,64,65,67,69,71,72,74,76]
    sounds = [ pygame.mixer.Sound("harp/"+str(soundFiles[s])+".wav")
                  for s in range(0,len(soundFiles))]
    
def getReading():
   global xRead,yRead
   xRead = readI2CwordAdjust(3) 
   yRead = readI2CwordAdjust(7)
   zRead = readI2CwordAdjust(5) # need to do this
   yRead /= scale   
   xRead /= scale
   
def readI2Cbyte(adr):
    return bus.read_byte_data(address, adr)
  
def readI2CwordAdjust(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    word = (high << 8) + low
    if (word >= 0x8000):
       return -((65535 - word) + 1)
    else:
       return word
 
def writeI2Cbyte(adr, value):
    bus.write_byte_data(address, adr, value)
    
def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global sample
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.MOUSEBUTTONDOWN :
        toggleSquare()     
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key >= pygame.K_0 and event.key <= pygame.K_9:
          sample = event.key & 0x0f
          print("Seeding note number",sample)
          
# Main program logic:
if __name__ == '__main__':    
    main()


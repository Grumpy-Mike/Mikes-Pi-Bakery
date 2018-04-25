# Bounce Drawing
# By Mike Cook March 2018
import pygame, os, time, random
import spidev, math

pygame.init() 
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Cartiesian Coordnates Sketch")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenWidth = 600 ; screenHight = screenWidth
cp = screenWidth // 2
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
backCol = (150,255,255) # background colour
standCol = (150,0,150) # standby colour
lineColBank = [(180,64,0),(255,255,0),(200,0,0),(0,0,255),(0,0,0)] # line colour
lineCol =lineColBank[0] ; colNumber = 0
polar = False ; inBuf = [0, 0]
maxRight = 1023 ;  maxLeft = 1023 # adjust for maximum

def main():
    loadResource()
    print("key s - swap controllers")
    print("key c - swap coordnate system")
    print("space - to wipe screen")
    while(1):
       checkForEvent()
       readSensor()
       display()
       
def display():
    global lastPos
    newPos = getPos()
    if lastPos[0] == newPos[0] and lastPos[1] == newPos[1]:
       return
    pygame.draw.line(screen,lineCol,(lastPos[0] ,lastPos[1] ), (newPos[0],newPos[1] ),2)
    lastPos[0] = newPos[0]
    lastPos[1] = newPos[1] 
    pygame.display.update()

def changeCords():
   global polar
   if polar :
      polar = False
      pygame.display.set_caption("Cartiesian Coordnates Sketch")
   else :
      polar = True
      pygame.display.set_caption("Polar Coordnates Sketch")

def swapControls():
   global leftC,rightC 
   if leftC == 0:
      rightC = 0
      leftC = 1
   else :
       rightC = 1
       leftC = 0
        
def getPos():
    if polar :
       r = inBuf[leftC]/maxLeft
       th = math.pi * 2 * (inBuf[rightC]/maxRight)
       x = cp * r * math.cos(th) + cp
       y = cp * r * math.sin(th) + cp
    else :
       x = inBuf[leftC]/maxLeft * screenWidth
       y = inBuf[rightC]/maxRight * screenWidth
    return [x,y]

def newDraw():
   global lastPos
   pygame.draw.rect(screen,standCol,(0,0,screenWidth,screenHight+2),0)
   pygame.display.update()
   time.sleep(2.5) # time before drawing again
   readSensor()
   lastPos = getPos()
   pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight+2),0)
   pygame.display.update()

def changeLineCol():
   global lineCol, colNumber
   colNumber += 1
   if colNumber >= len(lineColBank):
      colNumber = 0
   lineCol = lineColBank[colNumber]
    
def readSensor():
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel 
      inBuf[i] = (adc[1] & 3)<<8 | adc[2] # join two bytes together 
    
def loadResource():
   global spi,lastPos,leftC,rightC
   spi = spidev.SpiDev()
   spi.open(0,0)
   spi.max_speed_hz=1000000
   pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight),0)
   lastPos = [cp,cp]
   leftC = 0
   rightC = 1
   
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
       if event.key == pygame.K_SPACE :
          newDraw()
       if event.key == pygame.K_c :          
          changeCords() # change coordnate system
       if event.key == pygame.K_s :          
          swapControls() # change coordnate system
       if event.key == pygame.K_l :          
          changeLineCol() # change coordnate system          
       if event.key == pygame.K_d : # screen dump
          os.system("scrot")          
       
# Main program logic:
if __name__ == '__main__':    
    main()

# Bounce Test - plot inputs
# By Mike Cook March 2018
import pygame, os, time, random
import spidev

pygame.init() 
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Bounce Test")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenWidth = 1000 ; screenHight = 230
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
textHeight= 20  
font = pygame.font.Font(None, textHeight)
backCol = (150,255,150) # background colour

inBuf = [ 0, 0] 

def main():
    n=0
    loadResource()
    while(1):
       time.sleep(0.001) 
       checkForEvent()
       readSensor()
       display(n)
       n +=1
       if n > screenWidth:
         n=0
         lastX = -1; lastY = 0
         pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight+2),0)    
       
def display(n):
    global lastX,lastY
    col = (180,64,0)   
    y0 = ch0Low - inBuf[0]//9
    y1 = ch1Low - inBuf[1]//9
    if n != 0:
       pygame.draw.line(screen,col,(lastX ,lastY[0] ), (n ,y0 ),2)
       pygame.draw.line(screen,(0,64,180),(lastX ,lastY[1] ), (n ,y1 ),2)
    lastX = n
    lastY[0] = y0 ; lastY[1] = y1
    pygame.display.update()

def readSensor():
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel 
      inBuf[i] = (adc[1] & 3)<<8 | adc[2] # join two bytes together 
    
def loadResource():
   global spi,lastX,lastY,ch0Low,ch1Low
   spi = spidev.SpiDev()
   spi.open(0,0)
   spi.max_speed_hz=1000000
   pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight),0)
   lastX = -1 ; lastY = [0,0]
   ch0Low = screenHight/2 -2
   ch1Low = screenHight -2
   
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
       if event.key == pygame.K_d : # screen dump
          os.system("scrot")          
       
# Main program logic:
if __name__ == '__main__':    
    main()

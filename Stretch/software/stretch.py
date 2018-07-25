# Stretch Armstrong
# By Mike Cook June 2018
import pygame, os, time, random
import spidev

pygame.init()                   # initialise graphics interface

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Stretch")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
textHeight=26 ; font = pygame.font.Font(None, textHeight)
screenWidth = 206 ; screenHeight = 500
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)
background = (150,100,40) ; pramCol = (180,200,150)
lastReading = 0.0 ; reading = 200
Vin = 3.3 ; R1 = 270 # or replace with measured values

def main():
    global lastReading, reading
    loadResource()
    initScreen()
    while(1):
        checkForEvent()
        readSensor()
        if lastReading != reading:
          drawScreen()
        lastReading = reading
        time.sleep(0.1)
   
def drawScreen():
   pygame.draw.rect(screen,background,(0,474,screenWidth,screenHeight),0)
   pygame.draw.rect(screen,background,(0,0,screenWidth,450),0)
   drawWords(str(reading),40,478,pramCol,background)
   if reading > 600:
       drawWords(chr(0x221E),116,478,pramCol,background) # infinity
   else:    
       drawWords(str(Rs)+" "+chr(0x3a9),116,478,pramCol,background)
   stretch = 500 - reading
   if stretch > 2 :
      stretched =  pygame.transform.smoothscale( armstrong , (96,stretch) )   
      screen.blit(stretched,(54,450 - stretch))    
   pygame.display.update()

def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x
    textRect.top = y    
    screen.blit(textSurface, textRect)

def initScreen():
   pygame.draw.rect(screen,background,(0,0,screenWidth,screenHeight),0)
   drawWords("Reading  Resistance",16,454,pramCol,background)
    
def loadResource():
   global spi, armstrong
   spi = spidev.SpiDev()
   spi.open(0,0)
   spi.max_speed_hz=1000000
   armstrong = pygame.image.load("images/Armstrong.png").convert_alpha()

def readSensor():
      global reading,Rs
      adc = spi.xfer2([1,(8)<<4,0]) # request channel 
      reading = (adc[1] & 3)<<8 | adc[2] # join two bytes together
      if reading !=0:
         Rs = R1*( ( 1/ (Vin / (reading * Vin /1024) -1 ) ) )
         Rs = int(Rs) # convert into interger
      else:
         Rs = 0
   
def terminate(): # close down the program
    print ("Closing down")
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # handle events
    global reading
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_d : # screen dump
          os.system("scrot -u")
                  
# Main program logic:
if __name__ == '__main__':    
    main()

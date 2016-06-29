#!/usr/bin/env python
# All Mixup Exhibition version colour and B/W pack
# by Mike Cook June 2016

import RPi.GPIO as GPIO
import MFRC522
import time, pygame, os, sys

pygame.init() # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("All Mixed Up Exhibition")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

screenWidth = 406
screenHeight = 615
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)

numberOfCards = 20 # picture cards
numberOfBacks = 3  # background cards
card = [ pygame.image.load("CardsExhibition/R"+str(cardNumber)+".png").convert_alpha()
                  for cardNumber in range(0,numberOfCards+1)]
# three background images for each card
backImage = [ pygame.image.load("CardsExhibition/B"+str(backNumber)+".jpg")
                  for backNumber in range(0,numberOfBacks*3)]
# number of entries to match numberOfCards variable + 1
tokens = [0, 0xcc3214de,0xec0b0bde, 0xec010bde,0x8c5914de,0xecf70ade,
          0xbc23e6dd, 0xc24e6dd, 0xfce330de, 0x4ce430de, 0x9c3714de,
          0x96e2acd5,0xaa01a910,0xbd51192b,0xccb419de, 0xec9f19de,
          0x5c6ccadd, 0x1c0201de, 0xcc0101de,0x1c88fadd, 0xccba19de]

# number of entries to match numberOfBacks variable
backToken = [0x9c3131de,0xbcc8eedd,0xdc54e6dd,0x4ce430de]

robotSound = [ pygame.mixer.Sound("sounds/R"+str(sound)+".wav")
                  for sound in range(0,11)]

headRect = pygame.Rect(0,0,screenWidth,164)
bodyRect = pygame.Rect(0,165,screenWidth,224)
feetRect = pygame.Rect(0,384,screenWidth,231)
headReader = 0; bodyReader = 1; feetReader = 2

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
muxPins = [16,18,7]
cardPresent = [False,False,False]
cardID = [0,0,0]
needRedraw = True
background = 0
restartInterval = 25.0
restartTime = time.time()+restartInterval

def main():
   print "All mixed up"
   init()
   while 1:
      checkForEvent()
      if needRedraw :
         drawScreen()
      scanReaders()         
      
def scanReaders():
   global cardPresent, cardID, needRedraw, background
   for reader in range(0,3):
      setMux(reader)   
      (status,TagType) = mfRaeder[reader].MFRC522_Request(mfRaeder[reader].PICC_REQIDL)
      if status == mfRaeder[reader].MI_OK:
         (status,uid) = mfRaeder[reader].MFRC522_Anticoll()
         if status == mfRaeder[reader].MI_OK and cardPresent[reader] == False :
           cardPresent[reader] = True
           needRedraw = True
           token  = (uid[0] << 24) | (uid[1] << 16) | (uid[2] << 8) | uid[3]
           if getImageNumber(token) != 0 :
              robot = getImageNumber(token)
              cardID[reader] = robot
              if robot > 10 :
                 robot -= 10
              robotSound[robot].play() 
           else:   
              setBackground(token,reader)
           print "Card reader",reader,hex(token).rstrip("L")
      else :
         cardPresent[reader] = False # no card present
           
def drawScreen():
   global needRedraw,restartTime
   restartTime = time.time() + restartInterval
   screen.blit(backImage[background],(0,0))
   screen.set_clip(headRect)
   screen.blit(card[cardID[headReader]],(0,0)) # change 0 to 2 for inverse
   screen.set_clip(bodyRect)
   screen.blit(card[cardID[bodyReader]],(0,0))
   screen.set_clip(feetRect)
   screen.blit(card[cardID[feetReader]],(0,0)) # change 2 to 0 for inverse
   screen.set_clip(None)
   pygame.display.update()
   needRedraw = False

def getImageNumber(number):
   image = 0
   matchTry = 0
   while (matchTry < (numberOfCards+1)) and image == 0 :
      if tokens[matchTry] == number:
         image = matchTry
      matchTry +=1  
   return image

def setBackground(token, reader):
   global background
   background = 0
   for i in range(0,numberOfBacks):
      if token == backToken[i]:
         background = reader + (i*3)
      
def init():
   global mfRaeder
   for pin in range (0,3):
      GPIO.setup(muxPins[pin],GPIO.OUT) # mux pin to output 
   setMux(0)
   reader1 = MFRC522.MFRC522()
   setMux(1)
   reader2 = MFRC522.MFRC522()
   setMux(2)
   reader3 = MFRC522.MFRC522()
   mfRaeder = [reader1,reader2,reader3]
    
def setMux(n):
   mask = 1;
   for pin in range(0,3):
     if (mask & n) != 0 :
        GPIO.output(muxPins[pin], True)
     else :
        GPIO.output(muxPins[pin], False)
     mask = mask << 1
     
def freshStart():
   global restartTime, needRedraw, background 
   restartTime = time.time() + restartInterval
   background = 0
   needRedraw = True
   for i in range(0,3):
      cardID[i] = 0

def terminate(): # close down the program
    print ("Closing down")
    GPIO.cleanup()
    pygame.quit() # close pygame
    os._exit(1)
    
def checkForEvent(): # see if we need to quit
    global nextF, cardID
    if time.time() > restartTime:
       freshStart()
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          freshStart()
# Main program logic:
if __name__ == '__main__':    
    main()
        

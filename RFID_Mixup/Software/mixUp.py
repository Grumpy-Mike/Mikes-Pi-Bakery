#!/usr/bin/env python
# All Mixup by Mike Cook June 2016

import RPi.GPIO as GPIO
import MFRC522
import time, pygame, os, sys

pygame.init() # initialise graphics interface
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("All Mixed Up")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

screenWidth = 406
screenHeight = 615
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)

numberOfCards = 10 # picture cards
numberOfBacks = 3  # background cards
card = [ pygame.image.load("Cards/R"+str(cardNumber)+".png").convert_alpha()
                  for cardNumber in range(0,numberOfCards+1)]
# three background images for each card
backImage = [ pygame.image.load("Cards/B"+str(backNumber)+".jpg")
                  for backNumber in range(0,numberOfBacks*3)]
# number of entries to match numberOfCards variable + 1
tokens = [0,0x96e2acd5,0xaa01a910,0xbd51192b,0xccb419de, 0xec9f19de,
          0x5c6ccadd, 0x1c0201de, 0xcc0101de,0x1c88fadd, 0xccba19de]
# number of entries to match numberOfBacks variable
backToken = [0x9c3131de,0xbcc8eedd,0xdc54e6dd]

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
              cardID[reader] = getImageNumber(token)
           else:   
              setBackground(token,reader)
           print "Card reader",reader,hex(token).rstrip("L")
      else :
         cardPresent[reader] = False # no card present
           
def drawScreen():
   global needRedraw
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
   for i in range(0,numberOfCards+1) :
      if tokens[i] == number:
         image = i
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
   
def terminate(): # close down the program
    print ("Closing down")
    GPIO.cleanup()
    pygame.quit() # close pygame
    os._exit(1)
    
def checkForEvent(): # see if we need to quit
    global nextF, background, needRedraw, cardID
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE : # reset display
          background = 0
          needRedraw = True
          for i in range(0,3):
             cardID[i] = 0

# Main program logic:
if __name__ == '__main__':    
    main()
        

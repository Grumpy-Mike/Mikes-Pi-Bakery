#!/usr/bin/env python
# Mixup image adjustment
# by Mike Cook June 2016

import pygame, os, sys

pygame.init() # initialise graphics interface
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("All Mixed Up")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

screenWidth = 406
screenHeight = 615
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)

numberOfCards = 10 # change if you do not have this number of images to align
currentCard = 1
card = [ pygame.image.load("Alignment_folder/card"+str(cardNumber)+".jpg").convert_alpha()
                  for cardNumber in range(0,numberOfCards+1)]
needRedraw = True
offsetX = 0
offsetY = 0
saving = False

def main():
   print "All mixed up - image alignment program"
   print "Cursor keys to move image"
   print "s - to save aligned image"
   print "f - forward to next image"
   print "b - back to last image"
   while 1:
      checkForEvent()
      if needRedraw :
         drawScreen()         
                 
def drawScreen():
   global needRedraw, saving
   pygame.draw.rect(screen, (255,255,255),(0,0,screenWidth,screenHeight),0)
   screen.blit(card[currentCard],(offsetX,offsetY))
   if not saving :
      pygame.draw.line(screen,(102,204,255), (0,166), (screenWidth,166),1)
      pygame.draw.line(screen,(102,204,255), (0,384), (screenWidth,384),1)
      pygame.draw.line(screen,(102,204,255), (screenWidth/2,0), (screenWidth/2,screenHeight),1)
   pygame.display.update()
   if saving :
       saving = False
       pygame.image.save(screen,"Aligned/card"+str(currentCard)+".jpg")
       print "card image saved as Aligned/card"+str(currentCard)+".jpg"
   else :    
       needRedraw = False
   
def terminate(): # close down the program
    print ("Closing down")
    pygame.quit() # close pygame
    os._exit(1)
    
def checkForEvent(): # see if we need to quit
    global nextF, background, offsetX,offsetY,needRedraw, saving, currentCard 
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          background = 0   
       if event.key == pygame.K_RIGHT :
          offsetX += 1
          needRedraw = True
       if event.key == pygame.K_LEFT :
          offsetX -= 1
          needRedraw = True
       if event.key == pygame.K_DOWN :
          offsetY += 1
          needRedraw = True
       if event.key == pygame.K_UP :
          offsetY -= 1
          needRedraw = True
       if event.key == pygame.K_s :
          needRedraw = True
          saving = True
       if event.key == pygame.K_f : # move forword to next image
          needRedraw = True
          currentCard += 1
          if currentCard > numberOfCards :
             currentCard = 1            
       if event.key == pygame.K_b : # move back to last image
          needRedraw = True
          currentCard -= 1
          if currentCard == 0 :
             currentCard = numberOfCards

# Main program logic:
if __name__ == '__main__':    
    main()
        

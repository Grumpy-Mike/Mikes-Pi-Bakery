#!/usr/bin/env python3
#Locate LEDs on the basic track image
#Click on each LED point in turn, 
#copy and paste resulting numbers into a text editor and save it as a .csv file

import os, pygame, sys

pygame.init()
  
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("LED Racer")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT,pygame.MOUSEBUTTONDOWN])

screen = pygame.display.set_mode([920,498],0,32)
backCol = (160,160,160)
done = False

def main():
  print("Click on LEDs in turn")
  print("copy and past resulting numbers into a text editor and save it as a .csv file")
  init()
  drawScreen()
  while not done:
       checkForEvent()     
       
def drawScreen():
   screen.fill(backCol)
   screen.blit(track, (0,0) )
   pygame.display.update()

   
def init():
    global track
    track = pygame.image.load("images/Layout.jpg")    
  
def terminate(): # close down the program
    print ("Closing down")
    pygame.quit() # close pygame
    os._exit(1)
    

def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
          
    if event.type == pygame.MOUSEBUTTONDOWN :
        print(pygame.mouse.get_pos()[0],",",pygame.mouse.get_pos()[1])        

if __name__ == '__main__':
    main()

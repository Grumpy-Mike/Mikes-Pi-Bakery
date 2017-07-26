#!/usr/bin/env python3
# Maze Runner - Figit Spinner Maze runner
# By Mike Cook - July 2017

import pygame, time, os
import RPi.GPIO as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Figet Spinner Maze Runner")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

screenWidth = 500 ; screenHeight = 516
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)

xPlot = 237; yPlot = 494 ; needsRedraw = True
direction = (0,-1) # start direction
feel = [(0,1),(1,0),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
rad = 6 # radius of your marker
mazePath = [] ; restart = False
mazePath.append((xPlot,yPlot))

def main():
   global xPlot,yPlot,needsRedraw,rad,trail,progress,count,restart
   print("Figet Spinner - Return for progress - Space for reset")
   init() # GPIO
   loadResorces()
   trail = True
   setupMaze(xPlot,yPlot)
   progress = 0
   markPath()
   setupMaze(mazePath[0][0],mazePath[0][1])
   rad = 4
   end = len(mazePath) 
   while True:
      whistle.play()                   
      waitFinish()
      timeStart = time.time()
      count = 0
      while progress < end:
         checkForEvent()
         if needsRedraw:
            if trail:
               drawMaze(mazePath[progress][0],mazePath[progress][1])
            else:   
               setupMaze(mazePath[progress][0],mazePath[progress][1])            
            progress +=1
            needsRedraw = False
         if count != progress:
            progress = count
            needsRedraw = True
         if progress >= end:
            cheers.play()          
            print("Finished")
            print("Maze Run Time",int(time.time()-timeStart),"seconds")
            waitFinish()
         if restart:
            progress = end
            restart = False
      progress = 0
      setupMaze(mazePath[progress][0],mazePath[progress][1])
      time.sleep(2.0)
      
def markPath():
   global xPlot,yPlot,direction,mazePath
   print("Finding path please wait")
   step = 0
   while 1:
      checkForEvent()
      while pathClear():
        (xPlot,yPlot) = (direction[0]+xPlot,direction[1]+yPlot)
        drawMaze(xPlot,yPlot)
        mazePath.append((xPlot,yPlot))  
        if (xPlot > 255 and xPlot < 260) and (yPlot > 260 and yPlot < 268):
           print("Path found ready to play")
           return          
      findDirection()           
   
def pathClear(): # is path ahead clear
   nextPoint = (direction[0]*(rad+1)+xPlot,direction[1]*(rad+1)+yPlot)
   col = screen.get_at(nextPoint)
   if col == (255,255,255,255) :
      return True
   return False
   
def findDirection(): # where is free
   global direction
   direction = (0,0) # assume stuck
   i = 0
   while i<8:
     dirTest = (feel[i][0]*(rad+2)+xPlot,feel[i][1]*(rad+2)+yPlot)
     col = screen.get_at(dirTest)
     if col == (255,255,255,255):
       direction = feel[i]
       i = 10 # end search early
     i +=1
   
def setupMaze(x,y):
   screen.blit(mazeImage,(0,0))
   pygame.draw.circle(screen,(210,0,0),(x,y),rad,0)
   pygame.display.update()

def drawMaze(x,y):
   pygame.draw.circle(screen,(210,0,0),(x,y),rad,0)
   pygame.display.update()

def loadResorces():
   global mazeImage,cheers,whistle
   mazeImage = pygame.image.load("images/maze.png").convert_alpha()
   cheers = pygame.mixer.Sound("sounds/end.ogg")
   whistle = pygame.mixer.Sound("sounds/whistle.ogg")

def init():
   global count
   count = 0
   io.setwarnings(False)
   io.setmode(io.BCM)
   io.setup(4, io.IN, pull_up_down=io.PUD_UP)
   io.setup(23, io.OUT)
   io.add_event_detect(4, io.FALLING, callback = pulse)

def pulse(channel): # call back function
    global count
    count += 2
    io.output(23,not(io.input(23))) #optional feedback

def waitFinish():
   while pygame.mixer.get_busy():
      checkForEvent()                         

def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    io.cleanup()
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global trail,progress,restart
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          restart = True # restart game
          print("Restarting")
       if event.key == pygame.K_RETURN :
          print("Pulses from Fidget", progress // 2,"or",progress / 6,"revoloutions") 
       if event.key == pygame.K_t :
          trail = not(trail)
       if event.key == pygame.K_s :
          os.system("scrot")
          
# Main program logic:
if __name__ == '__main__':    
    main()

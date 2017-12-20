#!/usr/bin/env python3
# Pi Ring the changes - bells_play
# By Mike Cook - December 2017

import pygame, time, os, copy, random
from tkinter import filedialog
from tkinter import *

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Bells - Ring the changes")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT,
                          pygame.MOUSEBUTTONDOWN])
screenWidth = 1260 ; screenHight = 482
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
textHeight=26 ; hangY = 30 
font = pygame.font.Font(None, textHeight)
swingSpeed = 0.01 # animation rate
bellX = [60,180,320,460,620,790,973,1160]
backCol = (0,255,255) # background colour
trails = [(255,0,0),(255,255,0),(0,255,0),(0,0,255),
          (0,0,0),(255,128,0), (255,255,255), (32,120,0)]
speed = 0.4 ; running = False ; automatic = False
random.seed() ; ringLength = 8 ; filePlay = False

def main():
   global lastSequence, swapFrom, running, bellSequence
   drawLables()
   resetSequence()
   loadResources()
   print("Ring in the new - press R to ring")
   print("S to stop - F to play a file - C to ring the changes")
   while True:
      checkForEvent()
      if filePlay :
         if running:
            drawControls()
            lastSequence = fSeq[0]
            i=-1
            while i < int(len(fSeq))-1 and running:
               i += 1
               if int(len(fSeq[i])) > 0 :
                  if int(fSeq[i] !=0):
                    bellSequence = fSeq[i]
                    playPeal()
                    drawSequence()                                        
                    lastSequence = copy.deepcopy(bellSequence[:])
            running = False
      else:   
         if running:
            playPeal()
            lastSequence = copy.deepcopy(bellSequence[:])
            if swapFrom != -1: # if we need to swap
               bellSequence[swapFrom],bellSequence[swapFrom+1]=bellSequence[swapFrom+1],bellSequence[swapFrom]
            swapFrom = -1 # remove swap call
            drawControls()
            drawSequence()
            
def playPeal():
   global swapFrom, speed
   for ring in range(0,ringLength):
      showRing(ring)
      swing(bellSequence[ring])
      if ring ==2 and automatic and not(filePlay): # random swap
         swapFrom = random.randint(0,ringLength-2)
         drawControls()
         pygame.display.update()
      checkForEvent()
      time.sleep(speed)
      
def setMode(mode):
   global filePlay
   filePlay = mode
   if filePlay:
      root = Tk()
      root.filename = filedialog.askopenfilename(initialdir = "/home/pi",
           title = "Select bell method",filetypes = (("txt files","*.txt"),
           ("all files","*.*")))
      loadFile(root.filename)
      root.withdraw()
   else :
      pygame.display.set_caption("Bells - Ring the changes")
      resetSequence()
   
def loadFile(fileName):
   global fSeq, ringLength
   nameF = open(fileName,"r")
   pygame.display.set_caption("Playing - "+fileName)
   sequenceFile = nameF.readlines()
   ringLength = int(len(sequenceFile[0]) / 2)
   fSeq = [] ; k=-1
   for i in sequenceFile:
      k +=1
      ns = []
      for j in range(0,int(len(sequenceFile[k])),2):
         if i[j:j+1] != '-' and i[j:j+1] != '\n':
            n = int(i[j:j+1])-1 # to get bells 0 to 7
            ns.append(n)     
      fSeq.append(ns)
   fSeq.append(ns) # extra line at end   
   nameF.close()   
      
def showRing(n): # indicate the current ring point
   pygame.draw.rect(screen,backCol,(524,248,185,16),0)
   drawWords("^",530+n*24,248,(0,0,0),backCol)
   pygame.display.update()
   
def drawControls(): # draw swap radio buttons
   pygame.draw.rect(screen,backCol,(0,160,screenWidth,20),0)
   if filePlay:
      return
   for n in range(0,ringLength-1):
      if n == swapFrom:
         pygame.draw.rect(screen,(128,32,32),(bellX[n]+10,160,bellX[n+1]-bellX[n]-20,20),0)
         drawWords("<-- Swap -->",bellX[n]+10+n*6,160,(0,0,0),(128,32,32))
      else:
         drawWords("<-- Swap -->",bellX[n]+10+n*6,160,(0,0,0),backCol)
         pygame.draw.rect(screen,(0,0,0),(bellX[n]+10,160,bellX[n+1]-bellX[n]-20,20),1)

def drawSequence(): # display bell sequence
   screen.set_clip(0,260,screenWidth,screenHight-260)
   screen.scroll(-30,0)
   screen.set_clip(0,0,screenWidth,screenHight)
   for n in range(0,ringLength):
      t = -1 ; j = 0
      while t == -1:
         if bellSequence[j] == lastSequence[n]:
            t = j
         j +=1
      pygame.draw.line(screen,trails[lastSequence[n]],(screenWidth-50,screenHight-16-n*24),(screenWidth-30,screenHight-16-t*24),4)
   pygame.draw.rect(screen,backCol,(530,227,179,20),0)
   pygame.draw.rect(screen,backCol,(screenWidth-30,screenHight-200,16,191),0)
   for n in range(0,ringLength):
      drawWords(str(bellSequence[n]+1),530+n*24,227,(0,0,0),backCol) # horizontally
      drawWords(str(bellSequence[n]+1),screenWidth-30,screenHight-(n+1)*24,(0,0,0),backCol) # vertically   
   pygame.display.update()   
                
def drawLables():
   global textHeight
   textHeight = 26 
   pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight),0)
   for n in range(0,8):
      drawWords(str(n+1),bellX[n]-4,0,(0,0,0),backCol)
   textHeight = 36
   drawWords("<---- Sequence ---->",532,207,(0,0,0),backCol)
   
def swing(bellNumber): # animated bell swing
   global bellState
   if bellState[bellNumber] :
      for pos in range(1,11): # swing one direction
         showBell(bellNumber,pos,pos-1)
         time.sleep(swingSpeed)
      bellState[bellNumber] = 0
   else:
      for pos in range(9,-1,-1): # swing the other direction
         showBell(bellNumber,pos,pos+1)
         time.sleep(swingSpeed)
      bellState[bellNumber] = 1 
   samples[bellNumber].play()  # make sound 
   
def showBell(bellNumber,seqNumber,lastBell): # show one frame of the bell
   cRect = bells[bellNumber][lastBell].get_rect()
   cRect.move_ip((bellX[bellNumber]-plotPoints[bellNumber][lastBell][0],
                  hangY-plotPoints[bellNumber][lastBell][1]) )
   pygame.draw.rect(screen,backCol,cRect,0) # clear last bell image
   screen.blit(bells[bellNumber][seqNumber],(bellX[bellNumber]
         -plotPoints[bellNumber][seqNumber][0],
          hangY-plotPoints[bellNumber][seqNumber][1]))
   pygame.display.update()
   
def drawWords(words,x,y,col,backCol) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        textSurface = font.render(words, True, col, backCol)
        screen.blit(textSurface, textRect)
   
def loadResources(): 
   global bells, plotPoints, bellState, samples, swapIcon
   bellState = [1,1,1,1,1,1,1,1]
   scale = [12.0,11.0,10.15,9.42,8.8,8.25,7.76,7.33] # size of bell
   point = [(676, 63),(646, 73),(606, 73),(532, 75),(452, 71),
            (380,67),(290, 71),(214, 61),(154, 57),(118, 77),(114, 75) ]
   plotPoints = []
   bells = []
   for scaledBell in range(0,8):# get images of bells and scale them
      plotPoint = []
      bell = [ pygame.transform.smoothscale(pygame.image.load(
        "swing/b"+str(b)+".png").convert_alpha(),(int(792.0/scale[scaledBell]),
        int(792.0/scale[scaledBell]))) for b in range(0,11)]
      for p in range(0,11):
         p1 = int(point[p][0] / scale[scaledBell])
         p2 = int(point[p][1] / scale[scaledBell])
         plotPoint.append((p1,p2))
      bells.append(bell)
      plotPoints.append(plotPoint)
      showBell(scaledBell,0,0)   
   samples = [pygame.mixer.Sound("sounds/"+str(pitch)+".wav")
               for pitch in range(0,8)]
   
def resetSequence():
   global bellSequence, swapFrom,lastSequence
   bellSequence = [0,1,2,3,4,5,6,7]
   lastSequence = [0,1,2,3,4,5,6,7]
   swapFrom = -1
   pygame.draw.rect(screen,backCol,(0,227,screenWidth,253),0)
   drawControls()
   drawSequence()

def handleMouse(pos): # look at click for swap positions
   global swapFrom
   if filePlay :
      return
   update = False
   if pos[1] > 160 and pos[1] < 180: # swap click
      for b in range(0,ringLength-1):
         if pos[0] > bellX[b]+10 and pos[0] < bellX[b+1]+10 :
            swapFrom = b
            update = True
   if update :
      drawControls()
      pygame.display.update()
   
def terminate(): # close down the program
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global speed, running,ringLength, automatic
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_RETURN and not filePlay: # reset sequence
          resetSequence()   
       if event.key > pygame.K_3 and event.key < pygame.K_9 and not filePlay:
          ringLength = event.key & 0x0f # number of bells
          drawControls()
          drawSequence()
       if event.key == pygame.K_a : # automatic swap
          automatic = not(automatic)          
       if event.key == pygame.K_r : # run bell
          running = True
       if event.key == pygame.K_s : # stop bells
          running = False          
       if event.key == pygame.K_EQUALS : # reduce speed
          speed -= 0.04
          if speed < .08:
             speed = .08
       if event.key == pygame.K_MINUS : # increase speed
          speed += 0.04
       if event.key == pygame.K_c : # ring changes
          setMode(False)         
       if event.key == pygame.K_f : # play a file
          setMode(True)            
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())                  
          
# Main program logic:
if __name__ == '__main__':    
    main()

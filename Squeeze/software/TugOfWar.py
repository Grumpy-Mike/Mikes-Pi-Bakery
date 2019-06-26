#!/usr/bin/env python3
#Tug of war using squeeze controller
# Bu Mike Cook June 2019

import math, spidev, time
import os, pygame, sys, random

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Tug of War")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenWidth = 960 ; screenHight = 280 ; cp = screenWidth // 2
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
textHeight=22 ; font = pygame.font.Font(None, textHeight)
backCol = (160,160,160)
lastValue = [-10, -10, -10] # so you show on the first reading
screenUpdate = True ; random.seed()
nAv = 10 # number of samples to average
avPoint = [0,0,0] ; p1 = [0] * nAv ; p2 = [0] * nAv
runningAv = [p1,p2,[0]] ; average = [0.] * 3
target = 0.5 ; timeChange = 0 ; scale = 700

def main():
  global tugState, gameOver, winner
  print("Tug of War")
  init()
  while(1): # do forever
    timeChange = 0
    tugState = -cp # middle of screen   
    checkTarget()
    gameOver = False
    winner = -1 # no winer yet
    whistle.play() # start sound
    time.sleep(2.0)
    while not gameOver:
       checkForEvent()
       readVoltage()
       checkTug()
       checkTarget()
       if screenUpdate :
          drawScreen() 
          updateMeters()
    if winner == 0:      
       print("Blue Player is the winner")
       drawWords("Winner        ",123,159,(0,0,0),(20,178,155))
    else:   
       print("Yellow Player is the winner")
       drawWords("Winner            ",742,159,(0,0,0),(20,178,155))
    pygame.display.update()
    end.play() # end sound
    print("Press space for another game")
    time.sleep(3.0)
    while gameOver:
      checkForEvent()
    
def checkTug():
  global tugState,screenUpdate,gameOver,winner
  #check to see if anyone has won
  if tugState <= -869:
    gameOver = True
    winner = 0
    return
  if tugState >= -37:
    gameOver = True
    winner = 1
    return
  #check to see if anyone has scored
  p1 = abs(average[0] - average[2])
  p2 = abs(average[1] - average[2])
  if p1 < p2 : #player 1 closest
    if p1 < 40:
      tugState -= 1
      screenUpdate = True
  else:
    if p2 < 40:
      tugState += 1
      screenUpdate = True       

def checkTarget():
   global target, timeChange
   if time.time() < timeChange:
      return
   temp = random.uniform(0.2,0.8) 
   target = int(temp*scale) 
   average[2] = target
   timeChange = time.time() + random.uniform(3.2,6.8)
   drawScreen()
   updateMeters()
   
def drawScreen():
   screen.fill(backCol)
   for i in range(0,3):
      screen.blit(meter, (meterPositionX[i],meterPositionY[i]) )
   screen.blit(rope, (tugState,190) )
   drawWords("Target",447,159,(0,0,0),(20,178,155))
   drawWords("Blue Player",123,159,(0,0,0),(20,178,155))
   drawWords("Yellow Player",742,159,(0,0,0),(20,178,155))
   pygame.draw.line(screen,(0,0,0),(64,188),(64,272),4)
   pygame.draw.line(screen,(0,0,0),(896,188),(896,272),4)
   pygame.display.update()

def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect
   
def init():
    global meter, rope, meterPositionX, meterPositionY, spi,whistle, end
    whistle = pygame.mixer.Sound("sounds/whistle.ogg")
    end = pygame.mixer.Sound("sounds/end.ogg")
    meter = pygame.image.load("images/MeterPC.png").convert_alpha()
    rope = pygame.image.load("images/rope.png").convert_alpha()
    meterPositionX=[10,638,324]
    meterPositionY=[10,10,10]
    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.max_speed_hz=1000000     
    
def readVoltage():
   global screenUpdate, average, avPoint,lastValue, runningAv
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel
      reading = (adc[1] & 3)<<8 | adc[2] # join two bytes together
      runningAv[i][avPoint[i]] = reading
      avPoint[i]+=1
      if avPoint[i] >= nAv:
        avPoint[i] = 0
      average[i] =  0 
      for j in range(0,nAv): # calculate new running average
         average[i] += runningAv[i][j]
      average[i] = average[i] / nAv      
      if abs(lastValue[i] - average[i]) > 8 or (average[i] == 0 and lastValue[i] !=0):
         lastValue[i] = average[i]
         screenUpdate = True      

def updateMeters():
    global screenUpdate, average
    for i in range(0,3):
       plot = constrain(average[i]/scale,0.0,1.0)
       angle = (math.pi * ((-plot))) + (1.0 * math.pi)
       mpX = 146 + meterPositionX[i]
       mpY = 146 + meterPositionY[i]
       dx = mpX + 140 * math.cos(angle) 
       dy = mpY - 140 * math.sin(angle) 
       pygame.draw.line(screen,(50,50,50),(mpX,mpY),(dx,dy),2)
       screenUpdate = False
    pygame.display.update()
    
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))
  
def terminate(): # close down the program
    print ("Closing down")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
    
def checkForEvent(): # see if we need to quit
    global reading, screenUpdate, average, gameOver
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          gameOver = False

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Rocket Rescue - Side scrolling Game
# By Mike Cook - July 2019

import os, pygame, sys, csv, time, spidev, random

pygame.init()     # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Rocket Rescue")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([1200,420],0,32)
textHeight= 36;font =pygame.font.Font(None, textHeight)
backCol = (0,0,0) ; start = False ; random.seed()
scale = [4600, 4600] ; nAv = 10 # samples to average
avPoint = [0.0,0.0] ; average = [0.0,0.0]
speed =[0.0,0.0]; rollIndex=0; rPhase = 0 #rescue phase
p1 = [0] * nAv  ; p2 = [0] * nAv ; runningAv = [p1,p2]

def main():
   global start
   init() ; setUpPrams() # set up variables
   while True:
     time.sleep(1.5)
     intro.play()  # intro music
     while not start: # until space bar is pressed
       splashScreen()
       checkForEvent()
     start = False ; intro.play()  # intro music
     lastRedraw = time.time()
     while not done : # for the duration of the mission
        checkForEvent()
        readVoltage()
        updatePosition()
        if time.time() - lastRedraw >0.05 : # 18 FPS
          drawScreen(rollIndex)
          checkCollide()
          lastRedraw = time.time()
     missionResult() ; time.sleep(2)
     setUpPrams() # set up next run

def setUpPrams():
   global manRect,astLst,place,astroSpeed,done
   global colRect,rPhase,mission,astroPosX,astroPosY
   done = False ; rPhase = 0 ; mission = False
   manRect.x = 1100 ; manRect.y = 320
   place[0] = 0 ; place[1] = 0
   for i in range (0,nA):
      astLst[i].x = random.randint(160,890)
      astLst[i].y = random.randint(150,400)
      astroPosX[i] = float(astLst[i].x)
      astroPosY[i] = float(astLst[i].y)
      astroSpeed[i] = ((0.5-random.random())/100.0, ((0.5-random.random())/100.0))
      #astroSpeed[i] = (0.0,0.0) # for no movement
      colRect[i].x = astLst[i].x +7 # collision Rect
      colRect[i].y = astLst[i].y +6

def init():
    global spi,ship,place,lastPos,minLim,maxLim,drift
    global shipRectF,sRecRc,astroPosX,astroPosY
    global rectC,astro,man,manRect,astLst,astroSpeed
    global nA,breakUpR,breakUpRect
    global colRect,shipR,splash,sNum,manSplash,breakUp
    global cheers,confirmed,dock,intro,bell,crash
    sNum = 0 ; place = [400.0,230.0] # X/Y position
    lastPos = [-20,-20] ; minLim = [-10,-10] # X/Y
    maxLim = [1080, 352] # limits on ship placement
    drift = [ -0.05, 0.05 ] # no input movement
    cheers = pygame.mixer.Sound("sounds/end.ogg")
    confirmed = pygame.mixer.Sound("sounds/done.ogg")
    dock = pygame.mixer.Sound("sounds/hardDock.ogg")
    intro = pygame.mixer.Sound("sounds/Intro.ogg")
    bell =  pygame.mixer.Sound("sounds/BellToll.wav")
    crash = pygame.mixer.Sound("sounds/overboard.ogg")
    spi = spidev.SpiDev() ; spi.open(0,0)
    spi.max_speed_hz=1000000
    splash = [pygame.image.load("images/Splash_"+ str(i)+".png").convert_alpha() for i in range(0,18) ]
    manSplash = pygame.image.load("images/manSplash.png").convert_alpha()
    shipRectF = pygame.Rect(82,18,37,48)
    ship = [pygame.image.load("images/SpaceCargo_"+ str(i)+".png").convert_alpha() for i in range(0,12) ]
    shipR = [pygame.transform.flip(ship[i],True,False) for i in range(0,12) ]
    breakUp = [pygame.image.load("images/Cargo_"+ str(i)+".png").convert_alpha() for i in range(0,14) ]
    breakUpR = [pygame.transform.flip(breakUp[i],True,False) for i in range(0,14)]
    breakUpRect = breakUpR[0].get_rect()
    astro = pygame.image.load("images/Astro.png").convert_alpha()
    nA = 10 # number of asteroids
    astLst = [astro.get_rect() for i in range(nA)]
    colRect = [astro.get_rect().inflate(-14,-12) for i in range(nA)]
    astroPosX = [0.0] * nA ; astroPosY = [0.0] * nA
    astroSpeed = [(0.005,0.005)] * nA
    man = pygame.image.load("images/Sman.png").convert_alpha()
    manRect = man.get_rect()
    rectC =[(10,4,30,53),(11,6,31,45),(9,7,34,42),
            (9,11,32,34),(9,11,32,30),(11,13,30,26),
            (12,14,30,21),(12,17,31,17),(14,15,23,18),
            (14,13,25,25),(15,10,17,29),(15,9,20,32)]
    sRecRc=[pygame.Rect(rectC[i]) for i in range(0,12)]

def getRoll(y):
   r = int(12*(290-y)/290)
   r = constrain(r,0,11)
   return r

def constrain(val,min_val,max_val):
   return min(max_val,max(min_val,val))

def checkCollide():
   global rPhase, done, mission
   if rPhase:
      if place[0] <= minLim[0]:
         done = True ; mission = True # mission success
   else:
      if shipRectF.colliderect(manRect):
         dock.play() ; rPhase = 1
   if shipRectF.collidelist(colRect) > -1 or shipRectR.collidelist(colRect) > -1:
      crash.play() # sound for collision
      distructSeq() ; time.sleep(3.0)
      done = True ; mission = False # mission fail

def splashScreen():
   global sNum
   pygame.draw.rect(screen,backCol,(0,0,1200,420),0)
   screen.blit(splash[sNum],(280,-40 ))
   drawWords("Space bar to start",513,369)
   pygame.display.update() ; sNum += 1
   if sNum >=18:
     sNum = 0
   time.sleep(0.1)

def missionResult(): # display failed / success
   global sNum
   pygame.draw.rect(screen,backCol,(0,0,1200,420),0)
   screen.blit(splash[sNum],(280,-40 ))
   if mission: # mission True = success
      confirmed.play() # sound for success
      screen.blit(manSplash,(130,100 ))
      drawWords("Rescue Successful",513,369)
      pygame.display.update()
      time.sleep(1.0)
      cheers.play() # applause
   else:
      bell.play() # sound for success
      drawWords("Rescue Failed",513,369)
      pygame.display.update() ; time.sleep(2)

def distructSeq():
   for j in range(0,14):
      pygame.draw.rect(screen,backCol,(0,0,1200,420),0)
      for i in range(0,nA):
         screen.blit(astro,(astLst[i].x,astLst[i].y))
      if rPhase:
         screen.blit(breakUpR[j],(place[0],place[1]))
      else:
         screen.blit(breakUp[j],(place[0],place[1]))
      pygame.display.update() ; time.sleep(0.1)

def drawScreen(index):
   global shipRectF, shipRectR
   pygame.draw.rect(screen,backCol,(0,0,1200,420),0)
   #pygame.draw.rect(screen,(192,192,0),shipRectF,0)
   #pygame.draw.rect(screen,(192,192,0),shipRectR,0)
   if rPhase:
      screen.blit(shipR[index],(place[0],place[1]) )
   else:
      screen.blit(ship[index],(place[0],place[1]) )
   for i in range(0,nA):
      screen.blit(astro,(astLst[i].x,astLst[i].y) )
      #pygame.draw.rect(screen,(192,192,0),colRect[i],0)
   if not rPhase:
      screen.blit(man,(manRect.x,manRect.y))
   pygame.display.update()

def drawWords(words,x,y) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x ; textRect.top = y
        pygame.draw.rect(screen,(102,204,255),(x,y,14,textHeight-10),0)
        textSurface = font.render(words, True, (192,192,0),backCol)
        screen.blit(textSurface, textRect)

def updatePosition():
  global place, update,lastPos, speed, astroPosX
  global astroPosY,colRect,rollIndex,rPhase,shipRectR
  for i in range(0,2):
     if i==0:
        place[i] += speed[i] + drift[i]
     else:
        place[i] -= speed[i] - drift[i]
     place[i] = constrain(place[i],minLim[i],maxLim[i])
     if lastPos[i] != int(place[i]):
        update = True ; lastPos[i] = int(place[i])
        rollIndex = getRoll(place[1])
  if update:
    shipRectR=sRecRc[rollIndex]
    if rPhase: # rescue phase 0 = inbound / 1 = back
      shipRectF.x = place[0]+12;shipRectF.y=place[1]+18
      shipRectR.x = place[0] + 118 -rectC[rollIndex][2]
      shipRectR.y = place[1] + rectC[rollIndex][1]
    else:
      shipRectF.x = place[0]+82;shipRectF.y=place[1]+18
      shipRectR.x = place[0] + rectC[rollIndex][0]
      shipRectR.y = place[1] + rectC[rollIndex][1]

  for i in range(0,2):
     for i in range(0,nA):
       xp = astroPosX[i] ; yp = astroPosY[i]
       astroPosX[i] += astroSpeed[i][0]
       astroPosY[i] += astroSpeed[i][1]
       if int(xp) != int(astroPosX[i]) or int(yp) != int(astroPosY[i]):
          colRect[i].x = astLst[i].x + 7
          colRect[i].y = astLst[i].y + 6
          astLst[i].x = int(astroPosX[i])
          astLst[i].y = int(astroPosY[i])
          if astLst[i].x > 1250: #X past right side
             astroPosX[i] = -48.0 ; astLst[i].x = -48
          if astLst[i].y > 420:   #Y past the bottom
             astroPosY[i] =  -44.0 ; astLst[i].y = -44
          if astLst[i].x < -50:   #X past left side
             astroPosX[i] = 1250.0 ; astLst[i].x = 1250
          if astLst[i].y < -44:   #Y over the top
             astroPosY[i] =  420.0 ; astLst[i].y = 420

def readVoltage():
   global average, avPoint, speed, runningAv
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel
      reading = (adc[1] & 3)<<8 | adc[2] # join bytes
      runningAv[i][int(avPoint[i])] = reading
      avPoint[i]+=1
      if avPoint[i] >= nAv:
        avPoint[i] = 0
      average[i] =  0
      for j in range(0,nAv): # new running average
         average[i] += runningAv[i][j]
      average[i] = average[i] / nAv
      speed[i] = average[i] / scale[i]

def terminate(): # close down the program
    print("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)

def checkForEvent(): # see if we need to quit
    global start, done
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_RETURN :
          done = True
       if event.key == pygame.K_SPACE :
          start = True

# Main program logic:
if __name__ == '__main__':
    main()

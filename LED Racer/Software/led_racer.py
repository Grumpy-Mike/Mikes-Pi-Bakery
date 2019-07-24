#!/usr/bin/env python3
#LED Racer - by Mike Cook June 2019
# Needs to run in supervisor mode
# Can take over 5 seconds to initialise

import os, pygame, sys, csv, time, spidev
# comment out next line if no LEDs attached
import board, neopixel 

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("LED Racer")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([920,498],0,32)
textHeight=22 ; font = pygame.font.Font(None, textHeight)
done = False ; trackLEDs = False ; screenUpdate = False
lastPos = [0,0]
position = [0.0,0.0] # progress of player
lap = [0,0] ; raceLaps = 1 # number of laps in a race
nAv = 10 # number of samples to average
avPoint = [0.0,0.0] ; average = [0.0,0.0]  ; speed = [0.0,0.0]
p1 = [0] * nAv  ; p2 = [0] * nAv ; runningAv = [p1,p2]
backCol = (180,180,180) ; black = (0,0,0)
scale = [5000, 4100] # adjust if two controllers are not the same

def main():
  global position,lap,screenUpdate, done, winner, speed
  print("LED Racer - use number keys to set the number of laps")
  init()
  initLEDs() # comment out if no LEDs attached
  while 1:
     winner = -1 ; speed[0] = 0 ; speed[1] = 0
     position = [0.0,0.0] ; lap[0] = 0 ; lap[1] = 0
     drawScreen(0,0) ; time.sleep(2.0)     
     whistle.play()
     while not done:
        time.sleep(0.005)    
        checkForEvent()
        readVoltage()
        updatePosition() 
        if screenUpdate :
          drawScreen(path[int(position[0])],path[int(position[1])])
          updateLEDs(path[int(position[0])],path[int(position[1])])
          screenUpdate = False
     drawWords("press space for a new race",350,430,black,backCol)
     pygame.display.update()
     end.play()
     while done: # wait for space bar or quit
        checkForEvent()
      
def updatePosition():
  global position, screenUpdate, lap, lastPos, done, winner, speed
  for i in range(0,2):
     position[i] += speed[i] + speedChange[int(position[i])]
     if lastPos[i] != int(position[i]):
        screenUpdate = True
        lastPos[i] = int(position[i])
     if position[i] >=len(path):
        position[i] = 0
        lap[i] += 1
        if lap[i] >= raceLaps:
          winner = i
          done = True
          speed[0] = 0 ; speed[1] = 0

def updateLEDs(pos0,pos1):
    global pixels
    if(trackLEDs):
       pixels.fill((0, 0, 0))
       if pos0 == pos1:
         pixels[pos1] = (255,0,255)
       else:
         pixels[pos0] = (0,100,200)
         pixels[pos1] = (200,200,0)
       pixels.show()       
           
def drawScreen(pos0,pos1):   
   screen.blit(track, (0,0) )
   pygame.draw.rect(screen,backCol,(0,399,920,99),0)   
   drawWords("Blue Car",35,407,(0,100,200),backCol)
   drawWords("Yellow Car",630,407,(140,140,0),backCol)
   drawWords("Lap",35,430,black,backCol)
   drawWords("Lap",630,430,black,backCol)
   drawWords("Speed",35,450,black,backCol)
   drawWords("Speed",630,450,black,backCol)
   drawWords(str(raceLaps)+" Lap Race",390,407,black,backCol)
   drawWords(str(lap[0]), 87,430,black,backCol)
   drawWords(str(lap[1]), 688,430,black,backCol)
   drawWords(str(int(speed[0]*100)), 87,450,black,backCol)
   drawWords(str(int(speed[1]*100)), 688,450,black,backCol)   
   if pos0 == pos1:
      pygame.draw.rect(screen,(200,0,200),(led_pointX[pos0],led_pointY[pos0],10,10),0)
   else:
      pygame.draw.rect(screen,(0,100,200),(led_pointX[pos0],led_pointY[pos0],10,10),0)
      pygame.draw.rect(screen,(200,200,0),(led_pointX[pos1],led_pointY[pos1],10,10),0)
   if winner !=-1:
     screen.blit(flag, (64,122) )
     if winner == 0:
       screen.blit(flag, (145,402) )
     else:
       screen.blit(flag, (761,402) )   
   pygame.display.update()

def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def readVoltage():
   global average, avPoint, speed, runningAv
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel
      reading = (adc[1] & 3)<<8 | adc[2] # join two bytes together
      runningAv[i][int(avPoint[i])] = reading
      avPoint[i]+=1
      if avPoint[i] >= nAv:
        avPoint[i] = 0
      average[i] =  0 
      for j in range(0,nAv): # calculate new running average
         average[i] += runningAv[i][j]
      average[i] = average[i] / nAv
      speed[i] = average[i] / scale[i]
   
def init():
    global track, flag, led_pointX, led_pointY, path, spi, speedChange, whistle, end
    whistle = pygame.mixer.Sound("sounds/whistle.ogg")
    end = pygame.mixer.Sound("sounds/end.ogg")
    track = pygame.image.load("images/Layout.jpg")
    flag = pygame.image.load("images/flag.png").convert_alpha()
    path = [] # the sequence of LED numbers to make a lap
    for i in range(0,97):
      path.append(i)
    for i in range(129,184):
      path.append(i)
    for i in range(50,129):
      path.append(i)
    #print('number of steps in a lap',len(path))  
    led_pointX = []
    led_pointY = []
    x_Off = -5
    y_Off = -5
    with open('Points.csv',newline='') as File:
        reader = csv.reader(File)
        for row in reader:
            led_pointX.append(int(row[0])+x_Off)
            led_pointY.append(int(row[1])+y_Off)
    speedChange = [0.0] * len(path) # speed increment start off with zero
    # for bridge
    for i in range(22,32):
      speedChange[i] = -0.12 # retarding speed on up
    for i in range(33,43):
      speedChange[i] = 0.1 # increasing speed on down  
    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.max_speed_hz=1000000     

def initLEDs():
    global pixels, trackLEDs
    trackLEDs = True
    pixel_pin = board.D18
    num_pixels = 184
    ORDER = neopixel.GRB
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.15,
                               auto_write=False, pixel_order=ORDER)
    updateLEDs(0,0)
      
def terminate(): # close down the program
    pygame.mixer.quit()    
    pygame.quit() # close pygame
    if trackLEDs :
       pixels.fill((0, 0, 0)) # turn off LEDs
       pixels.show()
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global reading, screenUpdate, average, done, raceLaps
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          done = False
       if event.key == pygame.K_RETURN :
          done = True # reset a race
          screenUpdate = True
       if event.key > pygame.K_0 and event.key <= pygame.K_9 :
         raceLaps = event.key - pygame.K_0
         screenUpdate = True

if __name__ == '__main__':
    main()

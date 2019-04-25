#!/usr/bin/env python3
# coding=utf-8
# Test with the colour sensor and distance
# By Mike Cook March 2019

import time
from pylgbst import *
from pylgbst.movehub import MoveHub, COLORS
from pylgbst.peripherals import EncodedMotor
import pygame, os

pygame.init()
pygame.display.set_caption("Distance colour test")
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenWidth = 80 ; screenHight = screenWidth*2
cp = screenWidth // 2
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)

tileColours = [ (0,0,0), (0,0,0),(0,0,0), (0,0,255), (128,128,255), (0,255,255), (0,255,0), (255,255,0), (255,128,0), (255,0,0), (255,255,255)]  
shutDown = False
update = False 
refTime = time.time()
lastColour = 255 ; updateColour = 0
tileDistance = 0.0
currentMotor = 0
motorUpdate = True
logFile = open("white.csv","w") # change file name to reflect tile tested

def main():
  global update
  print("Colour sensor test start with tile against sensor")
  conn=get_connection_auto()
  print("Hub connected - press Green button to end")
  print("Starting scan")
  try:
    movehub = MoveHub(conn)
    init(movehub)
    while not shutDown and currentMotor <= 1480:
      checkForEvent()
      displayPrams(movehub)

  finally:
    retMotor()
    logFile.close()
    print("Shutting down")
    movehub.button.unsubscribe(call_button)
    movehub.color_distance_sensor.unsubscribe(callback_colour)
    conn.disconnect()
    pygame.quit()

def init(movehub):
   global motor, shutDown
   motor = None
   movehub.button.subscribe(call_button)
   movehub.color_distance_sensor.subscribe(callback_colour, granularity=0)
   if isinstance(movehub.port_D, EncodedMotor):
        print("Rotation motor is on port D")
        motor = movehub.port_D
   elif isinstance(movehub.port_C, EncodedMotor):
        print("Rotation motor is on port C")
        motor = movehub.port_C
   else:
        print("Motor not found on ports C or D")
        shutDown = True

def displayPrams(movehub):
    global lastColour, updateColour, motorUpdate
    if updateColour > 5 and motorUpdate:
      print("Colour %s number %s: sensor distance: %.2f real distance: %.2f" %
            (COLORS[correctColour(lastColour)],correctColour(lastColour), metricDistance(tileDistance), angle_distance(currentMotor)))
      logFile.write("%s, %s, %.2f,%.2f\n" %
            (COLORS[correctColour(lastColour)],correctColour(lastColour), metricDistance(tileDistance), angle_distance(currentMotor)))
      if correctColour(lastColour) != 255:
          screen.fill(tileColours[correctColour(lastColour)])
      else :
          screen.fill((128,128,128))
          for j in range(0,screenHight,10) :
             if (j % 20) == 0:
                t = 10
             else:
                t = 0  
             for i in range(t,screenWidth,20) :
               pygame.draw.rect(screen, (96,96,96), (i,j,10,10),0)
      pygame.display.update()   
      incMotor()

def metricDistance(measure):
   if measure != None:    
       metric = measure * 24.5  # distance in mm
   else:
      metric = 0
   return metric   

def angle_distance(position):
   dist = 31.5 * position / 1480.0
   return dist
  
def callback_colour(colour, distance): 
    global lastColour, updateColour, tileDistance
    lastColour = colour
    tileDistance = distance
    updateColour += 1

def correctColour(colour):                 
    correctColour = colour
    if colour == 5: # to correct for error in sensor
      correctColour = 6
    return correctColour

def incMotor():
   global currentMotor, motorUpdate, updateColour
   inc = 10
   currentMotor += inc
   motor.angled(-inc, 1.0)
   motorUpdate = True
   updateColour = 0
     
def retMotor(): # return motor up against sensor
   global currentMotor, motorUpdate, updateColour
   print("Returning motor")
   motor.angled(currentMotor, 0.5)
   time.sleep(1.0) # allow motor to return
   currentMotor = 0
   motorUpdate = True
   updateColour = 0
   
def call_button(is_pressed): # shut down on hub button press
   global shutDown
   if not is_pressed :
     shutDown = True    
   
def checkForEvent(): # see if we need to quit
    global shutDown
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         shutDown = True
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          shutDown = True
       if event.key == pygame.K_SPACE :
          incMotor()
       if event.key == pygame.K_RETURN :
          retMotor()   
   
if __name__ == '__main__':
    main()

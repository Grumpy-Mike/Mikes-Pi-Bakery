#!/usr/bin/env python
# String Pong a Neopixel one dimensional pong - 2 player
# using the wiring RPi libiary
# By Mike Cook June 2015

import time, random, os
import RPi.GPIO as io
from neopixel import *

DATA_PIN  = 18 # pin connected to the NeoPixels
NUM_PIXELS = 240 # number of LEDs 240 LEDs in 4 meters
try :
   io.setmode(io.BCM)
   io.setwarnings(False)
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)

pixels = Adafruit_NeoPixel(NUM_PIXELS,DATA_PIN,800000,5,False)

bat1pin = 3
bat2pin = 2
bat1 = bat2 = 1
serve = False
ballDir = True
toServe = 0 # player to serve next
slugLength = 5
hitPoint1 = hitPoint2 = -1
lastTime = time.time()
interval = 0.1 # delay between frames
insertPlace = 0
slugCol = 5

red =   [ 204,  0, 255, 255, 255, 255]
green = [ 102, 255,  0,  0,  153,  225]
blue =  [ 0,   255, 255, 0,  153,  0]
ballSpeed  = [ 0.005, 0.01, 0.015, 0.020, 0.025, 0.03 ]

def main() :
   global lastTime, interval, ballDir, insertPlace, serve, slugLength, hitPoint1,hitPoint2,slugCol
   init()
   while(True):  
      checkBat1()
      checkBat2()
     # advance the ball
      if ((time.time() - lastTime) > interval) & serve:
        lastTime = time.time()
        if(ballDir) :
           insertPlace += 1
        else :
           insertPlace -= 1
           
        if (insertPlace + slugLength) < 0 : # hit the player 1 end
            insertPlace = -slugLength  
            ballDir = not ballDir 
            hitPoint2 = -1 # clear the other players hit position
            if hitPoint1 == -1 or hitPoint1 > slugLength :  # failed to hit or too early
                 endRally(0) # tidy up an wait for serve          
            else :
                 slugCol = hitPoint1 # change colour for next rally
                 interval = ballSpeed[slugCol]            
        
        if insertPlace > NUM_PIXELS : # hit the player 2 end
           insertPlace = NUM_PIXELS-1
           ballDir = not ballDir
           hitPoint1 = -1 # clear other players hit position
           if hitPoint2 == -1 or (NUM_PIXELS -1 - hitPoint2) > slugLength :  # failed to hit or too early
                 endRally(1) # tidy up an wait for serve          
           else :
               slugCol = NUM_PIXELS -1 - hitPoint2 # change colour for next rally
               interval = ballSpeed[slugCol]
      if serve :
         place(insertPlace) # don't update if we have just missed the ball
         
def init() :
   global insertPlace, interval
   print"String Pong - by Mike Cook"
   print"Blue LED - you swung too soon"
   print"Green LED - you swung in time"
   print"No LED - you swung too late"
   print"White LED - serve when you are ready"
   pixels.begin() # This initializes the NeoPixel library.
   setupStart()
   print"Please ignore this stupid warning:-"   
   io.setup(bat1pin,io.IN, pull_up_down = io.PUD_UP)
   io.add_event_detect(bat1pin,io.FALLING, callback=buttonPress, bouncetime=30)
   io.setup(bat2pin,io.IN, pull_up_down = io.PUD_UP)
   io.add_event_detect(bat2pin,io.FALLING, callback=buttonPress, bouncetime=30)
   insertPlace = -slugLength
   interval = ballSpeed[slugCol]
   print"Player",toServe+1,"to serve"
   
def buttonPress(number): #call back function
   global bat1,bat2
   if number == 2:
      bat2 = 0
   else :
      bat1 = 0
    
def endRally(player):
     global serve,toServe,bat1,bat2,interval,slugCol
     print"out"
     bat1 = bat2 = 1
     serve = False
     time.sleep(1.0) # leave it
     wipe()
     pixels.show() # clear display
     time.sleep(0.8)   # leave blank for a time
     toServe = player
     print"Player",player+1,"to serve"
     setupStart()
     bat1 = bat2 = 1
     if ballSpeed[slugCol] == ballSpeed[0] :
        slugCol = random.randint(2,5)
        interval = ballSpeed[slugCol]

def checkBat1():
  global serve, hitPoint1,hitPoint2, bat1
  if bat1 == 0 : 
    bat1 = 1
    if (serve==False) & (toServe == 0) :
       serve=True # put ball in service
       print"serve 1"
       hitPoint1 = hitPoint2 = -1
    else :   # trying to hit the ball
       if hitPoint1 == -1 : # only record the first hit
           hitPoint1 = slugLength + insertPlace


def checkBat2():
  global serve, hitPoint1,hitPoint2, bat2 
  if bat2 == 0 :
    bat2 = 1 
    if (serve==False) & (toServe == 1) :
       serve=True # put ball in service
       print"serve 2"
       hitPoint1 = hitPoint2 = -1
    else :   # trying to hit the ball
       if hitPoint2 == -1 : # only record the first hit
         if(insertPlace != NUM_PIXELS) : 
            hitPoint2 = insertPlace

def place(point):
  global hitPoint1,hitPoint2
  wipe()
  for i in range(0, slugLength) : # put the slug in the buffer
    if (i+ point) >= 0 & ((i+ point) < NUM_PIXELS) :
       pixels.setPixelColor(i+ point,Color(red[slugCol],green[slugCol],blue[slugCol]))
  # set the end LEDs acording to the hit none - no hit ** blue - too soon ** green - good hit
  if(hitPoint1 != -1):
       if(hitPoint1 > slugLength) :
         pixels.setPixelColor(0, Color(0,0,128)) 
       else :
         pixels.setPixelColor(0, Color(0,128,0))

  if hitPoint2 != -1 :
       if hitPoint2 < ( NUM_PIXELS- 1 - slugLength) : # bat too soon
          pixels.setPixelColor(NUM_PIXELS -1, Color(0,0,128)) 
       else :
          pixels.setPixelColor(NUM_PIXELS -1, Color(0,128,0))
  pixels.show()
 
def setupStart(): # set display waiting to serve 
  wipe()
  if toServe == 0:
     pixels.setPixelColor(0, Color(128,128,128))
  else :
     pixels.setPixelColor(NUM_PIXELS-1, Color(128,128,128)) 
  pixels.show()

def wipe():
    for i in range(0,pixels.numPixels()):
       pixels.setPixelColor(i, Color(0,0,0)) 

# Main program logic follows:
if __name__ == '__main__':
    main()

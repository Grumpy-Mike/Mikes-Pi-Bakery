# Magic mirror display
# By Mike Cook - January 2016

import time, os, random
import wiringpi2 as io
from neopixel import *

random.seed()
DATA_PIN  = 18 # pin connected to the NeoPixels
NUM_PIXELS = 16 # number of LEDs in the spiral

try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)
   
pixels = Adafruit_NeoPixel(NUM_PIXELS,DATA_PIN,800000,5,False)
  
sensorPins = [17,24,23,27]
shutDownPin = 26
pattern = 0
patternTimeSteps = [0.5, 0.08, 0.05, 0.2, 0.01] # time spent in each step
patternStep = 0 ; patternTemp = 0 ; patternTemp2 = 0
col = [ (255,0,0),(0,255,0),(0,0,255),(255,255,255),
        (255,0,0),(0,255,0),(0,0,255),(255,255,255) ]

def main():   
   initGPIO()   
   while True:
     if io.digitalRead(shutDownPin) == 0 :
        os.system("sudo shutdown -h now") # to prepare for power down.
     checkForDistance()
     advancePattern()
     time.sleep(patternTimeSteps[pattern])
     
def advancePattern(): # next step in LED pattern
   global patternStep, patternTemp, patternTemp2
   if pattern == 0:
      return # nothing to do
   if pattern == 1 : # Radar scan
     if patternStep == 0:
        patternTemp +=1
        if patternTemp >3 :
          patternTemp = 0
     wipe()
     pixels.setPixelColor(patternStep,Color(col[patternTemp][0],col[patternTemp][1],col[patternTemp][2]))  
     updateStep()
     return
   if pattern == 2 : # Colour wipe
      if patternStep == 0:
         patternTemp +=1
         if patternTemp >3 :
            patternTemp = 0
      pixels.setPixelColor(patternStep,Color(col[patternTemp][0]  ,col[patternTemp][1] ,col[patternTemp][2] ))  
      updateStep()   
      return
   if pattern == 3 : # Multicolour riot
      wipe()
      off = patternStep & 0x03
      for L in range(0,NUM_PIXELS,4):         
         pixels.setPixelColor(L,   Color(col[off][0]  ,col[off][1] ,col[off][2] ))
         pixels.setPixelColor(L+1, Color(col[off+1][0],col[off+1][1],col[off+1][2]))
         pixels.setPixelColor(L+2, Color(col[off+2][0],col[off+2][1],col[off+2][2]))
         pixels.setPixelColor(L+3, Color(col[off+3][0],col[off+3][1],col[off+3][2]))
      updateStep()
      return
   if pattern == 4 : # Slow colour cycle
      if patternStep == 0:
         patternTemp += 5
         if patternTemp > 255:
            patternTemp = 0
      pixels.setPixelColor(patternStep, Hcol(((patternStep * 256 / NUM_PIXELS) + patternTemp) & 255))         
      updateStep()      
      return
   
def initGPIO():
   for pin in range (0,4):
      io.pinMode(sensorPins[pin],0) # input
      io.pullUpDnControl(sensorPins[pin],2) # activate pull ups
   io.pinMode(shutDownPin,0) # input
   io.pullUpDnControl(shutDownPin,2) # activate pull ups
   pixels.begin() # This initialises the NeoPixel library.   
      
def updateStep():
   global patternStep
   patternStep +=1
   if patternStep >= NUM_PIXELS :
      patternStep =0
   pixels.show()
   
def wipe():
    for i in range(0,pixels.numPixels()):
       pixels.setPixelColor(i, Color(0,0,0)) 

def Hcol(h): # HSV colour space with S = V = 1
   if h < 85:
       return Color(h * 3, 255 - h * 3, 0)
   elif h < 170:
       h -= 85
       return Color(255 - h * 3, 0, h * 3)
   else:
       h -= 170
       return Color(0, h * 3, 255 - h * 3)

def checkForDistance(): # select pattern based on distance
   global pattern, patternStep
   if io.digitalRead(sensorPins[0]) == 1 :
      if pattern != 0: # if something showing
         wipe()
         pixels.show()
         pattern = 0 # stop any display
         patternStep = 0 # put to start of a pattern
   else :
      close = 0
      for n in range(1,4):
         if io.digitalRead(sensorPins[n]) == 0 :
            close = n
      if pattern != close+1 : # has pattern changed      
         pattern = close+1
         patternStep = 0 # stage in pattern
         #print"now showing pattern ",pattern
      
# Main program logic:
if __name__ == '__main__':    
    main()

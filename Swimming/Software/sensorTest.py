#!/usr/bin/env python
# Swimming distance sensor test

import time
import os, sys
import wiringpi2 as io

compPins = [ 8,25,24,23]
ledPins = [ 7, 11, 4 ]

def main():
   global clip, stop, pendingStop, mode
   initGPIO()
   strokes = 0
   print"IR distance sensor"
   while True:
      while getSensor() != 1 :
         pass
      io.digitalWrite(ledPins[2],0)      
      io.digitalWrite(ledPins[0],1)
      print"start stroke ",
      while getSensor() != 3 :
         pass
      io.digitalWrite(ledPins[0],0)
      io.digitalWrite(ledPins[1],1)
      print"mid stroke ",
      while getSensor() != 7 :
         pass
      strokes += 1
      io.digitalWrite(ledPins[1],0)
      io.digitalWrite(ledPins[2],1)
      print"end stroke ",
      print strokes
      
def getSensor():
   sensor = 0
   for i in range(0,4) :
         sensor = (sensor << 1) | io.digitalRead(compPins[i])
   return sensor      

def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,4):
      io.pinMode(compPins[pin],0) # mux pin to input
      io.pullUpDnControl(compPins[pin],2) # input enable pull up
   for pin in range (0,3):
      io.pinMode(ledPins[pin],1) # LED pin to output
      io.digitalWrite(ledPins[pin],0)
      
if __name__ == '__main__':    
    main()
    

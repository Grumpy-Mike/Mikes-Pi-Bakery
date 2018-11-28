#!/usr/bin/env python3
#Lights out 
#By Mike Cook Oct 2018

import time, os, random
os.system("sudo pigpiod") # enable pigpio system
from max7219bang import Max7219bang

brightness = 8
dataPin = 14 ; clockPin = 15 ; loadPin = 18 # matrix wiring
matrix = Max7219bang(dataPin,clockPin,loadPin,brightness)
speed = 0.2 ; random.seed()

def main():
   global done
   print("Simple lights out game - Ctrl C to stop")
   print("Press buttons until all lights are out")
   matrix.clrLEDs() # turn all LEDs off
   while True:
     flash(4)
     done = False
     emptyPresses() # remove any bounce
     setup(2) # level of scrambling
     print("Try this one then")
     while not done:
        pressed = matrix.getSwitch() # return pressed switch or -1 for none 
        if pressed != -1 : # if switch has been pressed
          matrix.setLed(pressed,matrix.getLed(pressed) ^ 7)
          invertRow(pressed)
          invertCol(pressed)
          done = checkOut()
          emptyPresses() # remove any bounce

def invertRow(switch) :
   row = switch // 4  
   for i in range(row*4,row*4+4):
      matrix.setLed(i,matrix.getLed(i) ^ 7)
      time.sleep(speed)
   
def invertCol(switch) :
   col = switch % 4  
   for i in range(col,16,4):
      matrix.setLed(i,matrix.getLed(i) ^ 7)
      time.sleep(speed)

def checkOut(): # check LEDs are all off
   off = True
   for switch in range(0,16):
      if matrix.getLed(switch) != 0:
         off = False
   return off      
   
def setup(depth): # inital position of LEDs
   global speed
   speed = 0.001 # make setup quick
   matrix.clrLEDs() # turn all LEDs off
   for i in range(0,depth):
      target = random.randint(0,15)
      #print(target) # uncomment for testing
      matrix.setLed(target,matrix.getLed(target) ^ 7)
      invertRow(target)
      invertCol(target)
   speed = 0.2 # normal display speed

def flash(times):
   state = 7
   for flash in range(0,times*2):
      for i in range(0,16):
         matrix.setLed(i,state)
      time.sleep(0.3)
      state ^= 7
      
def emptyPresses(): # remove all bounce from key switches
    while matrix.getSwitch() != -1:
       pass
       print("extra bounce")
   
# Main program logic:
if __name__ == '__main__':    
  try: 
    main()
  except:  
    matrix.cleanUp()
# Note the use of the code disables any error output from the code
# when developing code comment out the lines:- try: and except: 


#!/usr/bin/env python3
#demo 1a using max7219bang class driver
#By Mike Cook Oct 2018

import time, os
os.system("sudo pigpiod") # enable pigpio system
from max7219bang import Max7219bang

brightness = 8
dataPin = 14 ; clockPin = 15 ; loadPin = 18 # matrix wiring
matrix = Max7219bang(dataPin,clockPin,loadPin,brightness)

def main():
   print("Matrix demo 1 - Ctrl C to stop")
   print("Add each colour led in turn on all switches ")
   print("then fade to dimest")
   speed = 1.0 # time between each change
   while True:
      matrix.setBrightness(15) # maximum
      for i in range(0,16):
         matrix.addRed(i) # all leds to red
      time.sleep(speed)

      for i in range(0,16):
         matrix.addGreen(i) # add green
      time.sleep(speed)
      
      for i in range(0,16):
         matrix.addBlue(i) # add blue
      time.sleep(speed)
      for i in range(15,-1,-1): # fade down
         matrix.setBrightness(i)
         #print("brightness",i)
         time.sleep(0.2)  
      time.sleep(speed)   
      matrix.clrLEDs() # all leds off
      #print("All LEDs off")
      time.sleep(speed)   
         
# Main program logic:
if __name__ == '__main__':
  try: 
    main()
  except:  
    matrix.cleanUp()
# Note the use of the code disables any error output from the code
# when developing code comment out the lines:- try: and except: 

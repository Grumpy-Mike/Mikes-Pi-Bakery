#!/usr/bin/env python3
#demo 1 using max7219bang class driver
#By Mike Cook Oct 2018

import time, os
os.system("sudo pigpiod") # enable pigpio system
from max7219bang import Max7219bang

brightness = 8
dataPin = 14 ; clockPin = 15 ; loadPin = 18 # matrix wiring
matrix = Max7219bang(dataPin,clockPin,loadPin,brightness)

def main():
   print("Matrix demo 1 - Ctrl C to stop")
   print("Show all LEDs on all switches in turn")
   speed = 1.0 # time between each change
   while True:
      for i in range(0,16):
         matrix.setRed(i) # all leds to red
      time.sleep(speed)
      for i in range(0,16):
         matrix.setGreen(i) # all leds to green
      time.sleep(speed)
      for i in range(0,16):
         matrix.setBlue(i) # all leds to blue
      time.sleep(speed)   
       
# Main program logic:
if __name__ == '__main__':
  try: 
    main()
  except:  
    matrix.cleanUp()
# Note the use of the code disables any error output from the code
# when developing code comment out the lines:- try: and except: 

#!/usr/bin/env python3
#demo 3 using max7219bang class driver
#Increment any LED value on the key pressed
# The sequence will be red, green, red & green, blue,
#     blue & red, blue & green, blue & green & red, all off
#By Mike Cook Oct 2018

import time, os
os.system("sudo pigpiod") # enable pigpio system
from max7219bang import Max7219bang

brightness = 8
dataPin = 14 ; clockPin = 15 ; loadPin = 18 # matrix wiring
matrix = Max7219bang(dataPin,clockPin,loadPin,brightness)

def main():
   print("Matrix demo 3 - Ctrl C to stop")
   print("Read switches and increment the LED value of that switch")
   for i in range(0,16):
      matrix.setRed(i) # all leds to red
   while True:
      newKey = matrix.getSwitch()
      while newKey != -1: # get all switches pressed and do stuff with them
         matrix.setLed(newKey,matrix.getLed(newKey)+1) # add 1 to LED number
         print("switch",newKey,"pressed LED value",matrix.getLed(newKey))
         newKey = matrix.getSwitch() # get next key
       
# Main program logic:
if __name__ == '__main__':
  try: 
    main()
  except:  
    matrix.cleanUp()
# Note the use of the code disables any error output from the code
# when developing code comment out the lines:- try: and except: 

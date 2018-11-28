#!/usr/bin/env python3
#demo 2 using max7219bang class driver
#Read switches by Mike Cook Oct 2018

import time, os
os.system("sudo pigpiod") # enable pigpio system
from max7219bang import Max7219bang

brightness = 8
dataPin = 14 ; clockPin = 15 ; loadPin = 18 # matrix wiring
matrix = Max7219bang(dataPin,clockPin,loadPin,brightness)

def main():
   print("Matrix demo - Ctrl C to stop")
   print("Read switches and light up all LEDs on the pushed one")
   matrix.clrLEDs() # turn all LEDs off
   while True:
     pressed = matrix.getSwitch() # return pressed switch or -1 for none 
     if pressed != -1 : # if switch has been pressed
        print("Switch", pressed, "pressed", end=" ")
        if matrix.getLed(pressed) == 0: # if LEDs off
           matrix.setLed(pressed,7)     # turn them on
           print("lights on")
        else:
           matrix.setLed(pressed,0)     # turn them off       
           print("lights off")
           
# Main program logic:
if __name__ == '__main__':    
  try: 
    main()
  except:  
    matrix.cleanUp()
# Note the use of the code disables any error output from the code
# when developing code comment out the lines:- try: and except: 


#!/usr/bin/env python3
#demo 1 using Vga_drive class driver
#By Mike Cook January 2019

import time

from vga_drive import Vga_drive

#1024 x 768 @ 57Hz settings: 128 x 64 characters
#800 x 600 @ 75Hz settings: 100 x 50 characters
#640 x 480 @ 69Hz settings: 80 x 40 characters
xWide = 100 ; yWide = 50 # Pick the resolution for your VDU settings
vga = Vga_drive(xWide, yWide)
time.sleep(1.5) # let the Propeller chip reset
s1 = ") Now is the time to come to the aide of the party "
s2 = " Again with feeling "

def main():
   print("Spin VGA driver demo1 - Ctrl C to stop")
   vga.cls()
   speed = 0.05 # time between each change
   while True:
      vga.sendStringLn(" Hello from the Raspberry Pi") # send with CR
      for i in range(1,yWide+20): # allow scrolling at the end
         vga.sendString(str(i)+s1) # send number and string
         time.sleep(speed*4)
         vga.sendString(s2)
         time.sleep(speed * 8)
         vga.erase(-1, len(s1)+len(str(i)), len(s1)) # remove last string         
         time.sleep(speed)
         vga.sendNl() # new line
      vga.cls()   
       
# Main program logic:
if __name__ == '__main__':
    main()

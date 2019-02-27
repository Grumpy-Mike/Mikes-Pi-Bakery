#!/usr/bin/env python3
#demo 2 using Vga_drive class driver
#with added colour theme switching
#By Mike Cook January 2019

import time, random
from vga_drive import Vga_drive

#1024 x 768 @ 57Hz settings: 128 x 64 characters
#800 x 600 @ 75Hz settings: 100 x 50 characters
#640 x 480 @ 69Hz settings: 80 x 40 characters
xWide = 100 ; yWide = 50 # Pick the resolution for your settings
vga = Vga_drive(xWide, yWide)
time.sleep(1.5) # let the Propeller chip reset
random.seed()
s1 = ") more into the breach dear friends:- "
#colours for themes
redF =   [3,0,3,0,0,0,3,3,3,0]
redB =   [0,3,0,0,2,3,0,3,1,1]
greenF = [3,0,3,3,0,0,1,3,3,3]
greenB = [0,3,0,0,2,1,0,1,1,1]
blueF =  [3,0,3,0,0,0,0,3,3,0]
blueB =  [0,3,2,0,0,0,0,0,2,1]
ThemeNames = ["White on black","Black on white","Atari/C64 theme",
            "Apple ][ ","Wasp/yellow jacket","Autumn","Inverse Autumn",
            "Creamsicle","Purple orchid","Gremlin","Chaos 1","Chaos 2"]

def main():
   print("Spin VGA colour theme demo - Ctrl C to stop")
   vga.cls()
   vga.sendStringLn("Hello from the Raspberry Pi")
   vga.sendString("starting the theme demo")
   time.sleep(5) # time for monitor to adjust
   while True:
      for j in range(0,12):
         if j >= 10:
            chaos(j & 1)
         else :   
            changeTheme(j,1) # use 0 for no special top line        
         vga.sendStringLn(
          "Hello from the Raspberry Pi - Theme "+ThemeNames[j])
         for i in range(1,yWide-1):
            vga.sendString(str(i)+s1) # send number and string
            vga.sendStringLn(" Again with feeling ")
         vga.sendString("This is the last line")   
         time.sleep(2)
         vga.cls()

def changeTheme(theme, top): # top = 1 if inverted
   start = top & 1
   if start != 0:
      vga.setY(0)
      vga.setColour(redB[theme],greenB[theme],blueB[theme],
                    redF[theme],greenF[theme],blueF[theme])
 
   for i in range(start, yWide):
      vga.setY(i) # choose line
      vga.setColour(redF[theme],greenF[theme],blueF[theme],
                    redB[theme],greenB[theme],blueB[theme])
   vga.home()   

def chaos(t): #just a bit of fun
   for i in range(0,yWide):
      vga.setY(i) # choose line
      c = [random.randint(0,3) for j in range(0,6)]
      if t == 1 :
         vga.setColour(c[0],c[1],c[2],c[3],c[4],c[5])
      else:
         vga.setColour(c[0],c[1],c[2],c[0]^3,c[1]^3,c[2]^3) # inverse back
   vga.home()   


# Main program logic:
if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Get a Grip - physical sequencer
# Version 1 reverse mode switch alt sound on reverse

import time, pygame
import os, sys
import wiringpi2 as io

pygame.init()                   # initialise pygame
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)

pygame.event.set_allowed(None)
seqSound = [ pygame.mixer.Sound("marimber_sounds/s"+str(sound)+".ogg")
                  for sound in range(0,15)]
altSound = [ pygame.mixer.Sound("piano_sounds/s"+str(sound)+".ogg")
                  for sound in range(0,15)]

startPush = 2; modePush = 3
lastStart = 1; lastMode = 1
muxPins = [ 23,24,25]
threshold = [80,153,235,290,370,426,475,535,586,636,681,745,816,879,922,950,1024] 
#note   C   D    E    F    G    A    B    C    D    E    F    G    A    B    C
#      1K  2K7  3K3  4K7  6K8  7K5  10K  12K  15K  18K  22K  33K  47K  82K  100K

def main():
   global clip, stop, pendingStop, mode
   initGPIO()
   print"Get A Grip - sequencer"
   clip=0 
   stop = False ; mode = True
   pendingStop = False
   while True:
      if io.digitalRead(modePush) == 0 and io.digitalRead(startPush) == 0 :
         terminate()
      if not stop :
         stepTime = 0.004 + (io.analogRead(71) / 2000.0)
         nextStep = time.time() + stepTime
         setMux(clip)
         while time.time() <= nextStep :
           readStart()
           readMode()
         readAD(clip)
         incrementClip()
      else :   
         readStart()
      
def incrementClip():
   global clip, stop, pendingStop, mode
   if mode :
      clip += 1
      if clip>7 :
         clip= 0
         if pendingStop :
            stop = True
            pendingStop = False
            print"stopped"
   else :
      clip -= 1
      if clip < 0 :
         clip= 7
         if pendingStop :
            stop = True
            pendingStop = False
            print"stopped"
 
def readMode():
    global mode, lastMode, clip
    current = io.digitalRead(modePush)
    if current == 0 and lastMode == 1:
         time.sleep(0.02) # debounce delay
         mode = not mode
         if mode :
            print"forward mode"
            clip = 0
         else :
            print"reverse mode"
            clip = 7
    lastMode = current
    
def readStart(): # Start / stop control
    global stop, pendingStop, lastStart
    current = io.digitalRead(startPush)
    if current == 0 and lastStart == 1:
       time.sleep(0.02) # debounce delay
       if stop :
          stop = False
          print"running"
       else :
          pendingStop = True
          print"stopping"
    lastStart = current
       
def readAD(step) :
   value = io.analogRead(70) # read multiplex
   look = 0
   while value >= threshold[look]:
      look +=1  
   if look>0 and look <16 :
      if mode :
        seqSound[look-1].play()
      else:        
        altSound[look-1].play()
   
def setMux(n):
   mask = 1;
   for pin in range(0,3):
     if (mask & n) != 0 :
        io.digitalWrite(muxPins[pin], 1)
     else :
        io.digitalWrite(muxPins[pin], 0)
     mask = mask << 1
                        
def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,3):
      io.pinMode(muxPins[pin],1) # mux pin to output
   io.pinMode(startPush,0) # start / stop input  
   io.pinMode(modePush,0) # mode input
   io.pullUpDnControl(startPush,2) # input enable pull up
   io.pullUpDnControl(modePush,2) # input enable pull up
   io.mcp3002Setup(70,0)
   
def terminate(): # close down the program
    print"closing down"
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
        
if __name__ == '__main__':    
    main()
    

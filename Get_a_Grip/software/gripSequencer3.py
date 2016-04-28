#!/usr/bin/env python
# Get a Grip - physical sequencer
# Version 3 phase mode - same sequence but delayed and drifts in an out of phase

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
gripState = [ 0,0,0,0,0,0,0,0 ]

def main():
   global clip, stop, pendingStop, mode, clipShift, nextPhase, stepTime
   initGPIO()
   print"Get A Grip - sequencer"
   clip=0 ; clipShift = 0
   stop = False ; mode = False
   pendingStop = False
   while True:
      if io.digitalRead(modePush) == 0 and io.digitalRead(startPush) == 0 :
         terminate()
      if not stop :
         stepTime = 0.004 + (io.analogRead(71) / 2000.0)
         nextStep = time.time() + stepTime
         setMux(clip)
         #print clip, clipShift
         while time.time() <= nextStep :
           readStart()
           readMode()
           if mode  and time.time() > nextPhase :
              echoSequence()
         readAD(clip)
         incrementClip()
      else :   
         readStart()
      
def incrementClip():
   global clip, stop, pendingStop
   clip= clip+1
   if clip>7 :
      clip= 0
      if pendingStop :
         stop = True
         pendingStop = False
         print"stopped"
   
def readMode():
    global mode, lastMode, clipShift, nextPhase
    current = io.digitalRead(modePush)
    if current == 0 and lastMode == 1:
         time.sleep(0.02) # debounce delay
         mode = not mode
         if mode :
            print"phase mode"
            clipShift = 0
            nextPhase = time.time() + 0.01
         else :
            print"sequence mode"
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
    
def echoSequence() : # echo of the sequence out of phase
   global nextPhase, clipShift, stepTime
   if gripState[clipShift] > 0 and gripState[clipShift] < 16 :
      altSound[gripState[clipShift]-1].play()
   clipShift -= 1
   if clipShift < 0 :
      clipShift = 7
   nextPhase = time.time() + stepTime + 0.01   
   
def readAD(step) :
   global gripState
   value = io.analogRead(70) # read multiplex
   look = 0
   while value >= threshold[look]:
      look +=1
   gripState[step] = look   
   if look>0 and look <16 :
      seqSound[look-1].play()
   
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
    

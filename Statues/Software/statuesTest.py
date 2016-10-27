#!/usr/bin/env python
# Statues
# Test hardware

import time, pygame
import os, sys
import wiringpi2 as io

pygame.init()                   # initialise pygame
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)

pygame.event.set_allowed(None)
moveSound = [ pygame.mixer.Sound("sounds/s"+str(sound)+".ogg")
                  for sound in range(0,5)]
def main():
   global clip, stop, pendingStop, mode
   initGPIO()
   print"Statues hardware test"
   print" Ctrl C to quit"
   leftMovement = False
   rightMovement = False
   while True:

      if io.digitalRead(pirPins[0]) == 1 and not(leftMovement):
         print"left movement detected"
         io.digitalWrite(ledPins[0],0) # turn Red on
         io.digitalWrite(ledPins[1],1) # turn Green off
         moveSound[0].play(0)
         leftMovement = True
      elif  io.digitalRead(pirPins[0]) == 0 and leftMovement:
         io.digitalWrite(ledPins[0],1) # turn Red off
         io.digitalWrite(ledPins[1],0) # turn Green on
         leftMovement = False
         
      if io.digitalRead(pirPins[1]) == 1 and not(rightMovement):
         print"right movement detected"
         io.digitalWrite(ledPins[2],0) # turn Red on
         io.digitalWrite(ledPins[3],1) # turn Green off
         moveSound[4].play(0)
         rightMovement = True
      elif io.digitalRead(pirPins[1]) == 0 and rightMovement:
         io.digitalWrite(ledPins[2],1) # turn Red off
         io.digitalWrite(ledPins[3],0) # turn Green on
         rightMovement = False
                                   
def initGPIO():
   global ledPins,pirPins
   ledPins = [ 4,17,27,22] # left R, left G, right R, right G
   pirPins = [18,23] # left / right 
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,4):
      io.pinMode(ledPins[pin],1) # led pin to output
      io.digitalWrite(ledPins[pin],1) # turn off
   io.pinMode(pirPins[0],0) # input left PIR sensor  
   io.pinMode(pirPins[1],0) # input right PIR sensor
   io.pullUpDnControl(pirPins[0],2) # input enable pull up
   io.pullUpDnControl(pirPins[1],2) # input enable pull up
   
def terminate(): # close down the program
    print"closing down"
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
        
if __name__ == '__main__':    
    main()
    

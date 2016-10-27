#!/usr/bin/env python
# Statues

import time, pygame
import os, sys, random
import wiringpi2 as io

pygame.init()                   # initialise pygame
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Statues")
screen = pygame.display.set_mode([300,100],0,32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
moveSound = pygame.mixer.Sound("sounds/s0.ogg")
pygame.mixer.music.load("sounds/tune.wav")
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play()
pygame.mixer.music.pause()
imageNames = ["ready","still","dance","freeze","leftWin","rightWin","play"]
messages = [ pygame.image.load("images/"+imageNames[m]+".png")
             for m in range(0,7) ]
                           
setup = 0 ; running =1; winner = 2; rstart = 3 # state machine constants
status = rstart # state machine status
stillTime = 0.0
startDelay = 2.0 # period to hold before game starts
stopDelay = 3.0 # period to wait after music stops before looking at sensors
playDuration = 4.0 # time the music plays
restart = False

def main():
   global leftMovement,rightMovement, status
   initGPIO()
   print"Statues game"
   print" Esc to quit"
   leftMovement = False
   rightMovement = False
   while True: 
      checkForEvent()
      if status == setup:
         settingUp()
      if status == running :
         gameRun()
      if status == winner :
         gameWinner()
      if status == rstart :
         gameRstart()
         
def settingUp():
   global stillTime, status, playTime
   checkSensors()
   showLEDs()
   if stillTime == 0:
      stillTime = time.time()
   elif time.time() - stillTime > startDelay :
      status = running
      playTime = time.time()
      pygame.mixer.music.unpause()
      #"play music - game running"
      displayMessage(2,128)
   if leftMovement or rightMovement:
      stillTime = 0 # reset the still time before the music
      moveSound.play()
      displayMessage(1,random.randint(40,220))
      
def gameRun():
   global leftMovement,rightMovement, status, playTime
   checkSensors()
   showLEDs()
   if time.time()-playTime > playDuration :
      #"music stops"
      displayMessage(3,128)
      pygame.mixer.music.pause()
      status = winner
      playTime = time.time()
   else :
      if not pygame.mixer.music.get_busy() : # check end of music file
         pygame.mixer.music.rewind()
         pygame.mixer.music.play()
         
def gameWinner():
   global leftMovement,rightMovement, status
   if time.time() - playTime > stopDelay :
      checkSensors()
      showLEDs()
      if leftMovement or rightMovement :
         moveSound.play()
         if leftMovement :
            print"right player wins"
            winLED(1)
            displayMessage(5,128)
         else :
            print"left player wins"
            winLED(0)
            displayMessage(4,128)
         status = rstart
         time.sleep(3.5)
         
def gameRstart():
   global restart, status, stillTime, playDuration
   if restart :
      restart = False
      status = setup
      checkSensors()
      showLEDs()
      displayMessage(0,128)
      print"ready"
      stillTime = 0.0
      playDuration = random.randint(6,20)+6 # time till next stop
   else :
      displayMessage(6,128)
    
def winLED(player):
   for i in range(0,4): # all LEDs off
      io.digitalWrite(ledPins[i],1)
   if player == 0: # winner's LEDs yellow
      io.digitalWrite(ledPins[0],0) 
      io.digitalWrite(ledPins[1],0) 
   else  :
      io.digitalWrite(ledPins[2],0) 
      io.digitalWrite(ledPins[3],0) 

def displayMessage(m,b):
   pygame.draw.rect(screen,(b,b,b),(0,0,300,100),0)
   screen.blit(messages[m],(0,0))
   pygame.display.update()
   
def checkSensors():
   global leftMovement,rightMovement
   if io.digitalRead(pirPins[0]) == 1 and not(leftMovement):
      leftMovement = True
   elif  io.digitalRead(pirPins[0]) == 0 and leftMovement:
      leftMovement = False         
   if io.digitalRead(pirPins[1]) == 1 and not(rightMovement):
      rightMovement = True
   elif io.digitalRead(pirPins[1]) == 0 and rightMovement:
      rightMovement = False
      
def showLEDs():
   if leftMovement :
      io.digitalWrite(ledPins[0],0) # turn Red on
      io.digitalWrite(ledPins[1],1) # turn Green off
   else :
      io.digitalWrite(ledPins[0],1) # turn Red off
      io.digitalWrite(ledPins[1],0) # turn Green on
   if rightMovement :
      io.digitalWrite(ledPins[2],0) # turn Red on
      io.digitalWrite(ledPins[3],1) # turn Green off
   else :
      io.digitalWrite(ledPins[2],1) # turn Red off
      io.digitalWrite(ledPins[3],0) # turn Green on     
    
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

def checkForEvent(): # see if we need to quit
    global restart
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_SPACE :
          restart = True
        
if __name__ == '__main__':    
    main()
    

# Mulder - animatronic skull
# By Mike Cook - August 2015
import pygame, time, random, sys, os
from smbus import SMBus
from copy import deepcopy

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Mulder")
screen = pygame.display.set_mode([424,430],0,32)
mulder = pygame.image.load("images/Mulder.png").convert_alpha()
screen.blit(mulder,[0,0])
pygame.display.update()
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
soundNames = ["laugh","scream","door","kill","thunder","owl"]
mulderSound = [ pygame.mixer.Sound("sounds/"+soundNames[effect]+".wav")
                  for effect in range(0,6)]

# command register addresses for the PCA9685 IC
PCA9685 = 0x40 # i2c address of PCA9685
bus = None
  
# right eye, left eye, jaw, neck
servos = [14, 15, 10, 8]
startPos = [269, 257, 180, 250]
white = [2480.0,4088.0,1608.0]
black = [0.0,0.0,0.0]
green = [0.0,3000.0,0.0]
# right eye - left eye - nose - cranium
lights = [(0,1,2),(3,4,5),(6,7,9),(11,12,13)] # PCA9685 registers
lightPC = [[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
lightTC =  deepcopy(lightPC) # Light Target colour
lightInc = deepcopy(lightPC) # Light Increment
servoPP = deepcopy(startPos) # servo Present Position
servoInc = [0.0,0.0,0.0,0.0] # servo Increment
servoTP = deepcopy(startPos) # servo Target Position
stepsInFade = 40.0 # change to alter speed
stepsInMove = 40.0 # change to alter speed
fadeSpeed = 0.06 # change to alter speed
fading = False
facing = startPos[3]
maxNeck = 337
minNeck = 177

   
def main():
   print"Welcome to the world of Mulder"
   busInit()
   print"Press keys to make him work"
   while True: # repeat forever
      checkForEvent()      
      if not checkMove() : # need to move?
         handleMove()
      if fading :  # need to fade?
         handleFade()
      if fading or ( not checkMove()): # delay between steps 
         time.sleep(fadeSpeed)

def busInit(): # start up the I2C bus 
   global bus
   try :
     bus = SMBus(1)
   except :
     print"start IDLE with 'gksudo idle' from command line"
     sys.exit()
   # initialise the outputs on the PCA9685  
   bus.write_byte_data(PCA9685,0,0x31) # sleep mode set to 1
   bus.write_byte_data(PCA9685,0xfe,132) # divider for 50Hz frame
   bus.write_byte_data(PCA9685,0,0x21) # sleep mode set to 0
   bus.write_byte_data(PCA9685,0x01,0x18) #Mode reg 2 - outputs open drain, invert bit set, output change on ack
   beginners() # initial position

def beginners(): # initial position
   for r in range(0,4):
      setServo(r, startPos[r]) # move directly 
   wipe() # lights out
   
def wipe(): # clear the lights
    for i in range(0,4):
       setLeds(i,[0,0,0])
       
def RestoreBeginners(): # restore initial position
   for r in range(0,4):
      setServoTarget(r, startPos[r])
   while not checkMove():
      handleMove()
      time.sleep(fadeSpeed)
   wipe() # lights out
       
def setServo(servo,pos): # move directly
   reg = (servos[servo] * 4)+6 #register number to start with
   regValues = [0,0,pos &0xff, pos >> 8]
   bus.write_i2c_block_data(PCA9685,reg,regValues)
   
def setServoTarget(motor, pos): # set new position to go to
   servoTP[motor] = pos
   servoInc[motor] = (pos - servoPP[motor]) / stepsInMove
   
def setLeds(led,col):   
   for c in range(0,3):
      reg = (lights[led][c] * 4)+6 #register number to start with
      regValues = [0,0,col[c] & 0xff, col[c] >> 8]
      #print reg,regValues
      bus.write_i2c_block_data(PCA9685,reg,regValues)
      
def setLEDfade(led,target): # set up an LED fade
   global lightPC,lightTC,lightInc, fading
   fading = True
   for i in range(0,3): # work out the increment
       lightTC[led][i] = target[i]      
       lightInc[led][i] = (lightTC[led][i] - lightPC[led][i])/stepsInFade

def handleMove():  # make one increment of all servos
   global servoPP
   for motor in range(0,4):
      if abs(servoTP[motor] - servoPP[motor]) >= 1.0 :
         if abs(servoTP[motor] - servoPP[motor]) >= abs(servoInc[motor]):
            servoPP[motor] += servoInc[motor]
         else:
            servoPP[motor] = servoTP[motor]
         setServo(motor,int(servoPP[motor]))
      else:
         servoPP[motor] = servoTP[motor]
   
def handleFade(): # make one increment of all fades
   global lightPC, fading
   fading = False # global indication of fading in progress
   for led in range(0,4):
      if checkFade(led) == False :
         fading = True
         for i in range(0,3): # work out the new colour values
            if abs(lightPC[led][i] - lightTC[led][i]) >= abs(lightInc[led][i]) :
               lightPC[led][i] += lightInc[led][i] # only change if we are not at target
               if lightPC[led][i] < 1.1:
                  lightPC[led][i] = 0.0
            else :
               lightPC[led][i] = lightTC[led][i]
            updateLED(led)

def updateLED(led):                  
    for c in range(0,3): # write LED values to the PCA9685
      reg = (lights[led][c] * 4)+6 #register number to start with
      regValues = [0,0,int(lightPC[led][c]) & 0xff, int(lightPC[led][c]) >> 8]
      bus.write_i2c_block_data(PCA9685,reg,regValues)

def checkMove():
   done = True
   for i in range(0,4):
      if servoTP[i] != servoPP[i]:
         done = False
   return done

def checkFade(led):
   done = True
   for i in range(0,3):
      if abs(lightPC[led][i] - lightTC[led][i]) >= 1.0 :
         done = False
   return done
   
def terminate(): # close down the program
    print "Closing down please wait"
    RestoreBeginners() # move motors back
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # keyboard commands
    global facing
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       # sounds
       if event.key == pygame.K_h :
          mulderSound[0].play()
       if event.key == pygame.K_j :
          mulderSound[1].play()
       if event.key == pygame.K_k :
          mulderSound[2].play()
       if event.key == pygame.K_l :
          mulderSound[3].play()
       if event.key == pygame.K_SEMICOLON :
          mulderSound[4].play()
       if event.key == pygame.K_QUOTE :
          mulderSound[5].play()
       # Lights  - eyes 
       if event.key == pygame.K_q : # eyes off
          setLEDfade(0,black)
          setLEDfade(1,black) 
       if event.key == pygame.K_w : # eyes white
          setLEDfade(0,white)
          setLEDfade(1,white)
       if event.key == pygame.K_e : # eyes blue
          setLEDfade(0,[0,0,1000])
          setLEDfade(1,[0,0,1000])          
       if event.key == pygame.K_r : # eyes red
          setLEDfade(0,[400,0,0])
          setLEDfade(1,[400,0,0])            
       if event.key == pygame.K_t : # eyes green
          setLEDfade(0,green)
          setLEDfade(1,green)
       if event.key == pygame.K_y : # right eye white
          setLEDfade(0,white)
          setLEDfade(1,black)           
       if event.key == pygame.K_u : # right eye red
          setLEDfade(0,[800,0,0]) 
       # Lights  - nose   
       if event.key == pygame.K_z : # nose off
          setLEDfade(2,black)
       if event.key == pygame.K_x : # nose white
          setLEDfade(2,white)
       if event.key == pygame.K_c : # nose blue
          setLEDfade(2,[0,0,1000])
       if event.key == pygame.K_v : # nose red
          setLEDfade(2,[1000,0,0])
       if event.key == pygame.K_b : # nose green
          setLEDfade(2,green)
       if event.key == pygame.K_n : # nose yellow
          setLEDfade(2,[1000,1000,0])
       if event.key == pygame.K_m :
          setLEDfade(2,[1000,300,0])# nose orange
          
       # Lights  - cranium   
       if event.key == pygame.K_a : # cranium off
          setLEDfade(3,black)
       if event.key == pygame.K_s : # cranium dim
          setLEDfade(3,[100,100,100])
       if event.key == pygame.K_d : # cranium medium
          setLEDfade(3,[600,600,600])
       if event.key == pygame.K_f : # cranium bright
          setLEDfade(3,[4000,4000,4000])
          
       # Movement
       if event.key == pygame.K_o :  # jaw open
          setServo(2,180)
          servoPP[2]= 180
       if event.key == pygame.K_p :  # jaw closed
          setServo(2,336)
          servoPP[2] = 336

       if event.key == pygame.K_1 : # eyes forward
          setServoTarget(0,269)
          setServoTarget(1,257) 
       if event.key == pygame.K_2 : # eyes left
          setServoTarget(0,233) 
          setServoTarget(1,192) 
       if event.key == pygame.K_3 : # eyes right
          setServoTarget(0,322) 
          setServoTarget(1,298)           
       if event.key == pygame.K_4 : # right eye forward
          setServoTarget(1,257) 
       if event.key == pygame.K_5 : # right eye left
          setServoTarget(1,192) 
       if event.key == pygame.K_6 : # right eye right
          setServoTarget(1,306) 
          
       if event.key == pygame.K_7 : # left eye forward
          setServoTarget(0,269) 
       if event.key == pygame.K_8 : # left eye left
          setServoTarget(0,233) 
       if event.key == pygame.K_9 : # left eye right
          setServoTarget(0,329) 

       if event.key == pygame.K_UP : # face the front
          facing = startPos[3]
          setServoTarget(3,facing)          
       if event.key == pygame.K_DOWN : # stop any movement
          facing = servoPP[3]
          setServoTarget(3,facing)
       if event.key == pygame.K_LEFT :
          facing += 20
          if facing > maxNeck: # limit left move
             facing = maxNeck
          setServoTarget(3,facing)
       if event.key == pygame.K_RIGHT :
          facing -= 20
          if facing < minNeck: # limit left move
             facing = minNeck
          setServoTarget(3,facing)          
       if event.key == pygame.K_PERIOD : # max right move
          facing = minNeck
          setServoTarget(3,facing)          
       if event.key == pygame.K_COMMA : # max left move
          facing = maxNeck
          setServoTarget(3,facing)          
          
          #debug
       if event.key == pygame.K_0 :
          print"Debug fading",fading
          print "present",lightPC
          print "target",lightTC
          print "increment",lightInc
          
          print"Debug moving",( not checkMove())
          print "present position",servoPP
          print "target",servoTP
          print "increment",servoInc
          
         
# Main program logic:
if __name__ == '__main__':   
    main()   

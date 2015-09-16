# Mulder Script - animatronic skull
# Plays scripted action from a text script
# By Mike Cook - August 2015
import pygame, time, random, sys, os
from smbus import SMBus
from copy import deepcopy

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Mulder")
screen = pygame.display.set_mode([170,40],0,32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
soundNames = ["laugh","scream","door","kill","thunder","owl"]
mulderSound = [ pygame.mixer.Sound("sounds/"+soundNames[effect]+".wav")
                  for effect in range(0,6)]
soundChannel = mulderSound[5].play()

# command register addresses for the PCA9685 IC
PCA9685 = 0x40 # i2c address of PCA9685
bus = None
  
# right eye, left eye, jaw, neck
servos = [14, 15, 10, 8]
startPos = [269, 257, 180, 250]
# right eye - left eye - nose - cranium
lights = [(0,1,2),(3,4,5),(6,7,9),(11,12,13)] # PCA9685 registers
lightPC = [[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
lightTC =  deepcopy(lightPC) # Light Target colour
lightInc = deepcopy(lightPC) # Light Increment
servoPP = deepcopy(startPos) # servo Present Position
servoInc = [0.0,0.0,0.0,0.0] # servo Increment
servoTP = deepcopy(startPos) # servo Target Position
maxNeck = 337
minNeck = 177
upperLimit = [322, 298, 336, maxNeck] # max number to set servo
lowerLimit = [233, 192, 180, minNeck] # min number to set servo
stepsInFade = 40.0 # change to alter speed
stepsInMove = 40.0 # change to alter speed
fadeSpeed = 0.06 # change to alter speed
fading = False
facing = startPos[3]
debug = False
background = False # background sound

   
def main():
   global debug
   print"Welcome to the world of Mulder - esc to quit"
   busInit()
   script = "script1.txt"
   print"Running script",script
   sFile = open(script,"r")

   movesToDo = 0
   moves = list()
   for lines in sFile.readlines():
      moves.append(lines)
      movesToDo += 1
   sFile.close()
   while True:
      debug = False
      for moveNo in range(0,movesToDo):
         command = moves[moveNo].split(",")
         exe = doCommand(command, moveNo)
         if debug :
            print command
         if exe : # run the commands
            while (not checkMove()) or fading or soundChannel.get_busy(): 
               time.sleep(fadeSpeed)
               checkForEvent()
               handleMove()
               handleFade()

def doCommand(c, line):
   global servoInc, soundChannel, debug, background, stepsInFade
   go = False
   try:
      if c[0] == "right eye":
         setLEDfade(0,[int(c[1]),int(c[2]),int(c[3])])
      elif c[0] == "left eye":
         setLEDfade(1,[int(c[1]),int(c[2]),int(c[3])])
      elif c[0] == "nose":
         setLEDfade(2,[int(c[1]),int(c[2]),int(c[3])])
      elif c[0] == "cranium":
         setLEDfade(3,[int(c[1]),int(c[2]),int(c[3])])
      elif c[0] == "move left eye":
         makeMove(0,c,line)         
      elif c[0] == "move right eye":
         makeMove(1,c,line)
      elif c[0] == "fade steps": # speed of light change
         stepsInFade = float(c[1])
      elif c[0] == "jaw":
         if c[1] == " open\n":
            setServoTarget(2, lowerLimit[2])
            servoInc[2] = servoTP[2] # increment the full size
         if c[1] == " closed\n":
            setServoTarget(2, upperLimit[2])
            servoInc[2] = servoTP[2] # increment the full size
      elif c[0] == "neck":
         makeMove(3,c,line)
      elif c[0] == "sound":
         soundChannel = mulderSound[int(c[1])].play()
      elif c[0] == "background\n":
         pygame.mixer.music.load("sounds/thunderLong.wav")
         pygame.mixer.music.set_volume(1.0)
         pygame.mixer.music.play(-1,0.0)
         background = True
      elif c[0] == "backgroundOff\n":
         pygame.mixer.music.fadeout(2000)
         time.sleep(2.0)
         background = False
      elif c[0] == "go\n": # start action
         go = True
      elif c[0] == "quit" or c[0] == "quit\n": # quit program
         terminate()
      elif c[0] == "delay":
         time.sleep(float(c[1]))
      elif c[0] == "#": #comment
         pass
      elif c[0] == "debug\n":
         debug = not debug
      elif True:
         print c[0],"command not recognised in line",line
   except :
      print"error in parameters in line",line, "for command", c[0]
   return go

def makeMove(motor,c,line): # check limits on servo and issue command
   try:
      position = int(c[1])
   except:
      print"error in parameter in line",line, "for command", c[0]
      return
   if position > upperLimit[motor] :
      position = upperLimit[motor]
   if position < lowerLimit[motor] :
      position = lowerLimit[motor]
   setServoTarget(motor, position)      
   
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
    if background :
       pygame.mixer.music.fadeout(2000)
       time.sleep(2.0)
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
          
# Main program logic:
if __name__ == '__main__':   
    main()   

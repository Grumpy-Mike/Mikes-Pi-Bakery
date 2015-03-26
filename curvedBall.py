# Curved Ball - a game for the Pi Glow board
# By Mike Cook - March 2015
import time, random, sys
from smbus import SMBus
import wiringpi2 as io

# command register addresses for the SN3218 IC used in PiGlow
CMD_ENABLE_OUTPUT = 0x00
CMD_ENABLE_LEDS = 0x13
CMD_SET_PWM_VALUES = 0x01
CMD_UPDATE = 0x16
SN3218 = 0x54 # i2c address of SN3218 IC
bus = None
try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   sys.exit()
   
pinList= [7,8,25] # GPIO pins for switches
lights = [0x00 for i in range(0,18)] # the LED brightness list
red    = [0,6,17]  # red LEDs
orange = [1,7,16]  # orange LEDs
yellow = [2,8,15]  # yellow LEDs
green  = [3,5,13]  # green LEDs
blue   = [14,4,11] # blue LEDs
white  = [12,9,10] # white LEDs
triangleIn  = [red,orange,yellow,green,blue,white]
triangleOut = [white,blue,green,yellow,orange,red]
speed = 0.03 # delay is twice this
returnSpeed = 0.1 # for hit back
score = 0

def main():
   initGPIO()
   busInit()
   while True: # repeat forever
      wipe()
      updateLEDs(lights)
      while scanSwitches() != -1: #make sure fingers off
         pass
      pitch()
      
def pitch(): # throw the ball
   global score
   time.sleep(1.0) # delay before the throw - try making this random
   arm = random.randint(0,2) # direction of curved ball
   bat = False
   push = -1
   for triangle in range(0,5):                     
      wipe() # clear all LEDs in the list
      if bat:
        lights[white[push]] = 0x20 # turn on bat LED
      lights[triangleIn[triangle][arm]] = 0x80
      updateLEDs(lights)
      time.sleep(speed)
      if not bat: # no switch pressed so far so look for one
         push = scanSwitches() # switched pressed?
         if push != -1:
            bat = True  # no more looking at switches
            score = 6 - triangle # sooner you see it the higher the score
      else:
         lights[white[push]] = 0x20
      updateLEDs(lights)
      time.sleep(speed)                     
   if arm == push:
      print "hit - score ",score
      for triangle in range(0,6):  # hit it back                   
         wipe()
         lights[triangleOut[triangle][arm]] = 0x80
         updateLEDs(lights)
         time.sleep(returnSpeed)
      time.sleep(0.7)

def initGPIO(): # set up the GPIO pins
   for pin in range (0,3):    
      io.pinMode(pinList[pin],0) # make pin into an input
      io.pullUpDnControl(pinList[pin],2) # enable pull up
      
def scanSwitches(): # look at each pin in turn
   down = -1 # default return value means no switch pressed
   for pin in range (0,3):
      if io.digitalRead(pinList[pin]) == 0:
         down = pin
   return down      

def busInit(): # start up the I2C bus and enable the outputs on the SN3218
   global bus
   bus = SMBus(1)
   bus.write_byte_data(SN3218,CMD_ENABLE_OUTPUT, 0x01)
   bus.write_i2c_block_data(SN3218, CMD_ENABLE_LEDS, [0xFF, 0xFF, 0xFF])
   
def updateLEDs(lights): # update the LEDs to reflect the lights list
   bus.write_i2c_block_data(SN3218, CMD_SET_PWM_VALUES, lights)
   bus.write_byte_data(SN3218,CMD_UPDATE, 0xFF)

def wipe(): # clear the lights list
    global lights
    for i in range(0,18):
        lights[i] = 0
         
# Main program logic:
if __name__ == '__main__':
  try:     
    main()   
  except KeyboardInterrupt:
	# set all the LEDs to "off" when Ctrl+C is pressed before exiting
        wipe()
        updateLEDs(lights)

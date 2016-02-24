# distance sensor test - Magic mirror
# By Mike Cook - January 2016

import time, os, random
import wiringpi2 as io

random.seed()

try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)
  
sensorPins = [17,24,23,27]
distance = ["50cm","30cm","20cm","10cm"]

def main():
   print"Distance sensor test - ctr C to quit"   
   initGPIO()   
   while True:
     checkForDistance()
     time.sleep(0.5)
     
def initGPIO():
   for pin in range (0,4):
      io.pinMode(sensorPins[pin],0) # input
      io.pullUpDnControl(sensorPins[pin],2) # activate pull ups

def checkForDistance():
   if io.digitalRead(sensorPins[0]) == 1 :
      print"nothing in range"
   else :
      close = 0
      for n in range(1,4):
         if io.digitalRead(sensorPins[n]) == 0 :
            close = n
      print" distance sensor ",n, "triggered"
      print"closer than", distance[n]
      
# Main program logic:
if __name__ == '__main__':    
    main()

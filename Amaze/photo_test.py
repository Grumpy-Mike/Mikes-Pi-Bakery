# photo transistor input test
# for the Amaze game - Mike Cook September 2015
import time, os
import wiringpi2 as io

pinList = [22,27,17,4] # GPIO pins for sensor switches

def main():
   initGPIO()
   print"Amaze sensor switch test"
   while True:
      for i in range(0,4):
         print io.digitalRead(pinList[i])," ",
      print" "
      time.sleep(1)
      
def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,4):
      io.pinMode(pinList[pin],0)
      io.pullUpDnControl(pinList[pin],2) # input enable pull up

# Main program logic:
if __name__ == '__main__':    
    main()

#!/usr/bin/env python3
#Neopixel Bounce - controlling LEDs with the bounce interface
#**** must start IDLE3 with "gksudo idle3" *****#

import time , spidev
from neopixel import Adafruit_NeoPixel

# LED strip configuration:
LED_COUNT      = 30      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800KHz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 140     # Set to 0 for darkest and 255 for brightest
LED_CHANNEL    = 0       # PWM channel
LED_INVERT     = True    # True if using an inverting interface

ws2812 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
ws2812.begin()

length = LED_COUNT
circleLength = 16
totemLength = 14
launchPoint = 11 # LED opposite totem
inBuf = [0, 0] ; lastBuf = [0, 0] ; difBuf = [0, 0]
totBuf = [ (0,i,0) for i in range(0,totemLength) ]

def main():
   print("Neopixel Bounce - Cnt C to stop")
   initHardware() ; curCol =(0,120,0) 
   wipe() # clear all LEDs
   place=0 ; totCount = 0 ; stoped = True   
   while True:
      wipeC(0,circleLength,(0,0,0)) # blank circle LEDs
      if not stoped :
         set_led(place,curCol[0],curCol[1],curCol[2]) # current colour
      if place == launchPoint and difBuf[1] > 4: # right place and moving
         for i in range(totemLength-1,0,-1): # add to totem
            t = totBuf[i-1]
            totBuf[i] = t
         totBuf[0]= curCol     
         transToTot(length) # transfer all
         totCount +=1
         if totCount > totemLength :
            runEffects()
            totCount = 0
            wipeC(circleLength,circleLength+totemLength,(0,0,0))
            for i in range(0,totemLength):
               totBuf[i] = (0,0,0)
      ws2812.show()
      readSensor()
      if stoped and difBuf[0] > 4:
         stoped = False
      s = mapV(difBuf[1],0,500,0.1,0.002)
      curCol = setCol()
      time.sleep(abs(s))
      if difBuf[1] > 4 :
         place += 1
         stoped = False
         stopedTime = time.time()
         if place >= circleLength:
            place=0
      else: # slowly decay
         if time.time() - stopedTime > 2.0:
            stoped = True
            if totCount > -1 :
               if totCount >= totemLength :
                  totCount -=1
               totBuf[totCount] = (0,0,0)
               stopedTime = time.time()
               totCount -= 1
               if totCount < 0:
                  totCount = 0
               transToTot(length) # transfer all
               ws2812.show()
            
def runEffects(): # display when totem fills up
   for j in range(0,4): # ascending LEDs
       wipeC(circleLength,circleLength+totemLength,(0,0,0))
       ws2812.show()
       time.sleep(0.3)  
       for i in range(0,14):
         transToTot(circleLength+i+1)
         ws2812.show()
         time.sleep(0.1)      
   for i in range(0,10): # flash totem LEDs
      wipeC(circleLength,circleLength+totemLength,(0,0,0))
      ws2812.show()
      time.sleep(0.2)
      transToTot(length)
      ws2812.show()
      time.sleep(0.2)      
      
def transToTot(size): # transfer totem buffer to LEDs
   j=0
   for i in range(circleLength,size):
      set_led(i,totBuf[j][0],totBuf[j][1],totBuf[j][2])
      j+=1
      
def setCol(): # HSV colour space with S = V = 1
   h = abs(inBuf[0])
   while(h > 255):
      h -= 255
   if h < 85:
       return (int(h * 3), int(255 - h * 3), 0)
   elif h < 170:
       h -= 85
       return (int(255 - h * 3), 0, int(h * 3))
   else:
       h -= 170
       return (0, int(h * 3), int(255 - h * 3))

def wipeC(s, e,col): # wipe with a colour
   for i in range(s,e):
      set_led(i,col[0],col[1],col[2])
      
def mapV(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
     
def wipe(): # everything off
    for i in range(0,length):
       set_led(i,0,0,0) # black      
    ws2812.show()

def set_led(i, r, g, b):
    if i < LED_COUNT:
        ws2812.setPixelColorRGB(i, r, g, b)
    
def readSensor():
   lastBuf[0] = inBuf[0] ; lastBuf[1] = inBuf[1]
   for i in range(0,2):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel 
      inBuf[i] = (adc[1] & 3)<<8 | adc[2] # join two bytes together
   difBuf[0] = abs(inBuf[0] - lastBuf[0]) # work out changes
   difBuf[1] = abs(inBuf[1] - lastBuf[1])

def initHardware():
   global spi,lastX,lastY,ch0Low,ch1Low
   spi = spidev.SpiDev()
   spi.open(0,0)
   spi.max_speed_hz=1000000
           
# Main program logic:
if __name__ == '__main__':
   try:
     main()
   except: # clear up the LEDs
      wipe()
      ws2812.show()


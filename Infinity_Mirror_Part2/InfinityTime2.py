# Infinity mirror with time 2 - Using RPi.GPIO
# By Mike Cook - March 2016

import time, os, random
import RPi.GPIO as io
from neopixel import *
import gaugette.ssd1306

random.seed()
numberText = ["zero","one","two", "three", "four", "five", "six", "seven","eight",
                    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen","fifteen",
                     "sixteen", "seventeen", "eighteen","nineteen"]
upperNumberText = ["teen","twenty","thirty","forty","fifty"]
pastText = [" ","Five","Ten","1/4","20", "25", "Half"]
pastTextFull = ["nothing","five","ten","quarter","twenty", "twenty five", "half"]
toText = [" "," Five","  Ten","Quarter","Twenty", "   25", " Half"]

DATA_PIN  = 18 # pin connected to the NeoPixels
NUM_PIXELS = 16 # number of LEDs in the spiral
#OLED display
RESET_PIN = 15
DC_PIN    = 16
ROWS      = 64


try :
   io.setmode(io.BCM)
   io.setwarnings(False)
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)
   
pixels = Adafruit_NeoPixel(NUM_PIXELS,DATA_PIN,800000,5,False)
  
sensorPins = [17,24,23,27]
shutDownPin = 26
pattern = 0
patternTimeSteps = [0.5, 0.08, 0.05, 0.2, 0.01]
patternStep = 0 ; patternTemp = 0 ; patternTemp2 = 0
col = [ (255,0,0),(0,255,0),(0,0,255),(255,255,255),
        (255,0,0),(0,255,0),(0,0,255),(255,255,255) ]

display = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN, rows = ROWS)
display.begin()
display.clear_display()

def main():   
   initGPIO()

   while True:
     if io.input(shutDownPin) == 0 :
        #os.system("sudo shutdown -h now")
        print"shutdown",
        print io.input(shutDownPin)
     checkForDistance()
     advancePattern()
     time.sleep(patternTimeSteps[pattern])
     
def advancePattern():
   global patternStep, patternTemp, patternTemp2
   if pattern == 0:
      return # nothing to do
   if pattern == 1 :
     if patternStep == 0:
        patternTemp +=1
        if patternTemp >3 :
          patternTemp = 0
     wipe()
     pixels.setPixelColor(patternStep,Color(col[patternTemp][0]  ,col[patternTemp][1] ,col[patternTemp][2] ))  
     updateStep()
     return
   if pattern == 2 :
      if patternStep == 0:
         patternTemp +=1
         if patternTemp >3 :
            patternTemp = 0
      pixels.setPixelColor(patternStep,Color(col[patternTemp][0]  ,col[patternTemp][1] ,col[patternTemp][2] ))  
      updateStep()   
      return
   if pattern == 3 :
      wipe()
      off = patternStep & 0x03
      for L in range(0,NUM_PIXELS,4):         
         pixels.setPixelColor(L,   Color(col[off][0]  ,col[off][1] ,col[off][2] ))
         pixels.setPixelColor(L+1, Color(col[off+1][0],col[off+1][1],col[off+1][2]))
         pixels.setPixelColor(L+2, Color(col[off+2][0],col[off+2][1],col[off+2][2]))
         pixels.setPixelColor(L+3, Color(col[off+3][0],col[off+3][1],col[off+3][2]))
      updateStep()
      return
   if pattern == 4 :
      if patternStep == 0:
         patternTemp += 5
         if patternTemp > 255:
            patternTemp = 0
      pixels.setPixelColor(patternStep, Hcol(((patternStep * 256 / NUM_PIXELS) + patternTemp) & 255))         
      updateStep()      
      return
   
def initGPIO():
   for pin in range (0,4):
      io.setup(sensorPins[pin],io.IN, pull_up_down = io.PUD_UP)
      #io.pullUpDnControl(sensorPins[pin],2) # activate pull ups
   io.setup(shutDownPin,io.IN, pull_up_down = io.PUD_UP)
   pixels.begin() # This initializes the NeoPixel library.
      
def updateStep():
   global patternStep
   patternStep +=1
   if patternStep > NUM_PIXELS :
      patternStep =0
   pixels.show()
   
def wipe():
    for i in range(0,pixels.numPixels()):
       pixels.setPixelColor(i, Color(0,0,0)) 

def Hcol(h):
	if h < 85:
		return Color(h * 3, 255 - h * 3, 0)
	elif h < 170:
		h -= 85
		return Color(255 - h * 3, 0, h * 3)
	else:
		h -= 170
		return Color(0, h * 3, 255 - h * 3)

def checkForDistance():
   global pattern, patternStep
   if io.input(sensorPins[0]) == 1 :
      if pattern != 0: # if something showing
         wipe()
         pixels.show()
         pattern = 0 # stop any display
         patternStep = 0 # put to start of a pattern
         display.clear_display() # wipe time display
   else :
      close = 0
      for n in range(1,4):
         if io.input(sensorPins[n]) == 0 :
            close = n
      if pattern != close+1 : # has pattern changed      
         pattern = close+1
         patternStep = 0 # stage in pattern
         timeText = time.strftime("%X")
         printHardTime(int(timeText[0:2]),int(timeText[3:5]) )
         print"now showing pattern ",pattern
         
def printHardTime(hardH, minsR):
    display.clear_display()    
    offset = 0
    past = True
    if(random.randint(0,10) > 5) :
       past = False
    if(past) :
       offset = random.randint(1, 6)
    else :
       offset = random.randint(1, 5)
    if(past) :
      display.draw_text2(0,0,pastText[offset]+" past",2)
      hardM = minsR - (offset * 5)
      if hardM < 0 :
        hardM +=60
        hardH -= 1
        if(hardH < 1) :
          hardH = 23     
      printTimeW(hardH,hardM); 
    else :
      display.draw_text2(0,0,toText[offset]+" to",2)
      hardM = minsR + (offset * 5)
      if(hardM >= 60) :
        hardM -=60
        hardH += 1
        if(hardH > 23) :
           hardH = 1     
      printTimeW(hardH,hardM)    
    display.display();

def printWords(number,y,s):
  if(number < 20):
    display.draw_text2(0,y,numberText[number],s)
    return
  else :
    display.draw_text2(0,y,upperNumberText[(number-10) / 10]+" ",s)
    if number % 10 != 0 :
       n = len(upperNumberText[(number-10) / 10]+" ")*6
       display.draw_text2(n,y,numberText[number% 10],s)

def printTimeW(h, mins):
  past = True
  if(h > 12) :
     h -= 12
  if(mins > 30):
        mins = 60 - mins; # test for seconds being mins
        h += 1
        if(h > 12) :
           h = 1
        past = False   
  if((mins % 5) == 0) :
     if(mins != 0):  # time is on a 5 min interval  
        #print(pastTextFull[mins / 5])
        display.draw_text2(0,24,pastTextFull[mins / 5],1)
        if( past ) :
           display.draw_text2(0,32,"      past ",1)
        else :
           display.draw_text2(0,32,"      to ",1)
        printWords(h,48,2)
     else : # time is on the hour
        printWords(h,48,2)
  else :
    printWords(mins,24,1) #minutes
    if( past ):
      if(mins == 1):
         display.draw_text2(0,32,"minute past ",1)
      else :
         display.draw_text2(0,32,"minutes past ",1)
    else :
      if(mins == 1) :
         display.draw_text2(0,32,"minute to ",1)
      else :
        display.draw_text2(0,32,"minutes to ",1)
  printWords(h,48,2)
      
# Main program logic:
if __name__ == '__main__':    
    main()

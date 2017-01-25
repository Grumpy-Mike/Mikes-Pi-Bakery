#!/usr/bin/python
# Drum Like Me Pygame framework
import pygame, time, os
import wiringpi as io

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Drum like me")
screen = pygame.display.set_mode([300,40],0,32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT]) 
bufferLength = 40 # number of hits to store
delay = 0 ; startDelay = 1.6 # quite time before playback
lastEntry = 0.0 ; debounceTime = 0.05 # minimum time between entry
lastInstrument = -1 ; ledOn = [0.0,0.0,0.0,0.0,0.0] 
playing = False
   
def main():
   global lastPin, delay, playing,event,lastEntry,lastInstrument
   initResource()
   print"Drum like Me - By Mike Cook"
   clearBuffer()
   timeOut = time.time()
   while True:
      startTime = time.time()
      while not playing:
         checkForEvent()
         pressed = getPins()
         if pressed:
            timeOut = time.time()
         for pin in range(0,len(sensorPins)):
            if currentPin[pin] == 0 and lastPin[pin] != 0:
               if time.time() - lastEntry > debounceTime or lastInstrument != pin:
                  drums[pin].play()
                  placeInBuffer(pin,time.time())
                  lastInstrument != pin
            lastPin[pin] = currentPin[pin]
         if time.time() > (timeOut + startDelay):
            playing = True # start playing if nothing received for a set time
            delay = time.time()-startTime # length of sequence
            adjustBuffer(delay) # add delay into buffer
      while playing :
         checkForEvent()
         lookAtBuffer(delay)
         pressed = getPins()
         if pressed:
            playing=False
            clearBuffer()
             
def lookAtBuffer(delay): # see if something needs sounding
   global event, instrument,ledOn
   for i in range(0,bufferLength):
      if instrument[i] != -1 and time.time() >= event[i]:
         toPlay = instrument[i]
         drums[toPlay].play()
         io.digitalWrite(ledPins[toPlay],1) # turn on LED
         ledOn[toPlay] = time.time()
         instrument[i] = -1
         placeInBuffer(toPlay,time.time()+delay)
   for i in range(0,len(ledPins)):
      if ledOn[i] != 0 and time.time() > (ledOn[i]+debounceTime):
         io.digitalWrite(ledPins[i],0)
         ledOn[i] = 0.0
      
def adjustBuffer(delay): # add delay into buffer
   global event,instrument
   for i in range(0,bufferLength):
      if instrument[i] != -1:
         event[i] += delay
   
def clearBuffer():
   global instrument,event, lastInstrument, lastEnrty
   lastInstrument = -1
   lastEnrty = 0.0
   for i in range(0,bufferLength):
      instrument[i] = -1
      event[i] = 0.0
      
def getPins():
   down = False
   for pin in range (0,len(sensorPins)):
      currentPin[pin] = io.digitalRead(sensorPins[pin])
      if currentPin[pin] == 0:
         down = True      
   return down     

def placeInBuffer(drum,strikeTime):
   global event, instrument,lastEntry,lastInstrument
   place = 0 # find free space
   while instrument[place] !=-1 and place < bufferLength-1 :
      place+=1
   event[place] = strikeTime
   instrument[place] = drum
   lastEntry = strikeTime  
   
def initResource():
   global sensorPins,samples,drums,currentPin,lastPin,event,instrument,ledPins 
   sensorPins= [20,15,12,7,24] # GPIO pins for input sensors
   ledPins = [16,14,21,8,23] # GPIO pins for the LEDs
   samples = [ "clap.wav","ti.wav","drum.wav","top.wav","ride.wav"]
   drums = [ pygame.mixer.Sound("sounds/"+samples[sound])
                  for sound in range(0,len(sensorPins))]
   currentPin = [1 for pin in range(0,len(sensorPins))]
   lastPin = [1 for pin in range(0,len(sensorPins))]
   event = [ time.time() for b in range(0,bufferLength)]
   instrument = [ 1 for b in range(0,bufferLength)]
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,len(sensorPins)):
      io.pinMode(sensorPins[pin],0) # make pin into an input
      io.pullUpDnControl(sensorPins[pin],2) # enable pull up
   for pin in range (0,len(ledPins)):
      io.pinMode(ledPins[pin],1) # make pin into an output
      io.digitalWrite(ledPins[pin],0) # set output low
            
def terminate(): # close down the program
    pygame.mixer.quit() ; pygame.quit()
    for pin in range (0,len(ledPins)):
      io.digitalWrite(ledPins[pin],0) # turn LEDs off
    os._exit(1)

def checkForEvent(): # keyboard commands
    global playing
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          playing = False
          clearBuffer()
          
# Main program logic:
if __name__ == '__main__':    
    main()

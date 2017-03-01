#!/usr/bin/python
# Paperclip_Play - 5th Pi Birthday Bash activity  By Mike Cook - February 2017
import pygame, time, os
import wiringpi as io

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Paperclip player")
scrWidth = 300
screen = pygame.display.set_mode([scrWidth,40],0,32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.QUIT])
font = pygame.font.Font(None, 36) 
pinList = [21,26,20,19,13,6,16,5,12] # GPIO pins
instruments = ["Marimba","Synth","Piano","Bells"]
instrumentPointer = 0
freePlay = True

# Do-Re-Mi        note, minimum gap
tuneNotes = [     0, 150, 1, 50, 2, 150, 0, 50,
                  2, 100, 0, 100, 2, 150,
                  1, 150, 2, 50, 3, 50, 3, 50, 2, 50, 1, 50,
                  3, 150,
                  2, 150, 3, 50, 4, 150, 2, 50,
                  4, 100, 2, 100, 4, 150,
                  3, 150, 4, 50, 5, 50, 5, 50, 4, 50, 3, 50,
                  5, 150,
                  4, 150, 0, 50, 1, 50, 2, 50, 3, 50, 4, 50,
                  5, 150,
                  5, 150, 1, 50, 2, 50, 3, 50, 4, 50, 5, 50,
                  6, 150,
                  6, 150, 2, 50, 3, 50, 4, 50, 5, 50, 6, 50,
                  7, 150, 6, 50, 6, 50,
                  5, 100, 3, 100, 6, 100, 4, 100,
                  7, 100, 4, 100, 2, 100, 1, 100,
# second verse
                  0, 150, 1, 50, 2, 150, 0, 50,
                  2, 100, 0, 100, 2, 150,
                  1, 150, 2, 50, 3, 50, 3, 50, 2, 50, 1, 50,
                  3, 150,
                  2, 150, 3, 50, 4, 150, 2, 50,
                  4, 100, 2, 100, 4, 150,
                  3, 150, 4, 50, 5, 50, 5, 50, 4, 50, 3, 50,
                  5, 150,
                  4, 150, 0, 50, 1, 50, 2, 50, 3, 50, 4, 50,
                  5, 150,
                  5, 150, 1, 50, 2, 50, 3, 50, 4, 50, 5, 50,
                  6, 150,
                  6, 150, 2, 50, 3, 50, 4, 50, 5, 50, 6, 50,
                  7, 150, 6, 50, 6, 50,
                  5, 100, 3, 100, 6, 100, 2, 100,
                  7, 150, 
                  0, 50, 1, 50, 2, 50, 3, 50, 4, 50, 5, 50, 6, 50,
                  7, 100, 4, 100, 0, 100  ]
  
def main():
   initGPIO()
   initSamples()
   print"Paperclip player - By Mike Cook"
   print"Press the space bar to change the instrument"
   while True:
      checkForEvent()
      if freePlay :
         for pin in range (0,len(pinList)):
           if io.digitalRead(pinList[pin]) == 0:
              #print pin, pinList[pin]
              samples[pin].play()
              time.sleep(0.090)
              while io.digitalRead(pinList[pin]) == 0:
                  pass
              time.sleep(0.090) # debounce time
      else :
         playTune()
         
def playTune():
   global tunePointer,freePlay
   noContact(True)
   noContact(False)
   samples[tuneNotes[tunePointer]].play()
   time.sleep(tuneNotes[tunePointer+1]/150)
   tunePointer += 2
   if tunePointer >= len(tuneNotes):
      freePlay = True
      #print"tune finished"
      noContact(True)
      time.sleep(1.5)
      
def noContact(keyUp):
   test = keyUp
   while keyUp == test:
      checkForEvent()
      keyUp = False
      for pin in range (0,len(pinList)): # look for all keys up
         if io.digitalRead(pinList[pin]) == 0:
            keyUp = True
   time.sleep(0.090)        

def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,len(pinList)):
      io.pinMode(pinList[pin],0) # make pin into an input
      io.pullUpDnControl(pinList[pin],2) # enable pull up
      
def initSamples():
      global samples, instrumentPointer
      directory = instruments[instrumentPointer]
      samples = [ pygame.mixer.Sound(directory+"/"+str(pitch)+".wav")
               for pitch in range(0,len(pinList))]
      drawWords(directory,36,6)
      instrumentPointer += 1
      if instrumentPointer >= len(instruments):
         instrumentPointer = 0
   
def drawWords(words,x,y) :
        textSurface = pygame.Surface((len(words)*12,36))
        textRect = textSurface.get_rect()
        textRect.left = x ; textRect.top = y
        pygame.draw.rect(screen,(0,0,0), (x,y,scrWidth,26), 0)
        textSurface = font.render(words, True, (255,255,64), (0,0,0))
        screen.blit(textSurface, textRect)
        pygame.display.update()
      
def terminate(): # close down the program
    pygame.mixer.quit()
    pygame.quit()
    os._exit(1)
 
def checkForEvent(): # keyboard commands
    global freePlay,tunePointer
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          initSamples()
       if event.key == pygame.K_RETURN :
          freePlay = not(freePlay)
          tunePointer = 0
             
# Main program logic:
if __name__ == '__main__':    
    main()

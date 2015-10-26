#!/usr/bin/python
# Spoon-o-phone - Stylophone emulator By Mike Cook - September 2015
import pygame, time, os
import wiringpi2 as io

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Stylophone")
screen = pygame.display.set_mode([190,40],0,32)
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.QUIT])
font = pygame.font.Font(None, 36) ; vibrato = False  
pinList = [21,26,20,19,16,13,6,12,5,11,7,8,9,25,10,24,22,23,27,18] # GPIO pins
notes = ["a2","a#2","b2","c3","c#3","d3","d#3","e3","f3","f#3","g3","g#3",
         "a3","a#3","b3","c4","c#4","d4","d#4","e4"]

def main():
   initGPIO()
   print"Stylophone - By Mike Cook"
   drawWords("vibrato off",36,6)
   while True:
      checkForEvent()
      for pin in range (0,len(pinList)):
        if io.digitalRead(pinList[pin]) == 0:
           sound = getSample(pin)
           pygame.mixer.music.load("stylo_smpl/"+sound+".wav")
           pygame.mixer.music.set_volume(1.0)
           pygame.mixer.music.play(-1,0.0)
           time.sleep(0.030)
           while io.digitalRead(pinList[pin]) == 0:
               pass
           pygame.mixer.music.fadeout(100)
           time.sleep(0.030) # debounce time
           
def getSample(number):
   sample = notes[number]
   if vibrato :
      sample +="v"  
   return sample  
   
def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,len(pinList)):
      io.pinMode(pinList[pin],0) # make pin into an input
      io.pullUpDnControl(pinList[pin],2) # enable pull up
      
def drawWords(words,x,y) :
        textSurface = pygame.Surface((len(words)*12,36))
        textRect = textSurface.get_rect()
        textRect.left = x ; textRect.top = y
        pygame.draw.rect(screen,(0,0,0), (x,y,len(words)*12,26), 0)
        textSurface = font.render(words, True, (255,255,255), (0,0,0))
        screen.blit(textSurface, textRect)
        pygame.display.update()
      
def terminate(): # close down the program
    pygame.mixer.quit() ; pygame.quit()
    os._exit(1)
 
def checkForEvent(): # keyboard commands
    global vibrato
    event = pygame.event.poll()
    if event.type == pygame.MOUSEBUTTONDOWN:
       vibrato = not vibrato
       if vibrato:
          drawWords("vibrato on ",36,6)
       else:
          drawWords("vibrato off",36,6)
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
             
# Main program logic:
if __name__ == '__main__':    
    main()

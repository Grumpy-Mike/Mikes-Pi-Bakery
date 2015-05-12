# Safari - Car game
# By Mike Cook - May 2015

import pygame, time, os, random
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Wildlife Safari Park")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([600,400],0,32)

try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)
   
pinList= [2,3,4,15,17,18,27,22,23,24] # GPIO pins for input switches
random.seed()
random.shuffle(pinList)
visited =[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
duplicate = False
areaName =["Lion","Camel","Monkeys","Elephant","Zebra","Tiger",
            "Rhinoceros","Ostrich","Donkey","Kangaroo","intro","final"]
animalPicture = [ pygame.image.load("images/"+areaName[frame]+".jpg").convert_alpha()
                  for frame in range(0,12)]
enclosureSound = [ pygame.mixer.Sound("sounds/"+areaName[frame]+".wav")
                  for frame in range(0,10)]
def main():
   global visited, duplicate
   print"Wildlive Safari Park"
   print"press return to restart a tour"
   showPicture(10) # introduction picture
   initGPIO()
   while True:
     checkForEvent()
     scanSwitches()
     if finished() :
        visited =[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
        random.shuffle(pinList)
        print"Tour complete"
        if duplicate :
           print"... but you visited an area more than once"
           duplicate = False
        time.sleep(6.0)
        showPicture(11) #final picture
        time.sleep(6.0)
        showPicture(10) # introduction picture
        
def initGPIO():
   #for pin in range (0,pinList.len):
   for pin in range (0,10):
      io.pinMode(pinList[pin],0)
      io.pullUpDnControl(pinList[pin],2) # input enable pull up
      
def scanSwitches():
   global visited, duplicate
   for pin in range (0,10):
      if io.digitalRead(pinList[pin]) == 0:
         print"You have now visited the",areaName[pin],"area"
         enclosureSound[pin].play()
         showPicture(pin)
         if visited[pin] == 0:
            duplicate = True
            print"you have already been here"
         visited[pin] = 0
   return

def showPicture(animal):
   pygame.draw.rect(screen, (0,0,0), (0,0,600,400),0)
   screen.blit(animalPicture[animal],[0,0])
   pygame.display.update()
   time.sleep(0.4)
   
def finished(): # have we visited all the animals?
   finished = True
   for place in range(0,10):
      if visited[place] == -1:
         finished = False
   return finished            

def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global visited, duplicate
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_RETURN :
          visited =[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
          duplicate = False
          print"Start your tour again"
          showPicture(10) # introduction picture
          
# Main program logic:
if __name__ == '__main__':    
    main()

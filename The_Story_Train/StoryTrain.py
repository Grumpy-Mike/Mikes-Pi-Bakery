# The Story Train
# By Mike Cook - December 2015

import pygame, time, os
import wiringpi2 as io
from tkFileDialog import askopenfilename

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("The Story Train")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([600,400],0,32)

try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)

pinList= [2,3] # GPIO track sensing switches

def main():
   global pageList, pagesInStory
   initGPIO()
   print"The Story Train"
   while True:
      notFinished = True
      page = 1
      getStory() # get the story to show
      showPage(0) #begining picture      
      while notFinished:
        holdUntilSwitch(1)
        # trigger half way round display
        showPage(-1)
        holdUntilSwitch(0)
        # display page sound and picture
        showPage(page)
        page += 1
        if page >= pagesInStory :
           notFinished = False    
      showPage(pagesInStory) #the end
      time.sleep(2.0)
        
def initGPIO():
   for pin in range (0,len(pinList) ):
      io.pinMode(pinList[pin],0)
      io.pullUpDnControl(pinList[pin],2) # input enable pull up
      
def holdUntilSwitch(pin):
   global advance
   advance = False
   while (io.digitalRead(pinList[pin]) == 1) and (advance == False):
         checkForEvent()
         time.sleep(0.2) # let other apps have a look in
   return

def showPage(page):
   pygame.draw.rect(screen, (0,0,0), (0,0,600,400),0)
   if page ==-1 :
      screen.blit(nextPicture,[0,0])
      nextSound.play()
   else :   
      screen.blit(pagePictures[page],[0,0])
      pageSounds[page].play()
   pygame.display.update()
   time.sleep(0.4)   
   
def getStory():  # get the list of pages to show
   global pagePictures, pageSounds, pagesInStory, nextSound, nextPicture
   pathP = "nothing"
   pathS = "nothing"
   while not(os.path.exists(pathP) and (os.path.exists(pathS)) ):
      checkForEvent()
      filename = askopenfilename()
      path = os.path.dirname(filename)
      pathP = path + "/pages/"
      pathS = path + "/sounds/"
   pageList = [os.path.join(pathP,fn) for fn in next(os.walk(pathP))[2]]
   list.sort(pageList) # put in alphbetical order
   pagePictures = [ pygame.image.load(pageList[frame]).convert_alpha()
                  for frame in range(1,len(pageList))]  
   soundList = [os.path.join(pathS,fn) for fn in next(os.walk(pathS))[2]]
   list.sort(soundList) # put in alphbetical order
   pageSounds = [ pygame.mixer.Sound(soundList[frame])
              for frame in range(1,len(soundList))]
   pagesInStory = len(pagePictures)-1
   nextSound = pygame.mixer.Sound(path+"/nextComing.wav")
   nextPicture = pygame.image.load(path+"/nextComing.jpg").convert_alpha()

def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global advance
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_RIGHT :
          advance = True
          
# Main program logic:
if __name__ == '__main__':    
    main()

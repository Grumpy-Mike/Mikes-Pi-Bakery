# Pi Olympic Swimmer - Swimming simulator
# By Mike Cook - June 2016

import pygame, time, os, random
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("The Pi Olympic Swimmer")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([1000,415],0,32)
textHeight = 36
font = pygame.font.Font(None, textHeight)
random.seed()

compPins = [ 8,25,24,23]
ledPins = [ 7, 11, 4 ]
restart = True ; strokeState = 0

soundEffects = ["whistle","mark","go","end"]
swimingFrames = [ pygame.image.load("images/S"+str(frame)+".png").convert_alpha()
                  for frame in range(0,24)]
background =  pygame.image.load("images/BackgroundPi.png").convert_alpha()                  
gameSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".ogg")
                  for sound in range(0,4)]

def main():
   global restart, strokeState
   initGPIO()
   print"The Pi Olympic Swimmer"
   while True:
     if restart:
        frame = 0 ; distance = 0 ; manDistance = -85       
        posts = 3 ; ledOff() ; strokeState = 0        
        restart = False ; showPicture(frame,distance,-400,posts)
        time.sleep(2.0) ; gameSound[0].play()        
        print"Mount" ; time.sleep(4.0)        
        showPicture(frame,distance,manDistance,posts)       
        print"Take your mark" ; gameSound[1].play()        
        time.sleep(random.randint(2,5))
        print"Start" ; startTime = time.time()        
        gameSound[2].play()
     strokeDetect()   
     showPicture(frame,distance,manDistance,posts)
     manDistance += 4
     distance += 40
     if distance > 3000:
        distance -= 2000
        posts -=1
     frame = frame + 1
     if frame > 23:
        frame = 0
     if posts == 0 and distance >=100 :
        raceTime = int(100*(time.time() - startTime))
        gameSound[3].play()
        drawWords("Finished "+str(raceTime / 100.0)+" Seconds",400,258)
        pygame.display.update()
        print"Finished - type return for another race"
        while not restart:
           checkForEvent()
        
def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for pin in range (0,4):
      io.pinMode(compPins[pin],0) # mux pin to output
      io.pullUpDnControl(compPins[pin],2) # input enable pull up
   for pin in range (0,3):
      io.pinMode(ledPins[pin],1) # LED pin to output
      io.digitalWrite(ledPins[pin],0)      
      
def showPicture(frame,distance,manDistance,post):
   screen.blit(background,[-distance,0])
   if distance > 1000 :
      screen.blit(background,[1999-distance,0])
   drawWords(str(post),-distance+1932,220)   
   screen.blit(swimingFrames[frame],[60+manDistance,230])
   pygame.display.update()

def drawWords(words,x,y) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        pygame.draw.rect(screen,(102,204,255), (x,y,14,textHeight-10), 0)
        textSurface = font.render(words, True, (255,255,255), (102,204,255))
        screen.blit(textSurface, textRect)

def strokeDetect():
   global strokeState
   if strokeState == 0:
      while getSensor() != 1 :
         checkForEvent()
      io.digitalWrite(ledPins[2],0)      
      io.digitalWrite(ledPins[0],1)
      strokeState = 1
      return
   if strokeState == 1:
      while getSensor() != 3 :
         checkForEvent()
      io.digitalWrite(ledPins[0],0)      
      io.digitalWrite(ledPins[1],1)
      strokeState = 2
      return
   if strokeState == 2:
      while getSensor() != 7 :
         checkForEvent()
      io.digitalWrite(ledPins[1],0)      
      io.digitalWrite(ledPins[2],1)
      strokeState = 0
      return

def getSensor():
    sensor = 0
    for i in range(0,4) :
         sensor = (sensor << 1) | io.digitalRead(compPins[i])
    return sensor      

def ledOff():
   for pin in range (0,3):
      io.digitalWrite(ledPins[pin],0) # LED off        
   
def terminate(): # close down the program
    print "Closing down please wait"
    for pin in range (0,3):
      io.pinMode(ledPins[pin],0) # LED pin to input      
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global restart
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_RETURN :
          restart = True
          print"New Race"
          
# Main program logic:
if __name__ == '__main__':    
    main()

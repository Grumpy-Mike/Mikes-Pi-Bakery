# Pi Racer - Sprint simulator
# By Mike Cook - June 2015

import pygame, time, os, random
import RPi.GPIO as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("The Pi Sprinter")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([1000,400],0,32)
textHeight = 36
font = pygame.font.Font(None, textHeight)

try :
   io.setmode(io.BCM)
   io.setwarnings(False)
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)
   
pinList = [2,3] # GPIO pins for input switches
random.seed()
moved = 0
restart = True
soundEffects = ["marks","set","go","end"]

runningFrames = [ pygame.image.load("images/Man"+str(frame)+".png").convert_alpha()
                  for frame in range(0,12)]
background =  pygame.image.load("images/BackgroundPi.png").convert_alpha()                  
gameSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".wav")
                  for sound in range(0,4)]

def main():
   global moved, restart
   initGPIO()
   print"Pi Racer"
   while True:
     checkForEvent()
     if restart:
        frame = 0
        distance = 0
        manDistance = -85
        posts = 3
        moved = 1
        restart = False
        print"On your marks"
        gameSound[0].play()
        showPicture(frame,distance,manDistance,posts)
        time.sleep(2.0)
        print"Get set"
        gameSound[1].play()
        time.sleep(random.randint(2,5))
        print"Go"
        startTime = time.time()
        gameSound[2].play()           
     if moved > 0 :
        moved -= 1
        showPicture(frame,distance,manDistance,posts)
        manDistance += 5
        distance += 40
        if distance > 3000:
           distance -= 2000
           posts -=1
        frame = frame + 1
        if frame > 11:
           frame = 0
     if posts == 0 and distance >=1160 :
        raceTime = int(100*(time.time() - startTime))
        gameSound[3].play()
        drawWords("Finished "+str(raceTime / 100.0)+" Seconds",400,220)
        pygame.display.update()
        print"Type return for another race"
        while not restart:
           checkForEvent()
        
def initGPIO():
   print"Please ignore this stupid warning:-"
   for pin in range (0,2):
      io.setup(pinList[pin],io.IN, pull_up_down = io.PUD_UP)
      io.add_event_detect(pinList[pin],io.FALLING, callback=buttonPress, bouncetime=30)
      
def showPicture(frame,distance,manDistance,post):
   screen.blit(background,[-distance,0])
   if distance > 1000 :
      screen.blit(background,[1999-distance,0])
   drawWords(str(post),-distance+1932,220)   
   screen.blit(runningFrames[frame],[manDistance,0])
   pygame.display.update()

def drawWords(words,x,y) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        pygame.draw.rect(screen,(102,204,255), (x,y,14,textHeight-10), 0)
        textSurface = font.render(words, True, (255,255,255), (102,204,255))
        screen.blit(textSurface, textRect)

def buttonPress(number): #call back function
   global moved
   moved += 1
   
def terminate(): # close down the program
    print "Closing down please wait"
    io.cleanup()
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
          print"Start the race again"
          
# Main program logic:
if __name__ == '__main__':    
    main()

# Pi Derby - Horse race game
# By Mike Cook - November 2016

import pygame, time, os, random
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("The Raspberry Pi Derby")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([942,466],0,32)
textHeight = 36 ; textHeight2 = 24
font = pygame.font.Font(None, textHeight)
font2 = pygame.font.Font(None, textHeight2)

random.seed() ; winningPost = 704
ballPins = [ [17,24,4,27],[22,10,9,11 ] ]
targetGx = [ 18,102,18,102 ]
targetGy = [ 18,18,102,102 ]
gallopInc = [1,1] ; gallop= [0,0]
dInc = [0,0] # distance increment
puzzle = [5,5] ; restart = True
moveTarget = [1,1] ; movePhase = [0,0]

def main():
   global restart,dInc,gallop,puzzle,moveTarget,movePhase
   initGraphics()
   initGPIO()
   #print"The Pi Derby"
   distance = [-120, -120]
   showPicture(distance,gallop)
   while True:
     checkForEvent()
     if restart :
       gameSound[3].play() 
       windBack(distance)
       pygame.mixer.fadeout(1000)
       time.sleep(3.5)
       distance[0] = -120 ; distance[1] = -120
       gallop[0] = 0 ; gallop[1] = 0
       gallopInc[0] = 1 ; gallopInc[1] = 1
       dInc[0] = 0 ; dInc[1] = 0
       puzzle = [5,5]
       moveTarget = [1,1] ; movePhase = [0,0]
       gameSound[0].play()                
       showPicture(distance,gallop)
       time.sleep(5)
       restart = False # show Puzzle
       showPicture(distance,gallop)
  
     moveDetect(distance)
     if dInc[0] or dInc[1] :
        for n in range(0,2):
           if dInc[n] :
              distance[n] += 3
              if dInc[n] :
                 dInc[n] -=1
                 gallop[n] = gallopAdv(gallop,n)  
        showPicture(distance,gallop)
        if checkForFinish(distance):
           restart = True
           time.sleep(4.0)

def moveDetect(dis):
   global dInc, puzzle, moveTarget
   move = -1
   for n in range(0,2):
      move = checkInput(n) # look at ball switch
      if move != -1 :
      # check if it is a valid move   
         if move ==  moveTarget[n] :            
            if movePhase[n] == 1 : #move complete
               dInc[n] = 50 # move this * 3
               gameSound[1].play()
               last = moveTarget[n]
               puzzle[n] = random.randint(0,11)
               while last == moveState[puzzle[n]][0] :
                  puzzle[n] = random.randint(0,11)
               moveTarget[n] = moveState[puzzle[n]][0]
               movePhase[n] = 0
            else :
               moveTarget[n] = moveState[puzzle[n]][1]
               movePhase[n] = 1
               showPicture(dis,gallop) # update move graphic
               if n ==0 :
                 gameSound[4].play()
               else :
                  gameSound[5].play()
    
def gallopAdv(gallop,n):
   global gallopInc
   gallop[n] += gallopInc[n]
   if gallop[n] > 6 or gallop[n] <0:
         gallopInc[n] = -gallopInc[n]      
   return gallop[n]   
   
def checkForFinish(d):
   if d[0] >=winningPost or d[1] >=winningPost:
        gameSound[2].play()
        finish(d[0] - d[1])
        time.sleep(3.0)
        return True
   else :
      return False

def windBack(d):
   wind = 4
   while d[0] >= -120 or d[1] >= -120:
      showPicture(d,gallop)
      checkForEvent()
      for n in range(0,2):
         if d[n] >=-120:
            d[n] -= wind
            
def checkInput(player):
   ball = -1
   for pin in range(0,4):
      if io.digitalRead(ballPins[player][pin]) == 0 :
         ball = pin
   return ball      

def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)
   for player in range(0,2):   
     for pin in range (0,4):
        io.pinMode(ballPins[player][pin],0)
        io.pullUpDnControl(ballPins[player][pin],2) # input enable pull up
      
def showPicture(run,gal):
   screen.blit(background,[0,0])   
   screen.blit(horse1,[run[0],30+gal[0] ] )
   screen.blit(horse3,[run[1],120+gal[1] ] )
   screen.blit(foreground,[0,200])
   pygame.draw.rect(screen,(102,204,255), (0,340,942,136), 0)
   if not restart :
      screen.blit(move[puzzle[0]],[50,345])
      pygame.draw.circle(screen, (255,154,51),(targetGx[moveTarget[0]]+50,targetGy[moveTarget[0]]+345),8,0)
      screen.blit(move[puzzle[1]],[471+50,345])
      pygame.draw.circle(screen, (255,154,51),(targetGx[moveTarget[1]]+50+471,targetGy[moveTarget[1]]+345),8,0)
   drawWords("1 - Raspberry Rake",120+70,350,0)
   drawWords("3 - Not Quite Pi",120+471+70,350,0)
   drawWords(str(winningPost-run[0])+" to go",120+70,400,1)
   drawWords(str(winningPost-run[1])+" to go",120+70+471,400,1)
   pygame.display.update()

def finish(distance):
   if distance != 0:
      caption = "Wins by " + margin(abs(distance))
      if distance < 0 :
         x= 120+70+471
      else:
         x= 120+70
      drawWords(caption,x,400,1)
   else :
      drawWords("Dead heat",120+70,400,1)
      drawWords("Dead heat",120+70+471,400,1)
   pygame.display.update()
   

def margin(dist):
   separation = dist / 120.0
   if separation >1.8:
      return "a distance"
   elif separation >0.9:
      return "a length"
   elif separation >0.7:
      return "three quarters of a length"
   elif separation >0.4:
      return "half a length"
   elif separation >0.25:
      return "a neck"
   elif separation >0.2:
      return "a short neck"
   elif separation >0.1:
      return "a head"
   elif separation >0.05:
      return "a short head"
   else :
      return "a nose"
   
def drawWords(words,x,y,f) :
   if f == 0:
      th = textHeight
   else :
      th = textHeight2
   textSurface = pygame.Surface((14,th))
   textRect = textSurface.get_rect()
   textRect.left = x
   textRect.top = y
   pygame.draw.rect(screen,(102,204,255), (x,y,14,th-10), 0)
   if f==0 :
      textSurface = font.render(words, True, (0,0,0), (102,204,255))
   else :
      textSurface = font2.render(words, True, (0,0,0), (102,204,255))
   screen.blit(textSurface, textRect)
   
def initGraphics():
   global background,foreground,horse1,horse3,move, moveState, gameSound
   soundEffects = ["start","gallop","end","ratchet","horse1","horse2"]
   background =  pygame.image.load("images/track.png").convert_alpha()
   foreground =  pygame.image.load("images/rail.png").convert_alpha()
   horse1 =  pygame.image.load("images/rr.png").convert_alpha()
   horse3 =  pygame.image.load("images/np.png").convert_alpha()
   move = [ pygame.image.load("images/dir"+str(m)+".png").convert_alpha()
           for m in range(0,12) ]
   moveState = [ [0,3],[3,0],[2,1],[1,2],[0,1],[1,0],[0,2],[2,3],[3,1],
                 [1,3],[3,2],[2,0] ]
   gameSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".wav")
                  for sound in range(0,6)]

def terminate(): # close down the program
    print "Closing down please wait"
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
          
# Main program logic:
if __name__ == '__main__':    
    main()

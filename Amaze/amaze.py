# Amaze - maze game
# By Mike Cook - September 2015

import pygame, time, os
import wiringpi2 as io

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Amaze - Maze helper")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([800,665],0,32)
textHeight = 36
font = pygame.font.Font(None, textHeight)
#define the points to draw the barriers
slider1 = [(87,173),(172,159),(172,187),(210,159),(210,186),(248,157),(248,186),
          (401,157),(401,185), (440,157),(440,185),(516,157),(516,185)]
slider2 = [(84, 285),(209, 270),(209, 300),(325, 269),(325, 299),(403, 269),
          (403, 298),(558, 269),(558, 299),(596, 269),(596, 298)]
slider3 = [(81, 402),(207, 387),(207, 417),(327, 385),
          (327, 416),(445, 384),(445, 415),(563, 384),(563, 414)]
slider4 = [(78, 522),(166, 507),(166, 538),(206, 506),(206, 537),(246, 505),
          (246, 538),(327, 505),(327, 538),(448, 505),
          (448, 536),(568, 504),(568, 535),(607, 503),(607, 535)]
slider = [slider1, slider2, slider3, slider4]
sliderShift = [38,38,40,40] # amount to shift slider x position for each line
sliderState = [True,True,True,True] # True = left, False = right
mazeLook = [5,9,4,11,6,10,1,12,7,13,3,14,8,15,2,16]
textHeight = 36
font = pygame.font.Font(None, textHeight)
# solutions
m1  =[3] 
m2  =[3]
m3  =[1,0,3]
m4  =[1,0,0,3]
m5  =[2,1,0,0,3]
m6  =[1,2,1,0,0,3]
m7  =[0,2,1,0,0,3]
m8  =[1,0,2,1,0,0,3]
m9  =[0,3,0,2,1,0,0,3]
m10 =[1,0,3,0,2,1,0,0,3]
m11 =[2,0,3,0,2,1,0,0,3]
m12 =[2,1,0,3,0,2,1,0,0,3]
m13 =[1,0,1,0,3,0,2,1,0,0,3]
m14 =[2,1,0,1,0,3,0,2,1,0,0,3]
m15 =[1,1,0,1,0,3,0,2,1,0,0,3]
m16 =[2,1,1,0,1,0,3,0,2,1,0,0,3]
sol =[ [],m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12,m13,m14,m15,m16 ]
progress = 0


pinList = [22,27,17,4] # GPIO pins for sensor switches
background =  pygame.image.load("images/noSlide.jpg").convert_alpha()
restart = False
chosen = False # for options
mazeIDnumber = 1
helpLevelNumber = 2
helpLevel = ["No help", "Validate slide", "Show next slide","Start maze run now"]
soundEffects = ["slide","ping","wrong","finish","thanks","help"]
mazeSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".wav")
                 for sound in range(0,6)]

def main():
   global moved, restart, progress
   initGPIO()
   print"Amaze - click on the start button"
   while True:
      restart = False
      setMaze(choose())
      waitForSet() # player puts maze into that position
      progress = 0 # number of slides
      helpLevelRequired()
      if helpLevelNumber == 2:
         drawWords("First slider to move is "+str(sol[mazeIDnumber][progress]+1),366, 37)
         pygame.display.update()
      while not restart:
        checkForEvent()
        updateSensors()
        
def initGPIO():
   try :
      io.wiringPiSetupGpio()
   except :
      print"start IDLE with 'gksudo idle' from command line"
      os._exit(1)

   for pin in range (0,4):
      io.pinMode(pinList[pin],0)
      io.pullUpDnControl(pinList[pin],2) # input enable pull up
      
def showPicture(): #draws maze and sliders
   screen.blit(background,[0,0])
   lineCol = (230,20,0)
   for s in range(0,4):
      pygame.draw.circle(screen,lineCol,slider[s][0],4,0)
      points = len(slider[s])-1
      for block in range(1,points,2):
         pygame.draw.line(screen,lineCol,slider[s][block],slider[s][block+1],4)
   pygame.display.update()
   
def waitForSet(): # hold until maze is put into matchins position
   drawWords("Set your Maze like this",366, 37)
   pygame.display.update()
   while checkSetup():
      checkForEvent()
   showPicture()
   drawWords("Thank you",366, 37)
   pygame.display.update()
   mazeSound[4].play()
   time.sleep(3.0)

def checkSetup(): # see if sensors are registering correctlly
   done = True
   for i in range(0,4):
      if sliderState[i] != bool(io.digitalRead(pinList[i])):
         done = False
   return not done

def updateSensors(): # see if the sliders have changed
   for i in range(0,4):
      sensor = bool(io.digitalRead(pinList[i]))
      if sliderState[i] != sensor:
         toggleSlider(i, True)
         time.sleep(2.0)
   return     

def helpLevelRequired():
   global helpLevelNumber, chosen
   drawWords(helpLevel[helpLevelNumber],366, 37)
   drawWords("->",366,65)
   drawWords("Change help level ",398,65)
   pygame.display.update()
   mazeSound[5].play()
   current = helpLevelNumber
   chosen = False
   while not chosen:
      checkForEvent()
      if current != helpLevelNumber :
         current = helpLevelNumber
         showPicture()
         drawWords(helpLevel[helpLevelNumber],366, 37)
         drawWords("->",366,65)
         pygame.display.update()
   drawWords(helpLevel[3],366, 37)
   pygame.display.update()
   time.sleep(2)
   showPicture()
   
   
def choose():
   global chosen, mazeIDnumber
   chosen = False
   mazeIDnumber = 1
   currentMaze = mazeIDnumber
   showPicture()
   drawWords("Choose Maze",366, 37)
   drawWords("<-",536,65)
   drawWords("->",576,65)
   drawWords("01",556,37)
   pygame.display.update()
   while not chosen :
      checkForEvent()
      if mazeIDnumber != currentMaze :
         currentMaze = mazeIDnumber
         if currentMaze > 9 :
           ns = str(currentMaze)
         else :
           ns = "0"+str(currentMaze)
         drawWords(ns,556,37)
         pygame.display.update()
   return mazeIDnumber  
      
   
def drawWords(words,x,y) :
        textSurface = pygame.Surface((len(words)*12,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        pygame.draw.rect(screen,(81,133,133), (x,y,len(words)*12,textHeight-10), 0)
        textSurface = font.render(words, True, (180,180,180), (81,133,133))
        screen.blit(textSurface, textRect)
   
def toggleSlider(s,showHelp): #move sliders to the other side
    global sliderState, progress
    if showHelp :
       mazeSound[0].play()
    if sliderState[s] :
       shift = 2
    else :
       shift = -2
    sliderState[s] = not sliderState[s]
    moves = 0
    while moves != sliderShift[s] :
       moves += abs(shift)
       updateSlider(s,shift)
       showPicture()
    if showHelp and helpLevelNumber !=0 :
       time.sleep(0.8) # allow slide sound to finish
       if progress < len(sol[mazeIDnumber]):   
          if s != sol[mazeIDnumber][progress] :
             drawWords("Wrong - out of sequence",366, 37)             
             pygame.display.update()
             mazeSound[2].play()
             if helpLevelNumber == 2:
                time.sleep(3.0)
                drawWords("The next slider move should be "+str(sol[mazeIDnumber][progress]+1),366, 37)
                pygame.display.update()
          else :
             drawWords("OK",366, 37)             
             pygame.display.update()
             mazeSound[1].play()
             progress += 1
             if progress < len(sol[mazeIDnumber]) :
                if helpLevelNumber == 2:
                   time.sleep(1.2)
                   drawWords("OK - next slider is "+str(sol[mazeIDnumber][progress]+1),366, 37)
                   pygame.display.update()
             else:
                time.sleep(1.5)
                mazeSound[3].play()
                drawWords("Click on Finish when done",366, 37)             
                pygame.display.update()
       else:        
          drawWords("Move was not required",366, 37)             
          pygame.display.update()
    
def updateSlider(s,inc):
   global slider
   points = len(slider[s])
   for i in range(0,points):
      slider[s][i]= (slider[s][i][0] + inc,slider[s][i][1])
      
def mazeNumber(): # set the maze to an ID number
   mazeNum = 0
   for i in range(0,4):
      mazeNum = mazeNum << 1
      if sliderState[i] :
         mazeNum = mazeNum | 1         
   return mazeLook[mazeNum]

def setMaze(n):
   i = 0
   while mazeLook[i] != n:
      i += 1
   # i has the bit pattern of the slider states
   mask = 0x8
   for n in range(0,4):
      if (mask & i) == 0 and sliderState[n] == True:
         toggleSlider(n, False)
      elif (mask & i) != 0 and sliderState[n] == False:
         toggleSlider(n, False)
      mask = mask >> 1   
   
def terminate(): # close down the program
    print "Closing down please wait"
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # look at keys
    global restart, chosen, mazeIDnumber, helpLevelNumber
    event = pygame.event.poll()
    if event.type == pygame.MOUSEBUTTONDOWN:
       point = pygame.mouse.get_pos()
       #print point # print out position of click dor development
       if (point[0] > 366 and point[0] <520) and (point[1] > 37 and point[1] < 63):
          chosen = True             
       if (point[0] > 630 and point[0] <691) and (point[1] > 76 and point[1] < 94):
          chosen = True             
       if (point[0] > 535 and point[0] <557) and (point[1] > 67 and point[1] < 91):
          mazeIDnumber -= 1
          if mazeIDnumber < 1:
             mazeIDnumber = 16
       if (point[0] > 576 and point[0] <597) and (point[1] > 66 and point[1] < 90):
          mazeIDnumber += 1
          if mazeIDnumber > 16:
             mazeIDnumber = 1
       if (point[0] > 365 and point[0] <385) and (point[1] > 66 and point[1] < 91):
          helpLevelNumber +=1
          if helpLevelNumber >2:
             helpLevelNumber = 0
       if (point[0] > 661 and point[0] <725) and (point[1] > 607 and point[1] < 623):
          restart = True            

    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
       if event.key == pygame.K_RETURN :
          restart = True
       '''   
       if event.key == pygame.K_1 :
          toggleSlider(0, True)
       if event.key == pygame.K_2 :
          toggleSlider(1, True)
       if event.key == pygame.K_3 :
          toggleSlider(2, True)
       if event.key == pygame.K_4 :
          toggleSlider(3, True)
       '''   
# Main program logic:
if __name__ == '__main__':    
    main()

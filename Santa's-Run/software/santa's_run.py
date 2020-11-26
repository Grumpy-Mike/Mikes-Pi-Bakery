# Santa's Run - a Christmas game
# By Mike Cook - October 2020

import pygame
import time
import os
import random
import RPi.GPIO as io

def main():
    global restart, santaState, coverTrack, santaDistance, targetRect, disInc
    global santaL_R, delivered, santaHeight, drop, lastDistance, throwCount, distance
    init()
    initGPIO()
    print("Santa's Run")
    while True:
        if restart:
            distance = 0 ; lastDistance = 0 ; santaDistance = 0       
            santaState = 0 ; coverTrack=[] ; drop = False ; throwCount = 0
            delivered = 0 ; santaL_R = 0 ; santaHeight = rigel - 150 
            targetRect = []
            setUpGround()
            restart = False        
            showPicture(distance)              
        waitNextFrame()
        distance = santaDistance * 4
        showPicture(distance)
        santaHeight += 0.5 # normal loss of height
        if santaHeight >= rigel : santaHeight = rigel # peg the lowest he can get
        if santaHeight <= 0 : santaHeight = 0.0 # peg the highest he can get
        if santaDistance >= 1150 : santaL_R = 1 # reverse run at end of screen
        if santaDistance < 0 or throwCount >= 100: # stop at end of screen or when magazines run out   
         gameSound[3].play() # end
         drawWords("Finished "+str(delivered)+" MagPi magazines delivered ",400,258)
         drawWords("Type return for another run", 467, 300)
         pygame.display.update()
         while not restart:
             checkForEvent()

def init():
    global textHeight, font, restart, santaState, screen
    global soundEffects, santaFrames, background, chimney
    global cover, gameSound, snowLine, snowLineShort, drop
    global groundPlotType, groundPlotY, groundTypeW, coverTrack
    global targetRect, coverDrop, santaL_R, groundSpeed, rigel
    global dropVel, groundLine, frame
    pygame.init()                   # initialise graphics interface
    pygame.mixer.quit()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.display.set_caption("Santa's Run")
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])
    screen = pygame.display.set_mode([1250,526],0,32)
    textHeight = 36
    font = pygame.font.Font(None, textHeight)
    random.seed()
    restart = True ; santaState = 0 ; drop = False   
    santaFrames = [[0,0] for _ in range(9) ]
    frames1 = [ pygame.image.load("images/Santa/Santa"+str(frame)+".png").convert_alpha()
                       for frame in range(1,10)]    
    frames2 = [ pygame.transform.flip (pygame.image.load("images/Santa/Santa"+str(frame)+".png").convert_alpha(), True, False)
                      for frame in range(1,10)]
    santaL_R = 0 # santa image flip 0 l to r, 1 r to l
    frame = 0
    for i in range(9) :
        santaFrames[i][0] = frames1[i]
        santaFrames[i][1] = frames2[i]
    background =  pygame.image.load("images/stars.png").convert_alpha()
    chimney = pygame.image.load("images/chimney.png").convert_alpha()
    cover = [pygame.image.load("images/covers/"+str(cov)+"-Cover1.png").convert_alpha()
                   for cov in range(1,101) ]
    soundEffects = ["throw","hit","miss","end"]
    gameSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".wav")
                      for sound in range(0,4)]
    snowLine = pygame.image.load("images/snow_line.png").convert_alpha()
    snowLineShort = pygame.image.load("images/snow_line_short.png").convert_alpha()
    groundSpeed = 4
    groundPlotType = [chimney, snowLine, snowLineShort]
    groundPlotY = [466, 517, 517]
    groundTypeW = [130, 130, 65] # width of each type of ground
    coverTrack = []
    targetRect = []
    coverDrop = [0, 0, 0]
    rigel = 312
    dropVel = 0
    # define what we fly over 0 = double chimney 1 = long snow line 2 = short snow line
    groundLine = [1, 1, 0, 2, 0, 2, 0, 2, 1, 2, 0, 0, 2, 0, 2, 0, 0, 0, 0, 2, 2, 0, 2, 0,
                  1, 0, 1, 0, 0, 0, 1, 2, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 2, 0, 0, 1, 2, 0,
                  2, 0, 0, 1, 1, 1, 1]
    
def setUpGround():
    global coverTrack, targetRect
    targetRect = []
    coverTrack = []
    length = 0
    for i in range(len(groundLine)) :
        part = groundLine[i]
        if part == 0 :
            targetRect.append(pygame.Rect(length + 18, 481, 93, 32))
        if part == 2 :
            length += 65
        else :
            length += 130
    #print("ground line length",length)
    
def initGPIO():
    io.setwarnings(False)
    io.setmode(io.BCM)
    io.setup(2, io.IN)
    io.add_event_detect(2, io.FALLING, callback = shakeDetect, bouncetime = 30)
     
def showPicture(distance):
    global coverDrop, drop, dropVel, santaDistance
    screen.blit(background,[0,0])
    showGround(distance)
    ''' # uncomment to see catching rectangles
    for t in range(len(targetRect)) :
        pygame.draw.rect(screen, (0,128,0), targetRect[t], 0)
    '''    
    if drop :
        if dropVel != 0 :
            dropVel += 1
        else :
            dropVel = 2
        screen.blit(cover[coverDrop[0]], [ coverDrop[1], coverDrop[2] ])
        if santaL_R :
            coverDrop[1] -= 4
        else:
            coverDrop[1] += 4
        coverDrop[2] += dropVel
        if coverDrop[2] > 526: gameSound[2].play() ; drop = False ; dropVel = 0
        if catch(distance) :
            gameSound[1].play()
            drop = False
            dropVel = 0
            santaDistance += disInc * 8 # give a little kick
    screen.blit(santaFrames[frame][santaL_R],[santaDistance, santaHeight])
    pygame.display.update()

def showGround(scroll):
    global lastDistance
    if scroll != 0:
        delta = scroll - lastDistance
        for t in range(len(targetRect)):
                targetRect[t] = targetRect[t].move(-delta, 0)
        lastDistance = scroll        
    length = - scroll
    chunk = 0
    while length < 1250 :
        if length > -130 :
            screen.blit(groundPlotType[groundLine[chunk]],[length, groundPlotY[groundLine[chunk]]])
        length += groundTypeW[groundLine[chunk]]
        chunk += 1
    for coverCount in range(len(coverTrack)) :
        screen.blit(cover[coverTrack[coverCount][0]], [coverTrack[coverCount][1] - scroll,
                    413] )

def catch(offset) : # dropping cover collide with chimney catch rectangle
    global coverTrack, delivered
    caught = False
    for r in range(len(targetRect)):
        if targetRect[r].collidepoint((coverDrop[1], coverDrop[2] + 66)) or targetRect[r].collidepoint((coverDrop[1] + 50, coverDrop[2] + 66)):
            caught = True ; delivered += 1
            coverTrack.append([coverDrop[0], coverDrop[1] + offset, coverDrop[2]]) 
            #print("coverTrack list",coverTrack)
    return caught

def drawWords(words,x,y) :
    textSurface = pygame.Surface((14,textHeight))
    textRect = textSurface.get_rect()
    textRect.left = x
    textRect.top = y
    pygame.draw.rect(screen,(102,204,255), (x,y,14,textHeight-10), 0)
    textSurface = font.render(words, True, (255,255,255), (102,204,255))
    screen.blit(textSurface, textRect)

def shakeDetect(pin):
    global frame, coverDrop, throwCount, disInc, santaDistance
    global santaHeight
    frame = frame + 1
    if frame >= 9: frame = 0 # frame of animation
    disInc = 2
    if santaL_R : disInc = -2
    if drop :
        santaHeight -= 2 # go up
    else :
        santaDistance += disInc            
        
def throw():
    global santaHeight, drop, coverDrop, throwCount
    if drop : return
    else: 
        if santaHeight >= rigel : # boost up if too low
            santaHeight = 30.0
        else :
            drop = True    
    if drop:     
        if santaL_R :
            coverDrop = [throwCount, 100 + santaDistance, int(santaHeight)]
        else :
            coverDrop = [throwCount, santaDistance, int(santaHeight)]
        throwCount += 1 # number of covers thrown for next time
        gameSound[0].play() # throw

def waitNextFrame():
    autoTime = time.time()
    while time.time() - autoTime < 0.04:  
        checkForEvent()            
   
def terminate(): # close down the program
    print("Closing down")
    io.remove_event_detect(2) 
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
       if event.key == pygame.K_SPACE :
           throw()
       if event.key == pygame.K_RETURN :
          restart = True
          print("New Run")
    if event.type == pygame.MOUSEBUTTONDOWN :
        pass
        #print(pygame.mouse.get_pos())
        #os.system("scrot")
                
# Main program logic:
if __name__ == '__main__':    
    main()

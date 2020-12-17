# Santa's Run - a Christmas race game
# By Mike Cook - November 2020

import pygame
import time
import os
import random
import RPi.GPIO as io

def main():
    global restart, frame, santaDistance, targetRect
    global santaHeight, lastDistance
    init()
    initGPIO()
    print("Santa's Run")
    while True:
        if restart:
            frame = [0, 0]
            distance = [0, 0]
            lastDistance = [0, 0]
            santaDistance = [0, 0]       
            setUpGround()
            santaHeight = [199.0, 462.0]
            w1 = False ; w2 = False
            restart = False        
            showPicture(frame, distance)              
            gameSound[0].play()
        waitNextFrame()
        showPicture(frame,distance)
        santaHeight[0] += 0.5 # normal loss of height
        santaHeight[1] += 0.5 # normal loss of height
        if santaHeight[0] > 199.0 : santaHeight[0] = 199.0 # peg the lowest he can get
        if santaHeight[1] > 462.0 : santaHeight[1] = 462.0 # peg the lowest he can get
        distance[0] = santaDistance[0] * 4
        distance[1] = santaDistance[1] * 4         
        if santaDistance[0] >= 1090: w1 = True # player 0 winner
        if santaDistance[1] >= 1090: w2 = True  # player 1 winner
        if w1 or w2 : # one player has wone
            gameSound[3].play() # end
            if w1 :
                drawWords(" Red player is the winner! ", 486, 238)
            else:
                drawWords(" Green player is the winner! ", 486, 238)
            pygame.display.update()
            print("Finished - type return for another race")
            while not restart:
                checkForEvent()

def init():
    global textHeight, font, restart, screen
    global soundEffects, santaFrames, background, chimney
    global gameSound, snow, chimney2, chimney3
    global groundPlotType, groundPlotY, groundTypeW
    global targetRect, groundSpeed, frame, groundLine 
    pygame.init()                   # initialise graphics interface
    pygame.mixer.quit()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.display.set_caption("Santa's Dash")
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])
    screen = pygame.display.set_mode([1250, 526], 0, 32)
    textHeight = 36
    font = pygame.font.Font(None, textHeight)
    random.seed()
    restart = True    
    santaFrames = [[0,0] for _ in range(9) ]
    frames1 = [ pygame.image.load("images/Santa/Santa" + str(frame) + ".png").convert_alpha()
                       for frame in range(1,10)]    
    frames2 = [ pygame.image.load("images/Santa2/Santa" + str(frame) + ".png").convert_alpha()
                       for frame in range(1,10)] 
    for i in range(9) :
        santaFrames[i][0] = frames1[i]
        santaFrames[i][1] = frames2[i]
        
    background =  pygame.image.load("images/stars.png").convert_alpha()

    chimney = pygame.image.load("images/chimney.png").convert_alpha()
    chimney2 = pygame.image.load("images/chimney2.png").convert_alpha()
    chimney3 = pygame.image.load("images/tall.png").convert_alpha()
               
    soundEffects = ["throw", "hit", "miss", "end"]
    gameSound = [ pygame.mixer.Sound("sounds/" + soundEffects[sound] + ".wav")
                      for sound in range(0,4)]
    snow = pygame.image.load("images/snow.png").convert_alpha()
    frame =[0, 0]
    groundSpeed = 4
    groundPlotType = [chimney, chimney2, chimney3, snow]
    groundPlotY = [[203, 175, 92, 254], [466, 438, 355, 517] ] # the Y position for each background element
    groundTypeW = [64, 64, 64, 130] # width of each type of ground
    targetRect = []
    # define what we fly over 0 = chimney    1 = tall chimney
    # 2 = Very tall chimney   3 = snow line 
    groundLine = []
    for i in range(48): 
        groundLine.append(3) # fill all with snow
    # put in chimneys
    groundLine[5] = 1 ; groundLine[10] = 0 ; groundLine[11] = 1 
    groundLine[22] = 0 ; groundLine[23] = 1 ; groundLine[44] = 0 
    groundLine[30] = 2 ; groundLine[39] = 2 ; groundLine[34] = 1

def setUpGround(): # set up the blocking rectangles
    global targetRect, targetRectupper
    targetRect = []
    targetRectupper = []
    length = 0
    for i in range(len(groundLine)) :
        part = groundLine[i]
        if part == 0 :
            targetRect.append(pygame.Rect(length + 2, 466, 50, 60))
            targetRectupper.append(pygame.Rect(length + 2, 203, 50, 60))
            length += 64
        if part == 1 :
            targetRect.append(pygame.Rect(length + 2, 438, 50, 88))
            targetRectupper.append(pygame.Rect(length + 2, 175, 50, 88))
            length += 64
        if part == 2 :
            targetRect.append(pygame.Rect(length, 355, 52, 171))
            targetRectupper.append(pygame.Rect(length, 88, 52, 171))            
            length += 64
        if part == 3 :
            length += 130
    #print("ground line length",length, " Elements in ground line ", len(groundLine))
    
def showGround(i, scroll):
    global lastDistance
    if scroll != 0:
        delta = scroll - lastDistance[i]
        for t in range(len(targetRect)):
            if i == 0:
                targetRectupper[t] = targetRectupper[t].move(-delta, 0)
            else :    
                targetRect[t] = targetRect[t].move(-delta, 0)
        lastDistance[i] = scroll        
    length = - scroll
    chunk = 0
    while length < 1250 :
        if length > -130 :            
            screen.blit(groundPlotType[groundLine[chunk]], [length, groundPlotY[i][groundLine[chunk]]])
        length += groundTypeW[groundLine[chunk]]
        chunk += 1
    
def initGPIO():
    io.setwarnings(False)
    io.setmode(io.BCM)
    io.setup(2, io.IN)
    io.setup(3, io.IN)
    io.add_event_detect(2, io.FALLING, callback = shakeR)
    io.add_event_detect(3, io.FALLING, callback = shakeG)

def shakeR(pin): # red shaker
    global frame, santaHeight, santaDistance 
    frame[0] +=1
    if frame[0] >= 9: frame[0] = 0 # frame of Santa 1
    if blocked(0) :
        santaHeight[0] -= 1
    else:        
        santaDistance[0] += 1        
   
def shakeG(pin): # green shaker
    global frame, santaHeight, santaDistance
    frame[1] +=1
    if frame[1] >= 9: frame[1] = 0 # frame of Santa 2
    if blocked(1) :
        santaHeight[1] -= 2
    else:        
        santaDistance[1] += 2        
   
def showPicture(frame, distance):
    global santaDistance
    screen.blit(background,[0, 0])
    screen.blit(background,[0, 263])
    showGround(0, distance[0])
    showGround(1, distance[1])
    '''
    # uncomment to see catching rectangles
    for t in range(len(targetRect)) :
        pygame.draw.rect(screen, (0,128,0), targetRectupper[t], 1)
        pygame.draw.rect(screen, (0,128,0), targetRect[t], 1)
    '''    
    screen.blit(santaFrames[frame[0]][0],[santaDistance[0], santaHeight[0]])
    screen.blit(santaFrames[frame[1]][1],[santaDistance[1], santaHeight[1]])
    pygame.display.update()

def drawWords(words, x, y) :
    textSurface = pygame.Surface((14,textHeight))
    textRect = textSurface.get_rect()
    textRect.left = x
    textRect.top = y
    pygame.draw.rect(screen,(102,204,255), (x, y, 14, textHeight-10), 0)
    textSurface = font.render(words, True, (255, 255, 255), (102, 204, 255))
    screen.blit(textSurface, textRect)

def waitNextFrame():
    global autoTime
    autoTime = time.time()
    while time.time() - autoTime < 0.04:  
        checkForEvent()            

def blocked(i):
    block = False
    point = (santaDistance[i] + 159, santaHeight[i] + 60) 
    for t in range(len(targetRect)):
        if i == 0:
            if targetRectupper[t].collidepoint(point): block = True
        else:
            if targetRect[t].collidepoint(point): block = True
    return block     
    
def terminate(): # close down the program
    print("Closing down")
    io.remove_event_detect(2)
    io.remove_event_detect(3)  
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
    if event.type == pygame.MOUSEBUTTONDOWN :
        pass
        #print(pygame.mouse.get_pos())
        #os.system("scrot")
                
# Main program logic:
if __name__ == '__main__':    
    main()

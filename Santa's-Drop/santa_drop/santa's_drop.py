# Santa's Drop - a Christmas game
# By Mike Cook - November 2020

import pygame
import time
import os
import random
import copy
import RPi.GPIO as io

def main():
    global restart, coverTrack, caught
    global drop, throwCount, score, lastDrop
    init()
    initGPIO()
    print("Santa's Drop")
    while True:
        if restart:
            throwCount = 0 # change for a shorter game     
            drop = False ; frame = 0
            score = 0 ; caught = False
            restart = False
            lastDrop = time.time()
            showPicture(frame)              
        waitNextFrame()
        showPicture(frame)
        frame = frame + 1
        if frame >= 9: frame = 0 # frame of animation
        if throwCount >= 100: # stop when run out magazines
            throwCount = 0
            gameSound[3].play() # end
            drawWords("Finished all MagPi magazines dropped", 400, 258)
            drawWords("Type return for another drop", 467, 300)
            pygame.display.update()
            print("Finished - type return for another try")
            while not restart:
                 checkForEvent()

def init():
    global textHeight, font, restart, screen
    global soundEffects, santaFrames, background, chimney
    global cover, gameSound, speedDrop, coverDrop
    global dropVel, groundLine, sH, sW, chimneyX, chimneyp
    pygame.init()                   # initialise graphics interface
    pygame.mixer.quit()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.display.set_caption("Santa's Drop")
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])
    sW = 1250 ; sH = 650
    screen = pygame.display.set_mode([sW, sH], 0, 32)
    textHeight = 36
    font = pygame.font.Font(None, textHeight)
    restart = True    
    santaFrames = [ pygame.image.load("images/Santa/Santa"+str(frame)+".png").convert_alpha()
                       for frame in range(1, 10)]    
    background =  pygame.image.load("images/stars.png").convert_alpha()
    chimney = pygame.image.load("images/chimney.png").convert_alpha()
    chimneyp = pygame.image.load("images/chimneyp.png").convert_alpha()
    cover = [pygame.image.load("images/covers/" + str(cov) + "-Cover1.png").convert_alpha()
                   for cov in range(1, 101) ]
    soundEffects = ["throw", "hit", "miss", "end"]
    gameSound = [ pygame.mixer.Sound("sounds/" + soundEffects[sound] + ".wav")
                      for sound in range(0,4)]
    chimneyX = (sW // 2) - 123 # centre of screen
    coverDrop = [0, 0, 0]
    speedDrop = []
    random.seed(123) # always gives the same sequence if a number is put here
    for i in range(100):
        speedDrop.append([random.randint(-10, 10) , random.randint(2, 10)])
    speedDrop[0] = [0, 4]  # nice slow no need to move the chimney
        
def initGPIO():
    io.setwarnings(False)
    io.setmode(io.BCM)
    io.setup(2, io.IN)
    io.setup(3, io.IN)
    io.add_event_detect(2, io.FALLING, callback = shakeL, bouncetime=10)
    io.add_event_detect(3, io.FALLING, callback = shakeR, bouncetime=10)

def shakeL(pin):
    global chimneyX, coverDrop
    if chimneyX > -72: chimneyX -= 4
    if caught : coverDrop[1] -= 4
    
def shakeR(pin):
    global chimneyX, coverDrop
    if chimneyX < 1078: chimneyX += 4
    if caught : coverDrop[1] += 4
       
def showPicture(frame):
    global coverDrop, drop, caught, targetRect 
    global lastDrop, throwCount, dropSpeed
    screen.blit(background, [0, 0])
    updateScore(0)
    pygame.draw.rect(screen, (255, 255, 255), (0, sH - 24, sW, 24), 0)
    pygame.draw.line(screen, (52, 108, 139), (0, sH - 24), (sW, sH - 24), 3)
    screen.blit(chimney, [chimneyX, sH - 169])
    targetRect = pygame.Rect(chimneyX + 65, sH - 149, 121, 50)
    # uncomment to see catching rectangle
    #pygame.draw.rect(screen, (0, 128, 0), targetRect, 0)
    screen.blit(santaFrames[frame], [509, 0])
    if drop :
        drawWords("MagPi #"+str(throwCount + 1), 835, 20)
        coverDrop[1] += dropSpeed[0] # x movement of cover
        coverDrop[2] += dropSpeed[1] # y movement of cover
        if coverDrop[1] <= 0 : #bounce off left screen
            dropSpeed[0] = - dropSpeed[0]
            coverDrop[1] = 0 # put at edge of screen
        hight = coverDrop[2] / 372
        sX = int(100 * hight) ; sY = int(141 * hight)
        if coverDrop[1] + sX > sW :
            dropSpeed[0] = - dropSpeed[0]
            coverDrop[1] = sW - sX # put at edge of screen
        if sX < 100 or sY < 141 :   
            reduced = pygame.transform.smoothscale(cover[coverDrop[0]],(sX, sY))
            screen.blit(reduced, [ coverDrop[1], coverDrop[2] ])
        else :
            screen.blit(cover[coverDrop[0]], [ coverDrop[1], coverDrop[2] ])
            if coverDrop[2] > 627:
                gameSound[2].play()
                drop = False
                throwCount += 1
                lastDrop = time.time()
            if coverDrop[2] > 525 and caught:
                gameSound[1].play()
                drop = False
                throwCount += 1
                lastDrop = time.time()
                updateScore(coverDrop[0]+1)
            if not caught : caught = catch()
            if caught :
                dropSpeed[0] = 0 ; dropSpeed[1] = 4    
                screen.blit(chimneyp, [chimneyX, sH - 169])
    pygame.display.update()

def updateScore(increment):
    global score
    score += increment
    drawWords("Your score is " + str(score), 100, 20)
    
def catch() : # dropping cover collide with chimney catch rectangle
    caught = False
    if targetRect.collidepoint((coverDrop[1], coverDrop[2] + 141)) and targetRect.collidepoint(
        (coverDrop[1] + 100, coverDrop[2] + 141)):
        caught = True
    return caught

def drawWords(words, x, y) :
    textSurface = pygame.Surface((14, textHeight))
    textRect = textSurface.get_rect()
    textRect.left = x 
    textRect.top = y
    pygame.draw.rect(screen, (102, 204, 255), (x, y, 14, textHeight-10), 0)
    textSurface = font.render(words, True, (255, 255, 255), (102, 204, 255))
    screen.blit(textSurface, textRect)

def waitNextFrame():
    autoTime = time.time()
    while time.time() - autoTime < 0.04:  
        checkForEvent()            
    
def dropNext():
    global drop, dropSpeed, coverDrop, caught, throwCount
    drop = True
    coverDrop = [throwCount, 578, 20]
    dropSpeed = copy.deepcopy(speedDrop[throwCount])
    caught = False
    gameSound[0].play() # throw            
   
def terminate(): # close down the program
    print("Closing down")
    io.remove_event_detect(2)
    io.remove_event_detect(3)  
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global restart, drop, coverDrop, chimneyX
    if not drop and not restart and time.time() - lastDrop > 2.5 : dropNext()
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

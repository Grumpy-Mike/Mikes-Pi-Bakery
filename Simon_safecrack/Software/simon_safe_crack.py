# #!/usr/bin/env python3
# coding=utf-8
# Simon Safe Crack
# By Mike Cook Feb 2020

import time
import pygame
import pigpio
import os
import random
from ky040 import Ky040

os.system("sudo pigpiod")
time.sleep(1.0)

def main():
    global update, sequence
    init()
    drawScreen()
    say([0.8, "welcome to", "simon", "safe crack"])
    time.sleep(2.0)
    while 1 :
        fail = 0  # reset number of fails
        #generate new sequence
        for c in range(0, maxLength):
           sequence[c] = random.randint(2, 15)
        say([0.8, "Try and match", "this combination"])
        time.sleep(2.0)
        far = 1
        while fail < maxFails:
            saySeq(far)
            if getSeq(far) != -1 :# if sequence OK  
                far = far + 1            
                if far <= maxLength:
                    say([2.0, "yes"])
                    time.sleep(1)
                    say([1.0,"adding", "one more"])
                fail = 0 # reset number of fails
            else :
                fail += 1
                if fail < maxFails:
                    say([2.0, "no"])
                    say([1.0, "try", "that one",
                         "again"])
                else :
                    say([0.8, "maximum tries",
                         "exceeded"])
                    time.sleep(2)
                    print("Game over - Your score is",
                          far-1)
                    say([1.0, "your score is"])
                    say([0.8, str(far- 1)])
                    time.sleep(1.5)
            if far > maxLength:
                say([0.8, "this is", "too easy",
                     "for you"])
                terminate()
        say([2.0,"Game over"])
        time.sleep(2.0)
        say([2.0,"Next player"])        
        time.sleep(2.0)
   
def init():
    global tot, screen, knob, cp, dirChange
    global maxLength, sequence, maxFails, lastInc
    tot = 0 ; dirChange = False ; lastInc = 0
    pygame.init()
    pygame.display.set_caption("Simon Safe Crack")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,
                              pygame.QUIT])
    screenWidth = 380 ; screenHight = screenWidth
    cp = (screenWidth // 2, screenHight // 2)
    screen = pygame.display.set_mode([screenWidth,
                                screenHight], 0, 32)
    loadImages()
    knob = Ky040(clk=22, dt=27, cbrot = callbackRot,
            sw = 17, cbr=callbackSwR, cbf=callbackSw)
    maxLength = 25 # maximum sequence due to cheating
    sequence = [1] * maxLength 
    maxFails = 3 # number of fails before game ends
    random.seed()
               
def saySeq(length):
    for num in range(0,length + 1):
      if num == length :
          say([0.8, "one"])
          #print(1)
      else :
          say([0.8, str(sequence[num])])
          #print(sequence[num])
      if num % 2 :
          say([1.5, "left"])
      else :
          say([1.5, "right"])         
          
def getSeq(length):
    global tot
    say([1.0, "Now", "you try"])
    tot = 0 ; drawScreen() # display start position
    for press in range(0, length):
       attempt = getClicks(press)
       if attempt != sequence[press]:
          time.sleep(0.8)
          return -1
    return 1

def getTry(n) :
    getClicks(n)

def getClicks(n) :
    global tot, dirChange, lastInc
    dirChange = False 
    startTot = tot # start position
    lastInc = 1
    if n & 1 :
        lastInc = -1
    while not dirChange:
        checkForEvent()
    startTot += lastInc + 1*lastInc
    if n == 0 : # first time
        startTot -= lastInc
    return abs(startTot - tot)

def loadImages():
   global dial
   dial = pygame.image.load(
       "images/lockDials.png").convert_alpha()

def drawScreen() :
    screen.fill((0, 95, 190))
    blitRotate(screen, dial, cp, (150, 150),
               float(tot * 3.6))
    pygame.draw.line(screen, (0, 255, 0), (cp[0], 20),
                     (cp[0], 38), 3)
    pygame.display.update()
    
def blitRotate(surf, image, pos, originPos, angle):
    # curtesy of Rabbid76 - Stack Overflow
    # find the axis aligned bounding - rotated image
    w, h = image.get_size()
    box = [pygame.math.Vector2(p)
           for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box = (min(box_rotate, key=lambda p: p[0])[0],
                min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0],
                max(box_rotate, key=lambda p: p[1])[1])
    # calculate the translation of the pivot 
    pivot = pygame.math.Vector2(originPos[0], 
                              - originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot
    # find the upper left origin of the rotated image
    origin = (pos[0] - originPos[0] + min_box[0]
              - pivot_move[0], pos[1] - originPos[1]
              - max_box[1] + pivot_move[1])
    # get a rotated image
    rotated_image = pygame.transform.rotate(image,
                                            angle)
    # rotate and blit the image
    surf.blit(rotated_image, origin)
   
def callbackRot(inc):
    global tot, dirChange, lastInc
    tot += inc
    if inc != lastInc :
        dirChange = True
        lastInc = inc
    drawScreen()

def callbackSw(pin, level, tick):
    terminate()

def callbackSwR(pin, level, tick):
    pass

def say(words) :
    for w in range(1, len(words)) :
        checkForEvent()
        word = words[w]
        os.popen('espeak "'+word+'" --stdout | aplay ')
        time.sleep(words[0])
   
def terminate(): # close down the program
    say([1.5,"closing down","good bye"])
    knob.cancel()
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()

if __name__ == '__main__':
    main()

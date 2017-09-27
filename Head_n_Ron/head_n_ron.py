#!/usr/bin/env python3
# Head 'n Ron collider game
# By Mike Cook - August 2017

import pygame,time, random
import RPi.GPIO as io

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
random.seed()
 
def main():
   global score, rightSpeed, speedThreshold, hInterval, rInterval
   global countR, countH
   print("Head n Ron collider game")
   print("Ctrl C to quit")
   init()
   while 1:
      clr()
      countR = random.randint(0,11)
      countH = random.randint(0,11)      
      score = 0
      hInterval = 2.0 ; rInterval = 1.5
      speedThreshold = 1.0
      io.output(speed[0],1)
      io.output(speed[1],0)
      rightSpeed = False
      while playRound(): # keep going until you miss
        pass
      miss.play()
      print("Score",score)
      a = input("Press return to play again")
      
def playRound():
   global countH, countR, lastRon, lastHead, overlap, score
   global rightSpeed, rInterval, hInterval, speedThreshold
   done = False
   if time.time() - lastRon > rInterval:
      countR = moveR(countR)
      lastRon = time.time()
      if countR == countH:
        if io.input(2) ==1 :
            overlap = True

      if not rightSpeed and rInterval > speedInc:
        rInterval -= speedInc
        hInterval -= speedInc
        if rInterval < speedThreshold:
          io.output(speed[0],0)
          io.output(speed[1],1)
          rightSpeed = True        
   if time.time() - lastHead > hInterval:
      countH = moveH(countH)
      lastHead = time.time()
      if countR == countH:
        if io.input(2) ==1 :
            overlap = True

   if countR != countH and overlap: # have they passed
      overlap = False
           
   if io.input(2) ==0 :
      if overlap and rightSpeed:    
         print("bang")
         bang.play()
         while pygame.mixer.get_busy():
             pass
         overlap = False
         # make go faster
         if speedThreshold > speedInc:
            speedThreshold -= 0.1 # change colliding speed
         hInterval = 2.0 ; rInterval = 1.5
         score +=1
         io.output(speed[0],1)
         io.output(speed[1],0)
         rightSpeed = False
         time.sleep(0.8)
      else:
          if not rightSpeed: 
            print("not going fast enough")
          else:
            print("not in the right position")  
          done = True
   return not done   
    
def moveH(count):
    io.output(heads[count],0)
    count += 1
    if count > 11:
        count = 0
    io.output(heads[count],1)
    return count

def moveR(count):
    io.output(rons[count],0)
    count -= 1
    if count < 0:
        count = 11
    io.output(rons[count],1)
    return count

def init():
   global heads, rons, speed, hInterval, rInterval
   global countH, countR, lastRon, lastHead, overlap
   global rightSpeed, speedInc, speedThreshold, bang, miss
   countH = 4 ; countR = 0
   lastRon = time.time()
   lastHead = time.time()
   overlap = False ; rightSpeed = False
   heads = [14,15,18,23,24,25,8,7,12,16,20,21]
   rons = [3,4,17,27,22,10,9,11,5,6,13,19]
   speed = [0,1] #speed LED
   hInterval = 2.0 ; rInterval = 1.5
   speedInc = 0.1
   speedThreshold = 1.0
   io.setwarnings(False)
   io.setmode(io.BCM)
   io.setup(heads, io.OUT)
   io.setup(rons, io.OUT)
   io.setup(speed, io.OUT)
   io.setup(2, io.IN) # foot switch
   bang = pygame.mixer.Sound("sounds/Screech.wav")
   miss = pygame.mixer.Sound("sounds/Spiral.wav")

def clr():
    for led in range(0,12):
       io.output(heads[led],0)
       io.output(rons[led],0)
    io.output(speed[0],0)
    io.output(speed[1],0)   

# Main program logic:
if __name__ == '__main__':
   try:  
      main()
   finally:
      clr()
      pygame.mixer.quit()
      pygame.quit() # close pygame


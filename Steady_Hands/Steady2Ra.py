# Steady hands game - python 2
# with sound effects
# run with - sudo python Steady2Ra.py
# updated to be Revision Aware, to cope with board revisions 1 & 2 

import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *

def findRevision():
    global boardRevision
    fin = open('/proc/cpuinfo')
    boardRevision = -1
    while True: # go through the file line by line
       line = fin.readline()
       if not line: break # end if reached the end of the file
       if "Revision" in line:
         rev = line[11:15]
         if rev == "0002" or rev == "0003" :
           boardRevision = 1
         if rev == "0004" or rev == "0005" or rev == "0006" :
           boardRevision = 2
    fin.close()
    if boardRevision == -1: print "Error can't find board revision"
# end of function definitions


pygame.init()
pygame.mixer.quit()
pygame.mixer.init()

print "Loading sound files"
hitSound = pygame.mixer.Sound("sounds/hit.ogg")
endSound = pygame.mixer.Sound("sounds/applause.ogg")
resetSound = pygame.mixer.Sound("sounds/reset.ogg")
startSound = pygame.mixer.Sound("sounds/off.ogg")


# use BCM GPIO numbering - use anything else and you are an idiot!
GPIO.setmode(GPIO.BCM)

boardRevision = -1
findRevision()
print "Hi from Python :- Steady Hands game with sound"
delay = range(0,5000)
dum = 0
if boardRevision == 1:
    wire = 1
    end_rest = 0
    print "On a revision 1 board"
if boardRevision == 2:
    wire = 3
    end_rest = 2
    print "On a revision 2 board"
start_rest = 4
# set up GPIO input pins
#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
GPIO.setup(start_rest, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Physical pins 0 & 1 have hardware pull ups fitted in the Pi so don't enable them
GPIO.setup(wire, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(end_rest, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

while True:
#wait until the wand is at the start
 print "Move the loop to the start rest"
 while GPIO.input(start_rest) != 0:
   time.sleep(0.8)

#now we are at the start of the bendy wire
 resetSound.play()
 print "Start when you are ready"
#wait until the loop is lifted off the wire
 while GPIO.input(start_rest) == 0:
   time.sleep(0.1)
 print "Your off"
 startSound.play()
#time the run to the other rest
 penalty = 0
 run_time = time.clock()

 while GPIO.input(end_rest) != 0:
    if GPIO.input(wire) == 0:
      hitSound.play()
      penalty = penalty + 1
      print "Penalties total", penalty, " points"
      time.sleep(0.07)
 score = time.clock() - run_time + (penalty * 0.07)
 endSound.play()
 print "The run time was", score, "seconds with", penalty, "Penalty points"
#finished a run so start again


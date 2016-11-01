# Steady hands game - python 2
# with sound effects
# run with - sudo python Steady2.py

import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *

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

# set up GPIO input pins
#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO 0 & 1 have hardware pull ups fitted in the Pi so don't enable them
GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

print "Hi from Python :- Steady Hands game"
delay = range(0,5000)
dum = 0
start_rest = 4
end_rest = 0
wire = 1
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


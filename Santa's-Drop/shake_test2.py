# Shake test for two shakers
# By Mike Cook - November 2020

import RPi.GPIO as io

leftCount = 0
rightCount = 0

def shakeL(pin):
    global leftCount
    print("shake left")
    leftCount += 1
    if leftCount > 10 :
        print("Left test done")
        io.remove_event_detect(2)
    
def shakeR(pin):
    global rightCount
    print("shake right")
    rightCount += 1
    if rightCount > 10 :
        print("Right test done")
        io.remove_event_detect(3)

print("Test shakers, shake now")
print("Press return when both tests are finished")
io.setwarnings(False)
io.setmode(io.BCM)
io.setup(2, io.IN)
io.setup(3, io.IN)
io.add_event_detect(2, io.FALLING, callback = shakeL, bouncetime=30)
io.add_event_detect(3, io.FALLING, callback = shakeR, bouncetime=30)

def shakeL(pin):
    global chimneyX, coverDrop
    if chimneyX > -72: chimneyX -= 4
    if caught : coverDrop[1] -= 4
    
def shakeR(pin):
    global chimneyX, coverDrop
    if chimneyX < 1078: chimneyX += 4
    if caught : coverDrop[1] += 4
    
    

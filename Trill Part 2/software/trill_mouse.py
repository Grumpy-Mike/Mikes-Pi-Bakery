#!/usr/bin/env python3
# trill_mouse - controls the mouse position with a square or hex pad
# using pyautogui - install with:- pip3 install pyautogui
# by Mike Cook Jan 2021

import pyautogui
import time
from trill_lib import TrillLib

lastYmove = 0 ; lastXmove = 0
lastTouched = time.time()
# control the fineness of movement over the sensor
rm = 100 # Trill location Reading Multiplyer 

def main():
    global touchSensor
    touchSensor = TrillLib(1, "square", 0x28)
    touchSensor.setPrescaler(3)
    screenWidth, screenHeight = pyautogui.size()
    print("screen size", screenWidth, screenHeight)

    while(1):
        moveMouse()
        time.sleep(0.05)

def moveMouse():
    global lastYmove, lastXmove, lastTouched
    touchSensor.readTrill()
    if touchSensor.getNumTouches() !=0 and touchSensor.getNumHorizontalTouches() != 0: # only move when touched
        currentMouseX, currentMouseY = pyautogui.position()
        if time.time() - lastTouched > 0.2 : # new touch after release
            lastYmove = int(touchSensor.touchLocation(0) * rm)
            lastXmove = int(touchSensor.touchHorizontalLocation(0) * rm)
        lastTouched = time.time()        
        moveY = int(touchSensor.touchLocation(0) * rm)
        moveX = int(touchSensor.touchHorizontalLocation(0) * rm)
        update = False
        if moveY != lastYmove :
            update = True
            deltaY = moveY - lastYmove # swap to change direction
            lastYmove = moveY
        else :
            deltaY = 0
        if moveX != lastXmove :
            update = True
            deltaX = lastXmove - moveX # swap to change direction
            lastXmove = moveX
        else :
            deltaX = 0            
        if update : pyautogui.moveTo(currentMouseX + deltaX, currentMouseY + deltaY)

# Main program logic:
if __name__ == '__main__':
   main()


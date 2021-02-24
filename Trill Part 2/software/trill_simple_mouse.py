#!/usr/bin/env python3
# trill_simple_mouse - controls the mouse position with a square or hex pad
# one to one mapping trill position - mouse position
# two touches == mouse click at current poition
# using pyautogui - install with:- pip3 install pyautogui
# by Mike Cook Jan 2021

import pyautogui
import time
from trill_lib import TrillLib

lastTouched = time.time() 

def main():
    global touchSensor, screenWidth, screenHeight
    print(" Simple Trill to Mouse. Ctrl C to quit")
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
    if touchSensor.getNumTouches() >1 or touchSensor.getNumHorizontalTouches() >1:
        pyautogui.click()
        #print("click")
        while touchSensor.getNumTouches() != 0 and touchSensor.getNumHorizontalTouches() != 0 :
            touchSensor.readTrill()
            time.sleep(0.2)
        return    
    if touchSensor.getNumTouches() !=0 and touchSensor.getNumHorizontalTouches() != 0: # only move when touched       
        posY = int(touchSensor.touchLocation(0) * screenHeight)
        posX = int(touchSensor.touchHorizontalLocation(0) * screenWidth)           
        #pyautogui.moveTo(posX, posY) # direct mapping
        pyautogui.moveTo(screenWidth - posX, posY) # reverse X movement
        #pyautogui.moveTo(posX, screenHeight - posY) # reverse Y movement
        #pyautogui.moveTo(screenWidth - posX, screenHeight - posY) # reverse X & Y movement

# Main program logic:
if __name__ == '__main__':
   main()


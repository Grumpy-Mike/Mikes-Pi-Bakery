#!/usr/bin/env python3
# trill_simple_mouse - controls the mouse position with a square or hex pad
# one to one mapping trill position - mouse position
# two touches == mouse click at current poition
# mouse scrolling with ring sensor two touches == click
# using pyautogui - install with:- pip3 install pyautogui
# by Mike Cook Jan 2021

import pyautogui
import time
from trill_lib import TrillLib

def main():
    global screenWidth, screenHeight
    init()
    print(" Simple Trill to Mouse. Ctrl C to quit")
    
    screenWidth, screenHeight = pyautogui.size()
    print("screen size", screenWidth, screenHeight)

    while(1):
        moveMouse()
        scrollMouse()
        time.sleep(0.05)

def init():
    global lastTouched, lastRingTouchTime, lastScroll, scroll
    global touchSensor, ringSensor 
    lastTouched = time.time()
    lastRingTouchTime = time.time()
    lastScroll = 0
    touchSensor = TrillLib(1, "square", 0x28)
    touchSensor.setPrescaler(3)
    ringSensor = TrillLib(1, "ring", 0x38)
    ringSensor.setPrescaler(3)
    
def scrollMouse():
    global lastRingTouchTime, lastScroll
    ringSensor.readTrill()
    numTouch = ringSensor.getNumTouches()
    if numTouch > 1 :
        pyautogui.click()
        time.sleep(1.0)
        return
    if numTouch != 0 : # when touched
        scroll = int(ringSensor.touchLocation(0) * 10) # only use first touch
        if time.time() - lastRingTouchTime > 0.5 : # new touch after release
            lastScroll = scroll
        lastRingTouchTime = time.time()    
        if abs(scroll - lastScroll) > 0 : # found a change
            delta = scroll - lastScroll
            #print("delta", delta)
            lastScroll = scroll
            click = delta
            if delta == -9 : # gone round once clockwise
                click -= delta
                click += 1
            if delta == 9 :  # gone round once anticlockwise
                click -= delta
                click -= 1                    
            #print("click", click)
            pyautogui.scroll(click)

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


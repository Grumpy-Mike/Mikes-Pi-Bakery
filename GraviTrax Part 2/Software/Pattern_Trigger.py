#!/usr/bin/env python
# Testing Neopixel and FL3731 patterns from a thread
# By Mike Cook November 2019

import Neo_Thread as ws
import FL3731_Thread as fl

ws.initIO()
fl.initI2C()
print("To quit just type return")
print("To trigger FL3731 threads add 10 to the number you type")
print("To stop animations and counts type 100")
try:
    while 1:
        thread = int(input("Thread to trigger "))
        if thread >=0 and thread <=7 : 
            ws.startWs2812Thread(thread)
        if thread >=10 and thread <= 16 :
            fl.startFL3731Thread(thread - 10)
        if thread == 100 :
            fl.stopCount()
            fl.stopAnimations()
except :
     fl.stopCount()
     fl.stopAnimations()
    


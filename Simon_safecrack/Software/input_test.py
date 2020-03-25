#!/usr/bin/env python
import time
import pigpio
from ky040 import Ky040
import os

time.sleep(1.0)
os.system("sudo pigpiod")

tot = 0
def callbackRot(inc):
    global tot
    tot += inc
    print("Counter value: ", tot )

def callbackSw(pin, level, tick):
    print(tick,"Switch press")

def callbackSwR(pin, level, tick):
    print(tick,"Switch released")

my_rotary = Ky040(clk=22, dt=27, cbrot = callbackRot,
            sw = 17, cbr=callbackSwR, cbf=callbackSw)
print("looking at encoder ctrl c to quit")
while 1 : # let the callback functions update the display
    pass



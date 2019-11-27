#!/usr/bin/env python
'''
FL3731 patterns from a thread
By Mike Cook November 2019
With some functions from Pimoroni examples
See Pimoroni site for how to install
the matrix11x7 and ledshim libiaries
'''
import threading
import time
from matrix11x7 import Matrix11x7
from matrix11x7.fonts import font5x7
import random
import colorsys
from sys import exit
import ledshim
try:
    import numpy as np
except ImportError:
    exit('This script requires the numpy module\nInstall with: sudo pip install numpy')
ledshim.set_clear_on_exit()
        
def startFL3731Thread(number):
    if number == 0:
        matrix_thread0 = threading.Thread(target =
                   spinC, args = (2, 0.008, 0.1, 0.01))
        matrix_thread0.start()
    elif number == 1:
        matrix_thread1 = threading.Thread(target =
                   spinA, args = (2, 0.008, 0.1, 0.01))
        matrix_thread1.start()
    elif number == 2:
        matrix_thread2 = threading.Thread(target =
                        timer, args = (2, 1.0))
        matrix_thread2.start()
    elif number == 3:
        matrix_thread3 = threading.Thread(target =
                         solid, args = ())
        matrix_thread3.start()
    elif number == 4: 
        matrix_thread4 = threading.Thread(target =
                         pulse, args = ())
        matrix_thread4.start()
    elif number == 5: 
        matrix_thread5 = threading.Thread(target =
                         larson, args = ())
        matrix_thread5.start()
    elif number == 6: # after shim background animate
        matrix_thread6 = threading.Thread(target =
                         breakup, args = ())
        matrix_thread6.start()
            
def stopCount():
    global stopTimer
    stopTimer = True

def stopAnimations():    
    global animateStop
    animateStop = True
    
def initI2C():
    global matrixInstance
    stopCount()
    stopAnimations()
    matrixInstance = []
    for i in range(0,4):
        try :
            ins = Matrix11x7(i2c_address = i + 0x74)
        except :
            print("nothing", i, "at address",
                   hex(i+ 0x74))
            ins = 0
        matrixInstance.append(ins)
    
def spinC(device, speed, stopSpeed, retard):# clockwise 
    pattern = 0
    while speed < stopSpeed:
        draw(pattern, device)
        pattern += 1
        if pattern > 3:
            pattern = 0
            speed += retard          
        time.sleep(speed)

def spinA(device, speed, stopSpeed, retard):
    pattern = 3
    while speed <= stopSpeed:
        draw(pattern,device)
        pattern -= 1
        if pattern < 0:
            pattern = 3
            speed += retard
        time.sleep(speed)
    draw(3,device)

def timer(device, speed):  # show time
    global stopTimer
    stopTimer = False
    matrixInstance[device].set_brightness(0.5)
    matrixInstance[device].clear()
    startT = time.time()
    while not stopTimer :
         display = str( (int(time.time()-startT) * 10)
                         // 10 )
         matrixInstance[device].write_string(display,
                        x=0, y=0, font=font5x7)
         if len(display) == 1:
             matrixInstance[device].scroll(-3)
             if display == "1":
                 matrixInstance[device].scroll(-1)
         else :        
             if display[0] == "1":
                 matrixInstance[device].scroll(-1)       
         matrixInstance[device].show()
         matrixInstance[device].clear()
         time.sleep(1.0)
         if int(display) > 98 : stopTimer = True
    matrixInstance[device].set_brightness(1.0)
    
def wipeL(device, speed):  # wipe left 
    for x in range(0,12):
        matrixInstance[device].clear()
        for y in range(0,7):
            matrixInstance[device].set_pixel(x,y,0.5)
        matrixInstance[device].show()    
        time.sleep(speed)
        
def wipeR(device, speed):  # wipe right 
    for x in range(11,-1,-1):
        matrixInstance[device].clear()
        for y in range(0,7):
            matrixInstance[device].set_pixel(x,y,0.5)
        matrixInstance[device].show()    
        time.sleep(speed)
    matrixInstance[device].clear()
    matrixInstance[device].show()

def larson():
    global animateStop
    animateStop = False
    REDS = [0] * 56
    SCAN = [1, 2, 4, 8, 16, 32, 64, 128, 255]
    REDS[28 - len(SCAN):28
            + len(SCAN)] = SCAN + SCAN[::-1]
    start_time = time.time()
    while not animateStop:
        delta = (time.time() - start_time) * 56
        offset = int(abs((delta % len(REDS)) - 28))
        for i in range(0, 28):
            ledshim.set_pixel(i, REDS[offset + i],
                              0, 0)
        ledshim.show()
        time.sleep(0.05)
        
def solid():
    global animateStop
    animateStop = False ; step = 0    
    while not animateStop :
        if step == 0 : ledshim.set_all(128, 0, 0)            
        if step == 1 : ledshim.set_all(0, 128, 0)            
        if step == 2 : ledshim.set_all(0, 0, 128)            
        step += 1 ; step %= 3        
        ledshim.show() ; time.sleep(0.5)
        
def pulse():
    global animateStop
    animateStop = False
    while not animateStop:
        for z in list(range(1, 10)[::-1]) + list(
                      range(1, 10)):
            fwhm = 15.0 / z
            gauss = make_gaussian(fwhm)
            y = 4 ; start = time.time()            
            for x in range(ledshim.NUM_PIXELS):
                h = 0.5 ; s = 1.0 ; v = gauss[x, y]                
                rgb = colorsys.hsv_to_rgb(h, s, v)
                r, g, b = [int(255.0 * i) for i in rgb]
                ledshim.set_pixel(x, r, g, b)
            ledshim.show()
            end = time.time()
            t = end - start
            if t < 0.04:
                time.sleep(0.04 - t)

def breakup():
    stopAnimations() # stop animation thread
    showTime = 2.0 # show for 2 seconds
    startTime = time.time()
    while time.time() - startTime < showTime :
        pixels = random.sample(
               range(ledshim.NUM_PIXELS),
               random.randint(1, 5))
        for i in range(ledshim.NUM_PIXELS):
            if i in pixels:
                ledshim.set_pixel(i, 255, 150, 0)
            else:
                ledshim.set_pixel(i, 0, 0, 0)
        ledshim.show() ; time.sleep(0.05)        
    ledshim.clear() # turn off after showTime
    ledshim.show()
      
def draw(n,ins):
    matrixInstance[ins].clear()
    if n == 2:
       y=0
       for x in range(2, 9):
           matrixInstance[ins].set_pixel(x, y, 0.5)
           y +=1
    elif n == 3:
       x=5   
       for y in range(0,7):
           matrixInstance[ins].set_pixel(x, y, 0.5)
    elif n == 0:
       y=6
       for x in range(2, 9):
           matrixInstance[ins].set_pixel(x, y, 0.5)
           y-=1
    elif n == 1:
        y=3
        for x in range(1, 10):
            matrixInstance[ins].set_pixel(x, y, 0.5)                 
    matrixInstance[ins].show()

def make_gaussian(fwhm):
    x = np.arange(0, ledshim.NUM_PIXELS, 1, float)
    y = x[:, np.newaxis]
    x0, y0 = 3.5, (ledshim.NUM_PIXELS / 2) - 0.5
    fwhm = fwhm
    gauss = np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / fwhm ** 2)
    return gauss

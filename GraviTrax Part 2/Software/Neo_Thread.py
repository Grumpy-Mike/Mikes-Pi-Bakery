#!/usr/bin/env python
# Neopixel patterns from a thread
# By Mike Cook November 2019

import threading
import time
import board
import neopixel
import RPi.GPIO as io

def startWs2812Thread(number):
    if number == 0:
      # Thread  Leds Dely Dir    front     back    wipe
      ws2812_thread0 = threading.Thread(target = push, 
            args = (number, 12, 0.5, True,
                   (30, 0, 0), (0, 30, 0), True))
      ws2812_thread0.start()
    elif number == 1:
      ws2812_thread1 = threading.Thread(target = push,
            args = (number, 12, 0.5, True,
                   (30, 0, 0), (0, 30, 0), True))
      ws2812_thread1.start()
    elif number == 2:
      ws2812_thread2 = threading.Thread(target = push,
            args = (number, 12, 0.5, False,
                   (30, 0, 0), (0, 30, 0), True))
      ws2812_thread2.start()
    elif number == 3:
      ws2812_thread3 = threading.Thread(target = push,
            args = (number,12,0.2, False,
                   (30, 0, 0), (0, 30, 0),True))
      ws2812_thread3.start()
    elif number == 4:
      ws2812_thread4 = threading.Thread(target = seq,
            args = (number,3, 0.06, False,
                   (0, 0, 30), (20, 20, 20), False))
      ws2812_thread4.start()
    elif number == 5:   
      ws2812_thread5 = threading.Thread(target = flash,
            args = (number,4,0.12, False,
                   (0, 30, 30), (30, 0, 0), False))
      ws2812_thread5.start()
    elif number == 6:
      ws2812_thread6 = threading.Thread(target = run,
            args = (number, 14, 0.13, False, (30, 0, 0),
            (0, 0, 0), False))
      ws2812_thread6.start()
    elif number == 7:
      ws2812_thread7 = threading.Thread(target=push,
            args = (number, 20, 0.03, False,
            (30, 30, 0), (0, 0, 30), False))
      ws2812_thread7.start()
              
def run(add, numLed, delay, direction, frontCol, backCol, wipe):
    strip[add].fill(backCol)
    for i in range(0,numLed):
        j = i
        if direction : j = numLed - i
        strip[add][j] = frontCol
        setAdd(add) ; strip[add].show()                                            
        time.sleep(delay)
        if not wipe : strip[add].fill(backCol)
    setAdd(add) ; strip[add].show()
    time.sleep(delay)
    strip[add].fill((0, 0, 0)) # clear out
    setAdd(add) ; strip[add].show()
    
def flash(add, repeats, delay, direction, frontCol, backCol, wipe):
    strip[add].fill(backCol)
    for i in range(0,repeats):
        strip[add].fill(frontCol)
        setAdd(add) ; strip[add].show()                                            
        time.sleep(delay)
        strip[add].fill(backCol)
        setAdd(add) ; strip[add].show()                                            
        time.sleep(delay)        
    if not wipe :
        strip[add].fill((0, 0, 0))
        setAdd(add) ; strip[add].show()
    
def push(add, numLed, delay, direction, frontCol, backCol, wipe):
    strip[add].fill(backCol)
    k = numLed // 2
    for i in range(numLed // 2, numLed):
        j = i ; k -= 1
        strip[add][j] = frontCol
        strip[add][k] = frontCol
        setAdd(add) ; strip[add].show()                                            
        time.sleep(delay)
        if not wipe :
           strip[add][j] = backCol
           strip[add][k] = backCol
    setAdd(add) ; strip[add].show()

def seq(add, repeats, delay, direction, frontCol, backCol, wipe):
    seqToLight = ( [3], [2, 4], [1, 5], [0, 6],
            [11, 7], [10, 8], [9], [10, 8], [11, 7],
            [0, 6], [1, 5], [2, 4], [3])
    for j in range(0,repeats):
      strip[add].fill(backCol)
      for i in range(0, len(seqToLight)):
          for k in range(0, len(seqToLight[i])) :
              strip[add][seqToLight[i][k]] = frontCol
          setAdd(add) ; strip[add].show()                                            
          time.sleep(delay)
          if not wipe :
              for k in range(0, len(seqToLight[i])) :
                  strip[add][seqToLight[i][k]] = backCol
      setAdd(add) ; strip[add].show()  
       
def initIO():
    global muxAdd, strip
    io.setwarnings(False)
    io.setmode(io.BCM)
    muxAdd = [11, 9, 10]
    io.setup(muxAdd, io.OUT), # set pins as outputs
    pixel_pin = board.D18
    num_pixels = 20 # maximum LEDs in biggest strip
    ORDER = [neopixel.GRB] * 8 
    strip = []
    for i in range(0,8):
        pixels = neopixel.NeoPixel(
               pixel_pin, num_pixels, brightness=0.1,
               auto_write=False, pixel_order=ORDER[i])                           
        strip.append(pixels)
    
def setAdd(add):
    for i in range(0, 3) : io.output(muxAdd[i],0) 
    if add & 1 : io.output(muxAdd[0],1)  
    if add & 2 : io.output(muxAdd[1],1)
    if add & 4 : io.output(muxAdd[2],1)

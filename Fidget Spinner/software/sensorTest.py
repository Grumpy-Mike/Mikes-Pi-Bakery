#!/usr/bin/env python3
# Figet Spinner sensor test
# By Mike Cook - July 2017

import time, os
import RPi.GPIO as io
io.setwarnings(False)


io.setmode(io.BCM)
io.setup(4, io.IN, pull_up_down=io.PUD_UP)
io.setup(23, io.OUT) # feedback

count = 0

def pulse(channel):
    global count
    count += 1
    io.output(23,not(io.input(23)))

def main():
    global count
    io.add_event_detect(4, io.FALLING, callback = pulse)
    while 1:
      interval = time.time()
      lastCount=count
      while time.time() - interval <1.0:
          pass
      print((count-lastCount)*10,"RPM")
    
# Main program logic:
if __name__ == '__main__':
   try:  
      main()
   finally:
      io.cleanup()

#!/usr/bin/env python3
# coding=utf-8
# MIDI Duet - sends off a short random note in key of C every 3 seconds
# Set up your DAW so you can play along and improvise against them
# By Mike Cook August 2020

import serial
import time
import random
                       
comPort = serial.Serial(port = "/dev/serial0", baudrate = 250000,
                        parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)

baseNote = [0, 2, 4, 5, 7, 9, 11, 12] # key of C major

def main():
    print("Random note to play along with")
    limitTime = 4.0
    startTime = time.time() - limitTime
    while 1:   
        
        if time.time() - startTime > limitTime :
           startTime = time.time() 
           note = baseNote[random.randint(0,7)] + (random.randint(3,6) * 12)
           #print(note)
           eb = bytearray([0x9, 0x90, note, random.randint(64,125)])
           comPort.write(eb) # send note on
           time.sleep(0.1) # small delay
           eb = bytearray([0x8, 0x80, note, 0])
           comPort.write(eb) # send note off
    
if __name__ == '__main__':
    main()

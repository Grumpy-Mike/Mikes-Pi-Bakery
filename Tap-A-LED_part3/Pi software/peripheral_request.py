#!/usr/bin/env python3
# coding=utf-8
# Using the Arduino analogue and digital I/O
# By Mike Cook September 2020

import serial
import os
import time
                       
comPort = serial.Serial(port = "/dev/serial0", baudrate = 250000,
                        parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)
# values in frame
# 0 = event type | 1 = event type with channel
# 2 = control number (0-119) | 3 = control value
frame = [0, 0, 0, 0]

def main():
    init()
    print("Send request for peripheral data from Arduino")
    while 1:
        # enable one or more of the following lines
        # parameters pin number , sleep after operation
        #toggleDigital(7, 0.5)
        readAnalog(0, 1.5)
        #readDigital(9, 1.5)
        #analogSweep(9, 0.01)
    
def toggleDigital(pinNumber, speed):
    global count
    count = (count +1) & 1
    sendIOrequest(digitalWrite, pinNumber, count )
    readMIDI()
    time.sleep(speed)

def readAnalog(pinNumber, speed):
    sendIOrequest(analogRead, pinNumber, 0)
    readMIDI()
    processIOrequest(analogRead, pinNumber)
    time.sleep(speed)
    
def readDigital(pinNumber, speed):
    sendIOrequest(digitalRead, pinNumber, 0)
    readMIDI()
    processIOrequest(digitalRead, pinNumber)
    time.sleep(speed)

def analogSweep(pinNumber, speed):
    global count
    count = (count + 1) & 0xFF
    sendIOrequest(analogWrite, pinNumber, count)
    readMIDI()
    processIOrequest(analogWrite, pinNumber)
    time.sleep(speed)
    
def sendIOrequest(pType, num, level):
    global frame
    frame[0] = 0xF9 # request periphal
    frame[1] = pType | num # request read of pin "num"
    frame[2] = level # digital or PWM 
    eb = bytearray([frame[0], frame[1], frame[2], frame[3]])
    comPort.write(eb) # send to Arduino

def processIOrequest(pType, num):
    print(frame) # debug
    if frame[0] == 0xF9 : # got an answer to peripheral request
        if frame[3] == 0xFF : print("Not a valid Pin number") ; return
    if pType == digitalRead :
        if frame[2] & 1 : print("Pin",num,"is HIGH")
        else : print("Pin",num,"is LOW")
    if pType == analogRead :
        print("Quick value for","A" + str(num), "is",frame[2])
        print("Full value for","A" + str(num), "is",(frame[2] << 3) | (frame[3] & 0x7))
    
def readMIDI():
    global frame
    frame = [0, 0, 0, 0] 
    string = ""
    i = 0
    done = False
    timeout = time.time()
    while time.time() - timeout < 0.01 and not done:
        if comPort.inWaiting() > 0:
            timeout = time.time()
            ch = comPort.read(1)
            if ch == b'\n' :
                if len(string) > 3:
                    frame = [int(s) for s in string.split() if s.isdigit()]
                done = True
            elif ch != b'\r' :
                string = string + ch.decode()       
def init():
    global digitalWrite, digitalRead, analogRead, analogWrite, count
    digitalWrite = 0x80 ; digitalRead = 0x0
    analogRead = 0x40 ; analogWrite = 0xC0
    count = 0

if __name__ == '__main__':
    main()

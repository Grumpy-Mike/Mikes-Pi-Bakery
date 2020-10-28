#!/usr/bin/env python3
# coding=utf-8
# GPIO port Serial monitor talking MIDI
# echos back any MIDI sent to the Arduino
# By Mike Cook August 2020

import serial
import time
                       
comPort = serial.Serial(port = "/dev/serial0", baudrate = 250000,
                        parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)
# 0 = event type | 1 = event type with channel
# 2 = control number (0-119) | 3 = control value
frame = [0, 0, 0, 0]

def main():
    print("Echo back MIDI data sent here")
    while 1:   
        readMIDI()
        if frame[0] != 0 :
           #print(frame) # lantcy 0.018 when enbled otherwise lantcy 0.002 seconds
           eb = bytearray([frame[0], frame[1], frame[2], frame[3]])
           comPort.write(eb) # echo back

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

    
if __name__ == '__main__':
    main()

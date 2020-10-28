#!/usr/bin/env python3
# x-y PAD by Mike Cook September 2020
# sends out a X-Y of touch location on
# CC 0x0E (MSB) and 0x2E (LSB) for X
# CC 0x0F (MSB) and 0x2F (LSB) for Y
# using external CalTap class

from caltap import CalTap
import serial
import time

comPort = serial.Serial(port = "/dev/serial0", baudrate = 250000,
                        parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)

def main():
    global pos
    print("Touch anywhere to send MIDI control message")
    init()
    setUpMode() # comment out if your daw is already set up.
    while 1:
        processPos(tap.getRaw())
        if pos[3] : # if a valid reading           
            sendMIDI(0xB, 0xB0, 0x0E, pos[0])
            sendMIDI(0xB, 0xB0, 0x0F, pos[1])

# Applications like Ableton require you to click on the parameter
# you want to control and then send just that control
# this lets you send first just the X control and then the Y control
# then it returns to the main loop to send both
def setUpMode():
    global pos
    print("Set up mode - sending just control message 0xE")
    print("Tap in lower left to advance or exit")
    step = 0
    while step == 0:
        processPos(tap.getRaw())
        if pos[3] : # if a valid reading           
            sendMIDI(0xB, 0xB0, 0x0E, pos[0])
            if pos[0] == 0 and pos[1] == 0 :
                step = 1
    print("Now sending just control message 0xF")
    time.sleep(1.5)
    pos[3] = False
    while step == 1:
        processPos(tap.rawRead())
        if pos[3] : # if a valid reading           
            sendMIDI(0xB, 0xB0, 0x0F, pos[1])
            if pos[0] == 0 and pos[1] == 0 :
                step = 0
    print("Now sending both controllers")        
        

    
def sendMIDI(command, fullCommand, pram, cValue):
    #print(command, fullCommand, pram, cValue)
    cValue &= 0x7F
    sf = bytearray([command, fullCommand, pram, cValue])
    comPort.write(sf) # send frame

def processPos(raw):
    global pos
    #print("x",raw[0], " y", raw[1], " z", raw[2]) # debug
    pos[0] = int((raw[0] - minExtent[0]) / scaleX)
    pos[1] = int((raw[1] - minExtent[1]) / scaleY)
    pos[2] = raw[2]
    pos[3] = raw[3]
    
def init():
    global tap, scaleX, scaleY, pos, minExtent  
    tap = CalTap()
    maxExtent = tap.getRawMax()
    minExtent = tap.getRawMin()
    scaleX = (maxExtent[0] - minExtent[0]) / 127
    scaleY = (maxExtent[1] - minExtent[1]) / 127
    pos = [0, 0, 0, False]

    
if __name__ == '__main__':
    main()

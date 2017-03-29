#!/usr/bin/env python
# DJ Hero interface test
# Mike Cook Feb 2017
from smbus import SMBus
import RPi.GPIO as rpi
import time as time

def main():
    init()
    print "DJ Hero Test"
    while 1:
         block = readDJ()
         euphoria = buttonFix(block[5] & 0x10)
         print "Euphoria", euphoria,
         slider = (block[2] >> 1) & 0x0f
         print "Slider", slider,
         joyX = block[0] & 0x3F # 0 to 63
         joyY = block[1] & 0x3F # 0 to 63
         print" Joy X =",joyX, " Joy Y =",joyY,
         buttonPlus = buttonFix(block[4] & 0x04)
         buttonMinus = buttonFix(block[4] & 0x10)
         print"B+",buttonPlus," B-",buttonMinus,
         butRed = buttonFix(block[4] & 0x02)
         butGreen = buttonFix(block[5] & 0x20)
         butBlue = buttonFix(block[5] & 0x04)
         print"RGB",butRed,butGreen,butBlue,
         effectsDial = (block[3] >> 5) | ((block[2] & 0x60) >> 2) # 0 to 31
         print"Effects",effectsDial,
         table = (block[2] >> 7) | ((block[1] & 0xC0)>> 5) | ((block[0] &0xC0) >> 3)
         if block[2] & 0x01 == 0x01: # the sign bit
             table = -(table ^ 0x1F)-1
         print"Turntable",table
         time.sleep(0.1)

def buttonFix(value):
    pressed = 1
    if(value != 0):
        pressed = 0
    return pressed

def init():
    global bus
    if rpi.RPI_REVISION == 1:
      i2c_bus = 0
    else :
      i2c_bus = 1
    bus = SMBus(i2c_bus)
    bus.write_byte_data(0x52,0xF0,0x55)

def readDJ(): # Currently an issue with the I2C drivers or something that throws up an occasional error - this is the sticking plaster
    try:
       bus.write_byte(0x52,0)
    except:
       print"bus restart" 
       init()
       bus.write_byte(0x52,0)
    dj = [(bus.read_byte(0x52)) for i in range(6)]
    return dj

# Main program logic:
if __name__ == '__main__':    
    main()
    

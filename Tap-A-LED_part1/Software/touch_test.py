#!/usr/bin/env python3
# simple test to see if touch screen is working
# by Mike Cook August 2020

from smbus import SMBus
import time
  

addr = 0x41
SYS_CTRL1 = 0x03 ; SYS_CTRL1_RESET = 0x02 
SYS_CTRL2 = 0x04
TSC_CTRL = 0x40 ; TSC_CTRL_XYZ  = 0x00 ; TSC_CTRL_EN  = 0x01 
ADC_CTRL1 = 0x20 ; ADC_CTRL1_10BIT = 0x00 
ADC_CTRL2 = 0x21 ; ADC_CTRL2_6_5MHZ = 0x02 
TSC_CFG = 0x41 ; TSC_CFG_4SAMPLE = 0x80 
TSC_CFG_DELAY_1MS = 0x20 
TSC_CFG_SETTLE_5MS = 0x04 
TSC_FRACTION_Z = 0x56
FIFO_TH = 0x4A 
#
def main():
    global bus
    bus = SMBus(1)        
    val = rxI2Cword(0)
    if val != 0x811: print("STMPE610 not found chip ID =", hex(val))
    #init610
    sendI2C( SYS_CTRL1, SYS_CTRL1_RESET)
    time.sleep(0.01)
    sendI2C(SYS_CTRL2, 0x0) # // turn on clocks
    sendI2C( TSC_CTRL, TSC_CTRL_XYZ | TSC_CTRL_EN) # XYZ and enable
    sendI2C( ADC_CTRL1, 0x49) # 80 clock cycles 12 bit A/D internal ref
    sendI2C( ADC_CTRL2, 0x01) # ADC clock 3.5MHz        
    sendI2C( TSC_CFG, TSC_CFG_4SAMPLE |
                                    TSC_CFG_DELAY_1MS |
                                    TSC_CFG_SETTLE_5MS)
    sendI2C( TSC_FRACTION_Z, 0x6)
    sendI2C( FIFO_TH, 2)

    print("make my day and touch the screen")
    while 1:
        touch = touched()
        if touch :
            print("yes")
            while touched() : pass
            print("again")
           
def sendI2C(reg, val):
    bus.write_byte_data(addr, reg, val)

def rxI2C(reg):
    r = bus.read_i2c_block_data(addr, reg, 1)
    return r[0]

def rxI2Cword(reg):
    r = bus.read_i2c_block_data(addr, reg, 2)
    val = (r[0]<<8) | r[1]
    return val

def touched():
    reg = rxI2C(TSC_CTRL)
    return reg & 0x80


if __name__ == '__main__':    
    main()       

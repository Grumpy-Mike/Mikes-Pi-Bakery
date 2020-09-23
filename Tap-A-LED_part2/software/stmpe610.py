#!/usr/bin/env python3
# class to setup the STMPE610 by Mike Cook August 2020

from smbus import SMBus
import time
  
class Stmpe610:
    addr = 0x41
    SYS_CTRL1 = 0x03 ; SYS_CTRL1_RESET = 0x02 
    SYS_CTRL2 = 0x04
    TSC_CTRL = 0x40 ; TSC_CTRL_XYZ  = 0x00 ; TSC_CTRL_EN  = 0x01 
    INT_EN = 0x01 ; INT_EN_TOUCHDET = 0x01 
    ADC_CTRL1 = 0x20 ; ADC_CTRL1_10BIT = 0x00 
    ADC_CTRL2 = 0x21 ; ADC_CTRL2_6_5MHZ = 0x02 
    TSC_CFG = 0x41 ; TSC_CFG_4SAMPLE = 0x80 
    TSC_CFG_DELAY_1MS = 0x20 
    TSC_CFG_SETTLE_5MS = 0x04 
    TSC_FRACTION_Z = 0x56 ; FIFO_CTRL_STA = 0x4B
    FIFO_TH = 0x4A ; FIFO_STA_EMPTY = 0x20
    FIFO_STA = 0x4B ; FIFO_STA_RESET = 0x01
    FIFO_SIZE = 0x4C ; INT_STA = 0x0B 
    TSC_I_DRIVE = 0x58 ; TSC_I_DRIVE_50MA = 0x01     
    INT_CTRL = 0x09 ; INT_CTRL_POL_HIGH  = 0x04 ; INT_CTRL_ENABLE = 0x01
    xPos = 0 ; yPos = 0 ; zPos = 0 ; interval = 0.04

    def __init__(self):
        self.bus = SMBus(1)        
        val = self.rxI2Cword(0)
        if val != 0x811: print("STMPE610 not found chip ID =", hex(val))
        #init610
        self.sendI2C( self.SYS_CTRL1, self.SYS_CTRL1_RESET)
        time.sleep(0.01)
        self.sendI2C( self.SYS_CTRL2, 0x0) # // turn on clocks
        self.sendI2C( self.TSC_CTRL, self.TSC_CTRL_XYZ | self.TSC_CTRL_EN) # XYZ and enable
        self.sendI2C( self.INT_EN, self.INT_EN_TOUCHDET)
        self.sendI2C( self.ADC_CTRL1, 0x49) # 80 clock cycles 12 bit A/D internal ref
        self.sendI2C( self.ADC_CTRL2, 0x01) # ADC clock 3.5MHz        
        self.sendI2C( self.TSC_CFG, self.TSC_CFG_4SAMPLE |
                                        self.TSC_CFG_DELAY_1MS |
                                        self.TSC_CFG_SETTLE_5MS)
        self.sendI2C( self.TSC_FRACTION_Z, 0x6)
        self.sendI2C( self.FIFO_TH, 1)
        self.sendI2C( self.FIFO_STA, self.FIFO_STA_RESET)
        self.sendI2C( self.FIFO_STA, 0) # // unreset
        self.sendI2C( self.TSC_I_DRIVE, self.TSC_I_DRIVE_50MA)
        self.sendI2C( self.INT_STA, 0xFF) # // reset all ints
        self.sendI2C( self.INT_CTRL, self.INT_CTRL_POL_HIGH | self.INT_CTRL_ENABLE)
        
    def readPos(self):
        timeout = False
        self.sendI2C( self.FIFO_CTRL_STA, 1)
        self.sendI2C( self.FIFO_CTRL_STA, 0)
        start = time.time()
        while self.bufferSize() == 0 and timeout == False:  # wait till it fills up a bit
            if time.time() - start > self.interval : timeout = True 
        if not timeout :
            r = self.bus.read_i2c_block_data(self.addr,0xD7, 4)
            self.xPos = 4096 - ((r[0] << 4) | (r[1] >> 4))
            self.yPos = ((r[1] & 0x0F) << 8) | r[2]
            self.zPos = r[3]
        return (self.xPos, self.yPos, self.zPos, not timeout)
               
    def sendI2C(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def rxI2C(self, reg):
        r = self.bus.read_i2c_block_data(self.addr, reg, 1)
        return r[0]

    def rxI2Cword(self, reg):
        r = self.bus.read_i2c_block_data(self.addr, reg, 2)
        val = (r[0]<<8) | r[1]
        return val

    def touched(self):
        reg = self.rxI2C(self.TSC_CTRL)
        return reg & 0x80

    def bufferEmpty(self):
        flags = self.rxI2C(self.FIFO_STA) 
        return flags & self.FIFO_STA_EMPTY

    def bufferSize(self):
        return self.rxI2C(self.FIFO_SIZE)
        

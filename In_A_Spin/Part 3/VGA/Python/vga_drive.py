#!/usr/bin/env python3
# Class for driving Propeller VDU
# By Mike Cook Jan 2019

import serial

class Vga_drive():
    
    def __init__(self, chrX,chrY): # initialisation
       self.spinProcessor = serial.Serial("/dev/ttyUSB0",115200, timeout = 1)
       self.spinProcessor.flushInput()
       self.spinProcessor.flushOutput()
       self.xWidth = chrX -1 # make first line zero
       self.yWidth = chrY -1
       
    def sendString(self, send): # send a string to the VDU
       buf = 27 # maximum string size for Pi buffers
       self.spinProcessor.flushInput()
       ln = len(send)
       i = 0 
       while i < ln:
          self.spinProcessor.write(send[i:i+buf].encode()+ b'\x0D')
          self.waitAck()
          i += buf
          
    def sendStringLn(self, send): # send a string no CR
      self.sendString(send)
      self.sendNl()
      
    def sendNl(self): # send a new line command
      self.spinProcessor.flushInput()
      self.spinProcessor.write(b'\x0E\x0D')  # send new line 
      self.waitAck()
      
    def setX(self,pos): # set X cursor
      pos += 14 # can't send zero or 13 so add 14
      if pos < 14 or pos > self.xWidth + 14: # outside limits
        print("ERROR ",pos,"IS OUT OF RANGE")
        return
      self.spinProcessor.flushInput()  
      s = b'\x0A' + str(chr(pos)).encode() + b'\x0D'
      self.spinProcessor.write(s)
      self.waitAck()
      
    def setY(self,pos): # set Y cursor
      pos += 14 # can't send zero or 13 so add 14
      if pos < 14 or pos > self.yWidth + 14: # outside limits
        print("ERROR ",pos,"IS OUT OF RANGE")
        return
      self.spinProcessor.flushInput()  
      s = b'\x0B' + str(chr(pos)).encode() + b'\x0D'
      self.spinProcessor.write(s)
      self.waitAck()
      
    def erase(self,line,start,length): # erase "line" from "start" for "length"
       if start + length > self.xWidth:
          length = self.xWidth - start
       s = ""
       for i in range(0,length):
         s +=" "
       if line > -1:  # set line to -1 to use current line
          self.setY(line)  
       self.setX(start)
       self.sendString(s)
       self.setX(start)
       if line > -1:  
          self.setY(line)  
      
    def waitAck(self): #wait for acknowledgement
      ack = self.spinProcessor.read()
      
    # set colour for current line  
    def setColour(self,rf,gf,bf,rb,gb,bb): # r,g,b foreground & r,g,b background
      colF = ((rf & 0x3) << 4) | ((gf & 0x3) << 2) | (bf & 0x3) | 0x40
      colB = ((rb & 0x3) << 4) | ((gb & 0x3) << 2) | (bb & 0x3) | 0x40
      s = b'\x0C' + str(chr(colF)).encode() +str(chr(colB)).encode()+ b'\x0D'
      self.spinProcessor.write(s)
      self.waitAck()
      
    def cls(self): # clear screen and set to home
      self.spinProcessor.write(b'\x01\x0D') # clear screen  
      self.waitAck()

    def home(self): # go to top left
      self.spinProcessor.write(b'\x02\x0D') # home
      self.waitAck()

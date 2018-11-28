#!/usr/bin/env python3
# Class for driving Max7219 Matrix
# Using pigpio for I/O & virtual push indicator
# By Mike Cook Oct 2018

import time
import pigpio

class Max7219bang():
    
    def __init__(self,data,clock,load,bright):
       self.da = data
       self.ck = clock
       self.ld = load
       if bright >-1 and bright < 16:
          self.br = bright
       else :
          self.br = 8 
       # copy of the Max chip's registers
       self.registers = [0]*9
       #0=off,1=red,2=green,4=blue
       self.ledsState  = [0]*16 # all off
       self.ledCol     = [0,4,2,6,1,5,3,7] # LED colour numbers RGB
       # colour offset per switch
       self.colOff     = [0,0,0,0, 4,4,4,4, 0,0,0,0, 4,4,4,4] 
       # switch number to register address
       self.address    = [1,3,5,7, 1,3,5,7, 2,4,6,8, 2,4,6,8]
       self.buttonPins = [12,25,24,23,6,13,19,26,16,20,21,4,17,27,22,5] # rows
       self.switches = [False] * 16
       
       self.pi = pigpio.pi()
       if not self.pi.connected:
          print("Pi not connected")
       self.pi.set_mode(self.ck,pigpio.OUTPUT)
       self.pi.set_mode(self.da,pigpio.OUTPUT)
       self.pi.set_mode(self.ld,pigpio.OUTPUT)
       for i in self.buttonPins:
          self.pi.set_mode(i,pigpio.INPUT)
          self.pi.set_pull_up_down(i, pigpio.PUD_DOWN)
       self.pi.write(self.ck, 0)
       self.pi.write(self.da, 0)
       self.pi.write(self.ld, 1)
              
       self.cb = [None] *32
       for i in range (0, len(self.buttonPins)):
         self.pi.set_glitch_filter(self.buttonPins[i], 200) # microseconds filter
         self.cb[i] = self.pi.callback(self.buttonPins[i], pigpio.EITHER_EDGE, self.cbf)
       self.sendMax(0x9,0)    # no decode
       self.sendMax(0xB,7)    # scan all digits
       self.sendMax(0xA,self.br) # intensity
       self.sendMax(0xC,1)    # take out of shutdown mode
       self.clrLEDs()          # start with all off
       for i in range(0,16): # clear out any glitches
         self.switches[i] = False  
       
    def setBrightness(self,brightness):
        if brightness > 15:
           brightness = 15
        if brightness < 0:
           brightness = 0          
        self.br = brightness
        self.sendMax(0xA,self.br)
        
    def clrLEDs(self):
        for add in range(1,9): # all display registers
          self.registers[add] = 0  
          self.sendMax(add,0)
        for i in range(0,16): # all display leds
            self.ledsState[i] = 0
            
    def getLed(self,switch):
        return self.ledCol[self.ledsState[switch]]
    
    def setRed(self,switch):
        self.setLed(switch,1)
    def setGreen(self,switch):
        self.setLed(switch,2)
    def setBlue(self,switch):
        self.setLed(switch,4)

    def addRed(self,switch):
        col = self.getLed(switch) | 1 # add red
        self.setLed(switch,col)
    def addGreen(self,switch):
        col = self.getLed(switch) | 2 # add green
        self.setLed(switch,col)
    def addBlue(self,switch):        
        col = self.getLed(switch) | 4 # add blue
        self.setLed(switch,col)

    
    def setLed(self,switch,col): # set what LEDs are on for switch
        if switch > 15 or switch < 0 :
            switch = 0          #default for switch out of range
        col &= 0x7              # restrict to 0 to 7
        col = self.ledCol[col]  #convert to register data
        self.ledsState[switch] = col        
        reg = self.address[switch]
        if self.colOff[switch] == 0 :
           self.registers[reg] = (self.ledsState[switch] << 4) | (self.ledsState[switch+4])
        else:   
           self.registers[reg] = (self.ledsState[switch-4] << 4) | (self.ledsState[switch])        
        self.sendMax(self.address[switch],self.registers[reg])

    def cbf(self, gpio, level, tick): # call back function       
       place = [i for i,x in enumerate(self.buttonPins) if x == gpio]
       #print("GPIO",gpio,"switch",place[0],"steady level",level)
       self.switches[place[0]] = True # indicate switch has changed
       
    def getSwitch(self):
        pressed = -1 ; i = 0
        while pressed == -1 and i<16: 
           if self.switches[i]: # key press found
              self.switches[i] = False
              pressed = i
           i+=1  
        return pressed
    
    def sendMax(self,add,data): # send a byte to mux chip
        package = (add << 8) | data # join into one bit pattern
        self.pi.write(self.ld, 0) # lower load
        for i in range(15,-1,-1): # from 15 to 0
           self.pi.write(self.da, 1 & (package >> i)) # send MSB first
           self.pi.write(self.ck, 1) # toggel clock
           self.pi.write(self.ck, 0)
        self.pi.write(self.ld, 1) # latch value

    def cleanUp(self):
       self.sendMax(0xC,0)     # put into shutdown mode 
       for i in range (0, 16): # remove callback vectors
          self.cb[i].cancel()
          self.pi.set_glitch_filter(self.buttonPins[i], 0)
       self.pi.stop() # stop pigpio

          

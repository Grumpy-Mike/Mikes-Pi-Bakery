#!/usr/bin/env python3
# Matrix test - By Mike Cook Sep 2018
 
import time
import RPi.GPIO as io

dataPin = 14 ; clockPin = 15 ; loadPin = 18 ; buttons = 0 ; oldButtons = 0
buttonPins = [12,25,24,23,6,13,19,26,16,20,21,4,17,27,22,5] # rows
ledsState  = [ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #0=off,1=red,2=green,3=blue
ledCol     = [0,64,32,16,0,4,2,1] # LED colour number
register   = [0,0,0,0,0,0,0,0,0] # copy of the Max chip's registers
address    = [1,3,5,7, 1,3,5,7, 2,4,6,8, 2,4,6,8] # switch number to register address
colOff     = [0,0,0,0, 4,4,4,4, 0,0,0,0, 4,4,4,4] # colour offset per switch

def main():
    global register
    print("Matrix test")
    init_io()
    init_max7219()
    time.sleep(0.04)
    clrLED()
    readButtons()
    for switch in range(0,16):
        setLed(switch,ledsState[switch])
    while True:
      for switch in range (0,16): 
        readButtons()
        if buttonsChanged :
          print("Bit pattern", fullBin(buttons), " Number =",buttons,)
          for switch in range(0,16):
            if buttons & (1 << switch) != oldButtons & (1 << switch) :
              print("changing switch number",switch)
              setLed(switch,ledsState[switch]) 
          time.sleep(0.2)
        
def setLed(switch,col): # increment LED state & display
    global register    
    reg = address[switch]
    ledsState[switch] += 1
    if ledsState[switch] >3 :
      ledsState[switch] = 0
    if colOff[switch] == 0 :
        register[reg] &= 0x0F # clear bottom bits
    else:   
        register[reg] &= 0xF0 # clear top bits
    register[reg] |= ledCol[colOff[switch]+ledsState[switch]]
    sendMax(address[switch],register[reg])
    
def fullBin(num): # to show all leading zeros
    binary = "" 
    for i in range(15,-1,-1):
      if num & (1 << i):
         binary = binary +"1"
      else:
         binary = binary +"0"
    return binary      
    
def init_io():
    io.setmode(io.BCM)
    io.setwarnings(False)
    for i in range (0, len(buttonPins)):
       io.setup(buttonPins[i], io.IN, pull_up_down=io.PUD_UP)
    io.setup(dataPin, io.OUT) # data out
    io.output(dataPin, 0)
    io.setup(clockPin, io.OUT) # clock
    io.output(clockPin, 0) 
    io.setup(loadPin, io.OUT) # not load
    io.output(loadPin, 1)

def readButtons():
    global buttons, buttonsChanged, oldButtons
    buttonsChanged = False
    oldButtons = buttons
    newBut = 0
    for i in range (0, len(buttonPins)):
       edge = io.wait_for_edge(buttonPins[i],io.FALLING,1,2)
       if edge == None:
          newBut &= 0xFFFF ^ (1<< i) # clear bit in variable          
       else:
          newBut |= 1<< i # set bit in variable
    if newBut != buttons : # we have a changed from last time
        buttons = newBut
        buttonsChanged = True
          
def clrLED():
    for add in range(1,9): # all display registers
      sendMax(add,0)
              
def init_max7219():
    sendMax(0x9,0)    # no decode
    sendMax(0xB,7)    # scan all digits
    sendMax(0xA,0x15) # maximum intensity
    sendMax(0xC,1)    # take out of shutdown mode
    
def sendMax(add,data): # send a byte to mux chip
    package = add << 8 | data # join into one bit pattern
    io.output(loadPin, 0) # lower load
    for i in range(15,-1,-1): # from 15 to 0
       io.output(dataPin, 1 & (package >> i)) # send MSB first
       io.output(clockPin, 1) # toggel clock
       io.output(clockPin, 0) 
    io.output(loadPin, 1) # latch value    
        
# Main program logic:
if __name__ == '__main__':    
    main()

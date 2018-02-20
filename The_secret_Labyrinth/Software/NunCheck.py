#!/usr/bin/python3
# Nunchuck test
from smbus import SMBus
import RPi.GPIO as io
import time

def init():
    global bus
    io.setmode(io.BCM)
    io.setwarnings(False)
    select = [4,17]
    io.setup(select,io.OUT)
    io.output(select,0)
    #time.sleep(0.3)
    print("initilise I2C")
    if io.RPI_REVISION == 1:
      i2c_bus = 0
    else :
      i2c_bus = 1
 
    bus = SMBus(i2c_bus)
    for nun in range(0,2):     
       bus.write_byte_data(0x52,0x40,0x00) # White Nunchuck
       #bus.write_byte_data(0x52,0xF0,0x55) # For Black
       #bus.write_byte_data(0x52,0xFB,0x00) # For Black
       io.output(4,1)
       time.sleep(0.01)
    
def readNck(nunNum): # Occasionally an issue with the I2C drivers or something that throws up an occasional error - this is the sticking plaster
    io.output(4,nunNum)    
    try:
       bus.write_byte(0x52,0)
    except:
       print("bus restart")
       time.sleep(0.1)
       init()
       bus.write_byte(0x52,0)
    time.sleep(0.001) #delay for Nunchuck to respond   
    nCk = [((bus.read_byte(0x52) ^ 0x17) +0x17) for i in range(0,6)]
    return nCk    

init()
print("Read joy stick, press Z key for printout")
while 1:
    for i in range(0,2):
       nun = readNck(i)
       if(nun[5] & 1) == 0:
          print("Nunchuck",i,nun[0], nun[1], nun[2], nun[3], nun[4], nun[5] & 0x3)

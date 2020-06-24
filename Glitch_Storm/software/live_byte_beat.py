#!/usr/bin/env python3
# create ByteBeat music live by Mike Cook
import spidev

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 400000
spi.mode = 0x0
t = 1
print ("Running Byte Beat live")
try :
    while 1:
        v = t * (42 & t >>10)
        t +=1
        spi.writebytes([0x70 | ( (v >> 4) & 0xF), (v & 0xF) << 4])
except :
    spi.close()


#!/usr/bin/env python3
# create glitch music live by Mike Cook
# through a D/A connected to the SIP port
import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)
rate = 300000 # about 7KHz sample rate
spi.max_speed_hz = rate
spi.mode = 0x0
samples = rate * 2 # 80 seconds of sound
a = 5 ; b = 2 ; c = 12 # constants to change sounds
t = 1 ; s = 0 ; s1= 0
print ("Running glitch live")
start = time.time()
for i in range(0, samples):
    v = (t*12&t>>a | t*b&t>>c | t*b&c//(b << 2))-2
    s = 0x70 | ( (v >> 4) & 0xF) 
    s1 = (v & 0xF) << 4
    t +=1
    spi.writebytes([s,s1])
end = time.time()
print((end - start), "seconds of sound")
print(" sample rate ",
      (samples / (end - start)/ 1000),"kHz")
spi.close()


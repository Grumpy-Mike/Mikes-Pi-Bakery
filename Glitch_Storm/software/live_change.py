#!/usr/bin/env python3
# create live glitch music through a D/A connected to the SIP port
# by Mike Cook May 2020
import spidev
import time
import os
import math
from ky040 import Ky040

def main():
    global p, changeSize
    print ("Running glitch live")
    instructions()
    init()    
    while not q :
        if p and size : play12()
        elif p and not size : play8()
        if changeSize : changeSize = False ; p = True
    spi.close()
    rot1.cancel() ; rot2.cancel() ; rot3.cancel()
    rot4.cancel() ; rot5.cancel()
        
def play8(): # play with 8 bit samples
    global a, b, c, t, p, v, r
    r = algorithm[useA]
    while p:
        v = eval(r)
        t +=1
        spi.writebytes([0x70 | ( (v >> 4) & 0xF), (v & 0xF) << 4])    

def play12(): # play with 12 bit samples
    global a, b, c, t, p, v, r
    r = algorithm[useA]
    while p:
        v = eval(r)
        t +=1
        spi.writebytes([0x70 | ( (v >> 8) & 0xF), v & 0xFF])

def init():
    global spi, a, b, c, v, t, p, q, maxRate
    global useA, rate, size, changeSize, rateCount
    global rot1, rot2, rot3, rot4, rot5, transDelay
    os.system("sudo pigpiod")
    time.sleep(1.0)
    spi = spidev.SpiDev()
    spi.open(0,0)
    maxRate = 8000000 # maximum SPI transfer rate
    rate = maxRate
    spi.max_speed_hz = rate
    spi.mode = 0x0
    a = 5 ; b = 2 ; c = 3 # constants to change sounds
    t = 1 ; v = 0 ; size = False ; changeSize = False
    rateCount = 1
    p = False # play flag
    q = False # quit program flag
    useA = 2 # initial algorithm to use
    transDelay = ["5.7 us", "7.8 us", "12.1 us", "20.6 us", "50.4 us",
                  "86 us", "235 us", "596 us", "1.176 ms" ] 
    # setting up the rotary encoders
    rot1 = Ky040(clk=21, dt=19, cbrot = cbRot1,
            sw = 20, cbr =cbR1, cbf=cbP1)
    rot2 = Ky040(clk=13, dt=16, cbrot = cbRot2,
            sw = 6, cbr =cbR2, cbf=cbP2)
    rot3 = Ky040(clk=5, dt=12, cbrot = cbRot3,
            sw = 22, cbr =cbR3, cbf=cbP3)
    rot4 = Ky040(clk=27, dt=24, cbrot = cbRot4,
            sw = 17, cbr =cbR4, cbf=cbP4)
    rot5 = Ky040(clk=7, dt=23, cbrot = cbRot5,
            sw = 18, cbr =cbR5, cbf=cbP5)
    makeAlgorithm()

def makeAlgorithm() :
    global aMax, aMin, bMax, bMin, cMax, cMin
    global algorithm, maxRec
    algorithm = []
    aMax = [] ; aMin = [] ; bMax = []
    bMin = [] ; cMax = [] ; cMin = []
    # note when converting C's turnary operations into python replace a ? with if and : with else
    # also note the modulo operator does not work the same in Python as it does in C - see the MagPi artical
    # algorithm number 0
    algorithm.append("t+(t&t^t>>abs(b*2-c))-t*((t>>a)&(t%c if 2 else (a-c))&t>>b)")
    aMax.append(10) ; aMin.append(0) ; bMax.append(14)
    bMin.append(0) ; cMax.append(14) ; cMin.append(1)
    # algorithm number 1
    algorithm.append("((t & ((t >> a))) + (t | ((t >> b)))) & (t >> (c + 1)) | (t >> a) & (t * (t >> b))")
    aMax.append(10) ; aMin.append(0) ; bMax.append(14)
    bMin.append(0) ; cMax.append(14) ; cMin.append(0)
    # algorithm number 2
    algorithm.append("(t >> c | a | t >> (t >> 16)) * b + ((t >> (b + 1)) & (a + 1))")
    aMax.append(12) ; aMin.append(0) ; bMax.append(20)
    bMin.append(4) ; cMax.append(12) ; cMin.append(3)
    # algorithm number 3 
    algorithm.append("t >> c ^ t & 37 | t + (t ^ t >> a) - t * ((t >> a if 2 else 6)&t >> b)^t << 1 & (t & b if t >> 4 else t >> 10)")
    aMax.append(30) ; aMin.append(6) ; bMax.append(16)
    bMin.append(0) ; cMax.append(10) ; cMin.append(0)
    # algorithm number 4
    algorithm.append("t>>6^t&37|t+(t^t>>11)-t*((t%a if 2 else 6)&t>>11)^t<<1&(t&b if t>>4 else t>>10)")
    aMax.append(30) ; aMin.append(6) ; bMax.append(16)
    bMin.append(0) ; cMax.append(10) ; cMin.append(0)
    # algorithm number 5
    algorithm.append("b * t >> a ^ t & (37 - c) | t + ((t ^ t >> 11)) - t * ((t >> 6 if 2 else a)&t >> (c + b))^t << 1 & (t & 6 if t >> 4 else t >> c)")
    aMax.append(12) ; aMin.append(1) ; bMax.append(22)
    bMin.append(1) ; cMax.append(10) ; cMin.append(1)
    # algorithm number 6
    algorithm.append("c * t >> 2 ^ t & (30 - b) | t + ((t ^ t >> b)) - t * ((t >> 6 if a else c)&t >> (a))^t << 1 & (t & b if t >> 4 else t >> c)")
    aMax.append(24) ; aMin.append(0) ; bMax.append(22)
    bMin.append(0) ; cMax.append(16) ; cMin.append(0)
    # algorithm number 7
    algorithm.append("t+(t&t^t>>6)-t*((t>>9)&(t%16 if 2 else 6)&t>>9)")
    aMax.append(24) ; aMin.append(0) ; bMax.append(22)
    bMin.append(0) ; cMax.append(16) ; cMin.append(0)
    # algorithm number 8 
    algorithm.append("((t>>a&t)-(t>>a)+(t>>a&t))+(t*((t>>b)&b))")
    aMax.append(10) ; aMin.append(3) ; bMax.append(28)
    bMin.append(0) ; cMax.append(10) ; cMin.append(3)
    # algorithm number 9
    algorithm.append("t>>b&t if t>>a else -t>>c")
    aMax.append(10) ; aMin.append(0) ; bMax.append(17)
    bMin.append(10) ; cMax.append(8) ; cMin.append(0)
    # case 7b - algorithm number 10
    algorithm.append("((t % 42 + b) * (a >> t) | (128 & b) - (t >> a)) % ((t >> b) ^ (t | (t >> c)))")
    aMax.append(10) ; aMin.append(0) ; bMax.append(22)
    bMin.append(10) ; cMax.append(8) ; cMin.append(0)
    # algorithm number 11
    algorithm.append("(t >> a | c | t >> (t >> 16)) * b + ((t >> (b + 1)))")
    aMax.append(12) ; aMin.append(0) ; bMax.append(20)
    bMin.append(0) ; cMax.append(20) ; cMin.append(0)
    # algorithm number 12 
    algorithm.append("((t*(t>>a|t>>(a+1))&b&t>>8))^(t&t>>13|t>>6)")
    aMax.append(16) ; aMin.append(0) ; bMax.append(86)
    bMin.append(0) ; cMax.append(26) ; cMin.append(0)
    # algorithm number 13 
    algorithm.append("((t>>32)*7|(t>>a)*8|(t>>b)*7)&(t>>7)")
    aMax.append(8) ; aMin.append(0) ; bMax.append(22)
    bMin.append(0) ; cMax.append(13) ; cMin.append(0)
    # algorithm number 14
    algorithm.append("(((t >> a) % (1+(128-(b<<(t>>(9-c)))))  )) * b * (t >>( c*(t<<4))) * (t >> 18)+((t >> c) if 2 else a)&t * (t >> b)")
    aMax.append(16) ; aMin.append(4) ; bMax.append(8)
    bMin.append(1) ; cMax.append(9) ; cMin.append(2)
    # algorithm number 15
    algorithm.append("((t >> 6 if 2 else a)&t * (t >> c) | ( b) - (t >> a)) % ((t >> b) + (4 | (t >> c)))")
    aMax.append(16) ; aMin.append(4) ; bMax.append(8)
    bMin.append(1) ; cMax.append(9) ; cMin.append(2)
    # algorithm number 16
    algorithm.append("int(math.fmod(((t >> b if c else a)&t * (a) | ( 8) - (t >> 1)) , ((t >> b) + (4 | (t >> c)))))")
    aMax.append(16) ; aMin.append(4) ; bMax.append(8)
    bMin.append(1) ; cMax.append(9) ; cMin.append(2)
    # algorithm number 17
    algorithm.append("(t*12&t>>a | t*b&t>>c | t*b&c//(b << 2))-2")
    aMax.append(18) ; aMin.append(0) ; bMax.append(8)
    bMin.append(1) ; cMax.append(14) ; cMin.append(5)
    # algorithm number 18
    algorithm.append("(t*a & t >> b | t*c&t >> 7 | t*3 &t // 1024)-1")
    aMax.append(18) ; aMin.append(0) ; bMax.append(8)
    bMin.append(1) ; cMax.append(14) ; cMin.append(5)
    # algorithm number 19
    algorithm.append("(t*a & (t >> 7)) | (t*b & (t >> 10)) # c is not used")
    aMax.append(18) ; aMin.append(1) ; bMax.append(14)
    bMin.append(1) ; cMax.append(10) ; cMin.append(1)
    # algorithm number 20
    algorithm.append("((t * (t >> a) & (b * t >> 7) & (8 * t >> c)))")
    aMax.append(18) ; aMin.append(10) ; bMax.append(14)
    bMin.append(1) ; cMax.append(10) ; cMin.append(1)
    # algorithm number 21 
    algorithm.append("t>>c^t&1 | t+(t^t>>21)-t*(( b if t>>4 else a )&t>>12) ^ t<<1&( t>>4 if a&12 else t>>10)")
    aMax.append(8) ; aMin.append(0) ; bMax.append(16)
    bMin.append(0) ; cMax.append(6) ; cMin.append(1)
    # algorithm number 22
    algorithm.append("t >> c ^ t & 1 | t + (t ^ t >> 21)-t*((t >> 4 if b else a)&t >>(12 - (a >> 1)))^t << 1 & (a&12 if t >> 4 else t>>10)")
    aMax.append(8) ; aMin.append(0) ; bMax.append(16)
    bMin.append(0) ; cMax.append(6) ; cMin.append(1)
    # algorithm number 23
    algorithm.append("(t*((t>>a|t<<c)&29&t>>b))")
    aMax.append(13) ; aMin.append(0) ; bMax.append(20)
    bMin.append(0) ; cMax.append(13) ; cMin.append(0)
    maxRec = len(algorithm)
    conPram()
    print(maxRec, "algorithms loaded")
    print("Using algorithm ",useA," ",algorithm[useA])
    print("NOW - push red to start playing")

def conPram() : # constrain parameters
    global a, b, c
    if a > aMax[useA] : a = aMin[useA]
    if a < aMin[useA] : a = aMax[useA]
    if b > bMax[useA] : b = bMin[useA]
    if b < bMin[useA] : b = bMax[useA]        
    if c > cMax[useA] : c = cMin[useA]
    if c < cMin[useA] : c = cMax[useA]    
    
# change parameter a
def cbRot1(inc):
    global a
    a -= inc
    conPram()    
    print("a =",a)

# start playing
def cbP1(pin, level, tick):
    global p
    p = True
    print("playing starting ")

def cbR1(pin, level, tick):
    pass

# change parameter b
def cbRot2(inc):
    global b
    b -= inc
    conPram()    
    print("b =",b)

# restart sequence
def cbP2(pin, level, tick):
    global t
    t = 1
    print("t reset to one")

def cbR2(pin, level, tick):
    pass

# change parameter c
def cbRot3(inc):
    global c
    c -= inc
    conPram()   
    print("c =",c)

# quit the program
def cbP3(pin, level, tick):
    global q, p
    q = True
    p = False
    print("quiting program")

def cbR3(pin, level, tick):
    pass

# pick a algorithm
def cbRot4(inc):
    global useA, r
    useA -= inc
    if useA >= maxRec : useA = 0
    if useA < 0 : useA = maxRec -1
    r = algorithm[useA]
    conPram()
    print("using algorithm",useA,r)
    print("with t at",t)

# change sample size
def cbP4(pin, level, tick):
    global size, changeSize, p
    size = not size
    p = False
    changeSize = True
    if size : print("12 bit samples")
    else : print("8 bit samples")

def cbR4(pin, level, tick):
    pass

#change transfer rate
def cbRot5(inc):
    global rate, rateCount
    rateCount += inc
    if rateCount < 0 : rateCount = 0
    if rateCount > 8 : rateCount = 8
    spi.max_speed_hz = maxRate >> rateCount
    print("transfer delay",transDelay[rateCount])

# stop playing
def cbP5(pin, level, tick):
    global p
    p = False

def cbR5(pin, level, tick):
    print("playing stopped")

def instructions():
    print("push red to start playing")
    print("push yellow to stop playing")
    print("push green to restart start the sequence")
    print("push blue to quit program")
    print("push megenta for 8 / 12 bit samples")
    print()
    print("rotate red to change parameter a")
    print("rotate green to change parameter b")
    print("rotate blue to change parameter c")
    print("rotate megenta to change sound generation algorithm")
    print("rotate yellow to change sample transfer delay")
    print("")
    
if __name__ == '__main__':
    main()

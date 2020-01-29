#!/usr/bin/env python3
# Test the Hex-A-Pad touch sensors and LEDs
# with simple sounds
# By Mike Cook January 2020
import sys
import time
import board
import busio
import adafruit_mpr121
import digitalio as io
import pygame
  
def main():
    global last_touch
    init()
    setMPR121()
    last_touch = cap.touched()
    print ('Adafruit MPR121 Capacitive Sensor Test')
    print ('Press Ctrl-C to quit.')
    while True:  
      if not capSenseNew.value:
          cur_touch = cap.touched()
          for i in range(0,8):
              readPins(i, cur_touch)
          last_touch = cur_touch    
          time.sleep(0.1)

def readPins(i,c_touch) :
    global last_touch
    pin_bit = 1 << i
    if c_touch & pin_bit and not last_touch & pin_bit:
        print (i,"touched - now playing",
             soundNames[i])
        if i < 6 : LEDs[i].value = True
        if i == 7 :
            i2c.writeto(0x5A, bytes([0x78,0xC0]))
        if i == 6 :
            i2c.writeto(0x5A, bytes([0x78,0x30]))
        sounds[i].play()
    if not c_touch & pin_bit and last_touch & pin_bit:
        print (i,"released")
        if i < 6 : LEDs[i].value = False
        if i == 7 :
            i2c.writeto(0x5A,bytes([0x79,0xC0]))
        if i == 6 :
            i2c.writeto(0x5A,bytes([0x79,0x30]))

def init():
    global i2c, cap, capSenseNew, LEDs, sounds
    global pygame, soundNames
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = adafruit_mpr121.MPR121(i2c)
    capSenseNew = io.DigitalInOut(board.D4)
    capSenseNew.direction = io.Direction.INPUT
    capSenseNew.pull = io.Pull.UP
    LEDs = []
    LEDpin = [board.D17, board.D18, board.D27,
              board.D22, board.D23, board.D24]
    for i in range(0,len(LEDpin)):
        led = io.DigitalInOut(LEDpin[i])
        led.direction = io.Direction.OUTPUT 
        LEDs.append(led)    
    cap.reset()
    # to see what you have
    print("I2C devices at",i2c.scan()) 
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()
    pygame.mixer.music.set_volume(1.0)    
    soundNames = ["ambi_choir", "bass_voxy_hit_c",
            "drum_splash_hard", "drum_tom_hi_hard",
            "drum_tom_lo_hard", "drum_snare_hard",
            "bass_voxy_c", "loop_amen_full"]
    sounds = [ pygame.mixer.Sound("sounds/"+
               soundNames[i]+".wav")
               for i in range(0,len(soundNames))]
    
def setMPR121(): # top 4 sensor inputs to GPIOs
    # turn off cap sense
    i2c.writeto(0x5A, bytes([0x5e,0]))
    #gpio enable top 4 bits
    i2c.writeto(0x5A, bytes([0x77,0xf0]))
    # control 0 control 1 direction
    i2c.writeto(0x5A, bytes([0x73,0xf0]))
    i2c.writeto(0x5A, bytes([0x74,0xf0]))
    i2c.writeto(0x5A, bytes([0x76,0xf0]))
    # limit sensor to first 8
    i2c.writeto(0x5A, bytes([0x5e,8])) 

if __name__ == '__main__':
    main()    


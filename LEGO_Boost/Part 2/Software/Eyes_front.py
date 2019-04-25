#!/usr/bin/env python3
# coding=utf-8
# Eyes Front - move motor A to match tilt angle
# By Mike Cook March 2019

from time import sleep
from pylgbst import *
from pylgbst.movehub import MoveHub
from pylgbst.peripherals import TiltSensor

motorAngle = 0
tiltAngle = 0
shutDown = False

def main():
  print("Eyes front - move the eyes to the front")
  conn=get_connection_auto()
  print("Hub connected - press Green button to end")
  try:
    movehub = MoveHub(conn)
    setup(movehub)
    while not shutDown:
      adjust(movehub)

  finally:
    movehub.tilt_sensor.unsubscribe(callbackTilt)
    movehub.motor_A.unsubscribe(callback_A_angle)
    movehub.button.unsubscribe(call_button)
    conn.disconnect()

def setup(movehub):
   movehub.tilt_sensor.subscribe(callbackTilt, mode=TiltSensor.MODE_3AXIS_FULL, granularity=1)
   movehub.motor_A.subscribe(callback_A_angle, granularity=1)
   movehub.button.subscribe(call_button)

def adjust(movehub): 
    maxA = 88 # maximum angle
    targetAngle = tiltAngle # so it won't change during this function
    if targetAngle > maxA: # limit target angle to approx +/- 90 Degrees
       targetAngle = maxA

    if targetAngle < -maxA:     
       targetAngle = -maxA
       
    requiredMove = int(targetAngle - motorAngle) # amount required to move
    if abs(requiredMove) > 4: # to reduce jitter
       print("Moveing",requiredMove)
       movehub.motor_A.angled(requiredMove, 0.02)
       sleep(0.5)

def callbackTilt(roll, pitch, yaw):
    global tiltAngle
    #print("Tilt roll:%s pitch:%s yaw:%s" % (roll, pitch, yaw))
    tiltAngle = pitch * 1.4 # under reporting pitch

def callback_A_angle(param1):
   global motorAngle
   motorAngle = param1

def call_button(is_pressed):
   global shutDown
   if not is_pressed :
     print("Closing Down")
     shutDown = True    
   
if __name__ == '__main__':
    main()

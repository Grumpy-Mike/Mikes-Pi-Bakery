# #!/usr/bin/env python3
# coding=utf-8
# Mike's Demo - put the LEGO Boost trough its paces
# By Andrey Pokhilko & Mike Cook Feb 2019

from time import sleep
import time
from pylgbst import *
from pylgbst.movehub import MoveHub, COLORS
from pylgbst.peripherals import EncodedMotor, TiltSensor, Amperage, Voltage

def main():
  print("Mike's Demo - put the LEGO Boost trough its paces")
  conn=get_connection_auto()
  try:
    movehub = MoveHub(conn)
    demo_voltage(movehub)
    demo_button(movehub) 
    demo_led_colors(movehub)   
    demo_motors_timed(movehub)
    demo_motors_angled(movehub)
    demo_port_cd_motor(movehub)
    demo_tilt_sensor_simple(movehub)
    demo_tilt_sensor_precise(movehub)
    demo_color_sensor(movehub)
    demo_motor_sensors(movehub)
    sleep(1)
    print("That's all folks")
  finally:  
    conn.disconnect()

def demo_voltage(movehub):
    print("Reading voltage & current for a short time")
    def callback1(value):
        print("Amperage: %.3f" % value)

    def callback2(value):
        print("Voltage: %.3f" % value)

    movehub.amperage.subscribe(callback1, mode=Amperage.MODE1, granularity=0)
    movehub.amperage.subscribe(callback1, mode=Amperage.MODE1, granularity=1)

    movehub.voltage.subscribe(callback2, mode=Voltage.MODE1, granularity=0)
    movehub.voltage.subscribe(callback2, mode=Voltage.MODE1, granularity=1)
    sleep(5)
    movehub.amperage.unsubscribe(callback1)
    movehub.voltage.unsubscribe(callback2)

def demo_button(movehub):
    global notPressed
    print("Please press the green button")
    notPressed = True

    def call_button(is_pressed):
        global notPressed
        if is_pressed :
           print("Thank you button pressed")
        else:
          print("Now it is released")
          notPressed = False
        
    movehub.button.subscribe(call_button)
    while notPressed:
        sleep(0.4)
    sleep(0.4)    
    movehub.button.unsubscribe(call_button)    

def demo_led_colors(movehub):
    # LED colors demo
    print("LED colours demo")
    for colour in range(1,11):
        print("Setting LED colour to: %s" % COLORS[colour])
        movehub.led.set_color(colour)
        sleep(1)
                
def demo_motors_timed(movehub):
    print("Motors movement demo: timed")
    for level in range(0, 101, 10):
        levels = level / 100.0
        print(" Speed level: %s" %  levels)
        movehub.motor_A.timed(0.2, levels)
        movehub.motor_B.timed(0.2, -levels)
    print("now moveing both motors with one command")    
    movehub.motor_AB.timed(1.5, -0.2, 0.2)
    movehub.motor_AB.timed(0.5, 1)
    movehub.motor_AB.timed(0.5, -1)


def demo_motors_angled(movehub):
    print("Motors movement demo: angled")
    for angle in range(0, 361, 90):
        print("Angle: %s" % angle)
        movehub.motor_B.angled(angle, 1)
        sleep(1)
        movehub.motor_B.angled(angle, -1)
        sleep(1)

    movehub.motor_AB.angled(360, 1, -1)
    sleep(1)
    movehub.motor_AB.angled(360, -1, 1)
    sleep(1)


def demo_port_cd_motor(movehub): # Move motor on port C or D
    print("Move external motor on Port C or D 45 degrees left & right")
    motor = None
    if isinstance(movehub.port_D, EncodedMotor):
        print("Rotation motor is on port D")
        motor = movehub.port_D
    elif isinstance(movehub.port_C, EncodedMotor):
        print("Rotation motor is on port C")
        motor = movehub.port_C
    else:
        print("Motor not found on ports C or D")
    if motor:
        print("Left")
        motor.angled(45, 0.3)
        sleep(3)
        motor.angled(45, -0.3)
        sleep(1)

        print("Right")
        motor.angled(45, -0.1)
        sleep(2)
        motor.angled(45, 0.1)
        sleep(1)

def demo_tilt_sensor_simple(movehub):
    print("Tilt sensor simple test. Turn Hub in different ways.")
    demo_tilt_sensor_simple.cnt = 0
    limit = 10 # number of times to take a reading

    def callback(state):
        demo_tilt_sensor_simple.cnt += 1
        print("Tilt # %s of %s: %s=%s" % (demo_tilt_sensor_simple.cnt, limit, TiltSensor.TRI_STATES[state], state))

    movehub.tilt_sensor.subscribe(callback, mode=TiltSensor.MODE_3AXIS_SIMPLE)
    while demo_tilt_sensor_simple.cnt < limit:
        sleep(1)
    movehub.tilt_sensor.unsubscribe(callback)

def demo_tilt_sensor_precise(movehub):
    print("Tilt sensor precise test. Turn device in different ways.")
    demo_tilt_sensor_simple.cnt = 0
    limit = 50

    def callbackTilt(roll, pitch, yaw):
        demo_tilt_sensor_simple.cnt += 1
        print("Tilt #%s of %s: roll:%s pitch:%s yaw:%s" % (demo_tilt_sensor_simple.cnt, limit, roll,pitch,yaw))

    # granularity = 3 - only fire callback function when results change by 3 or more
    movehub.tilt_sensor.subscribe(callbackTilt, mode=TiltSensor.MODE_3AXIS_FULL, granularity=3)
    while demo_tilt_sensor_simple.cnt < limit:
        sleep(1)
    movehub.tilt_sensor.unsubscribe(callbackTilt)

def callback_color(color, distance=None): # returns to nearest for distances > 1 inch
    global limit
    demo_color_sensor.cnt += 1
    correctColor = color
    if color == 5: # to correct for error in sensor
        correctColor = 6
    if distance != None:    
       metric = distance * 2.45  # distance in mm
    else:
      metric = 0
    print('#%s/%s: Colour %s, distance %.2fmm' % (demo_color_sensor.cnt, limit, COLORS[correctColor], metric))

def demo_color_sensor(movehub):
    global limit    
    print("Colour & distance sensor test: wave your hand in front of it")
    demo_color_sensor.cnt = 0
    limit = 100 # number of times to take a reading
    try:
        movehub.color_distance_sensor.subscribe(callback_color)
    except:
       print("No colour & distance sensor found")
       sleep(2)
       return        
    while demo_color_sensor.cnt < limit:
        sleep(0.5)
    # sometimes gives a warning - not sure why
    movehub.color_distance_sensor.unsubscribe(callback_color)

def demo_motor_sensors(movehub):
    global resetTimeout, posA, posB, posE
    testTime = 5
    print("Motor rotation sensors test, move by hand any motor")
    print("Test ends after %s seconds with no change" % testTime)
    print()
    demo_motor_sensors.states = {movehub.motor_A: None, movehub.motor_B: None}
    resetTimeout = False ; external = False
    posA = 0 ; posB = 0 ; posE = 0
    
    def callback_a(param1):
        global resetTimeout,posA
        last_a = demo_motor_sensors.states[movehub.motor_A]
        if last_a != param1:
           resetTimeout = True
        demo_motor_sensors.states[movehub.motor_A] = param1
        posA = param1

    def callback_b(param1):
        global resetTimeout,posB
        last_b = demo_motor_sensors.states[movehub.motor_B]
        if last_b != param1:
           resetTimeout = True
        demo_motor_sensors.states[movehub.motor_B] = param1
        posB = param1

    def callback_e(param1):
        global resetTimeout,posE
        last_e = demo_motor_sensors.states[movehub.motor_external]
        if last_e != param1:
           resetTimeout = True        
        demo_motor_sensors.states[movehub.motor_external] = param1
        posE = param1

    movehub.motor_A.subscribe(callback_a)
    movehub.motor_B.subscribe(callback_b)
    external = False

    if movehub.motor_external is not None:
        demo_motor_sensors.states[movehub.motor_external] = None
        external = True
        movehub.motor_external.subscribe(callback_e)
        
    timeOut = time.time() + testTime
    while timeOut > time.time():
      if resetTimeout :
         if external :
            print("Motor A position %s \t Motor B position %s \t External Motor position %s" % (posA, posB, posE)) 
         else:
            print("Motor A position %s \t Motor B position %s " % (posA, posB)) 
         timeOut = time.time() + testTime
         resetTimeout = False
       
    movehub.motor_A.unsubscribe(callback_a)
    movehub.motor_B.unsubscribe(callback_b)

    if movehub.motor_external is not None:
        demo_motor_sensors.states[movehub.motor_external] = None
        movehub.motor_external.unsubscribe(callback_e)

if __name__ == '__main__':
    main()

from pylgbst.movehub import MoveHub, EncodedMotor
import time

def callback(angle):
    print("Angle: %s" % angle)

hub = MoveHub()
print("read motor angle")
hub.motor_A.subscribe(callback, mode=EncodedMotor.SENSOR_ANGLE)
time.sleep(60) # rotate motor A
hub.motor_A.unsubscribe(callback)

from pylgbst.movehub import MoveHub, ColorDistanceSensor
import time

def callback(clr, distance):   
    if clr <= 10:
       print("Colour number",clr,LED_COLORS[clr], " / Distance",distance)
    else:   
       print("Color: %s / Distance: %s" % (clr, distance))          

hub = MoveHub()

LED_COLORS = ['BLACK', '', '', 'BLUE', '', 'GREEN', '', 'YELLOW', '', 'RED', 'WHITE']
hub.color_distance_sensor.subscribe(callback, mode=ColorDistanceSensor.COLOR_DISTANCE_FLOAT)
time.sleep(60) # play with sensor while it waits   
hub.color_distance_sensor.unsubscribe(callback)

'''
Subscription mode constants in class `ColorDistanceSensor` are:
- `COLOR_DISTANCE_FLOAT` - default mode, use `callback(color, distance)` where `distance` is float value in inches
- `COLOR_ONLY` - use `callback(color)`
- `DISTANCE_INCHES` - use `callback(color)` measures distance in integer inches count
- `COUNT_2INCH` - use `callback(count)` - it counts crossing distance ~2 inches in front of sensor
- `DISTANCE_HOW_CLOSE` - use `callback(value)` - value of 0 to 255 for 30 inches, larger with closer distance
- `DISTANCE_SUBINCH_HOW_CLOSE` - use `callback(value)` - value of 0 to 255 for 1 inch, larger with closer distance
- `LUMINOSITY` - use `callback(luminosity)` where `luminosity` is float value from 0 to 1
- `OFF1` and `OFF2` - seems to turn sensor LED and notifications off
- `STREAM_3_VALUES` - use `callback(val1, val2, val3)`, sends some values correlating to distance, not well understood at the moment

Tip: laser pointer pointing to sensor makes it to trigger distance sensor
'''

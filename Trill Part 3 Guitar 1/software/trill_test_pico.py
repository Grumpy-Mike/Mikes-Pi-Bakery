'''
MicroPython
Trill test- Mike Cook March 2021
Test to check trill_lib
Pico has alternitave pin numbers for each of the two I2C busses
bus  scl sda
0     1   0
1     3   2
0     5   4
1     7   6
0     9   8
1    11  10
0    13  12
1    15  14
0    17  16
1    19  18
0    21  20
1    27  26
'''
from pico_trill_lib import PicoTrillLib
import time

def main():
    print("Trill touch sensor test")
    print("You need the pico_trill_lib installed on the Pico")
    barSensor = PicoTrillLib(1, "bar", 0x20, 15, 14, 400000)
    squareSensor = PicoTrillLib(1, "square", 0x28, 15, 14, 400000)
    barSensor.printDetails()
    print()
    squareSensor.printDetails()
    # Modes can be "CENTROID", "RAW", "BASELINE", "DIFF"
    #touchSensor.setMode("DIFF") #uncomment for raw data
    #touchSensor.printDetails()
    squareSensor.setPrescaler(3) # change for other values
    barSensor.setPrescaler(5) # change for other values
    a = input("press return to start reading")
    print("now touch the sensor")
    touchSensor = [barSensor, squareSensor]
    sensor = ["barSensor", "squareSensor"]
    s = 0
    while(1):
        touchSensor[s].readTrill()
        if touchSensor[s].getMode() == "CENTROID" :
            if touchSensor[s].getNumTouches() !=0 : # only print when touched
                print(sensor[s],touchSensor[s].getNumTouches())
                for i in range(touchSensor[s].getNumTouches()):
                    print(touchSensor[s].touchLocation(i))
                    if touchSensor[s].is2D() :
                        print(touchSensor[s].touchHorizontalLocation(i))
        else: # in any other mode
            # one at a time printing
            for i in range(touchSensor[s].getNumChannels()) :
                print(touchSensor.rawData[i])
            print("or")
            # or the whole list
            print(touchSensor[s].rawData)
            time.sleep(2.0)
        time.sleep(0.1)
        s = s ^ 0x1 # toggle the value of s
    
    
# Main program logic:
if __name__ == '__main__':
   main()
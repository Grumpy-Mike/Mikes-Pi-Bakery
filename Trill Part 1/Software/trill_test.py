#!/usr/bin/env python3
# Trill test- Mike Cook December 2020
#Test to check trill_lib
from trill_lib import TrillLib
import time

def main():
    print("Trill test")
    #Uncomment just one of these depending on what type of sensor you have attached
    #touchSensor = TrillLib(1, "bar", 0x20)
    touchSensor = TrillLib(1, "square", 0x28)
    #touchSensor = TrillLib(1, "craft", 0x30)
    #touchSensor = TrillLib(1, "ring", 0x38)
    #touchSensor = TrillLib(1, "hex", 0x40)
    touchSensor.printDetails()
    print()
    # Modes can be "CENTROID", "RAW", "BASELINE", "DIFF"
    #touchSensor.setMode("DIFF") #uncomment for raw data
    #touchSensor.printDetails()
    a = input("press return to start reading the Ctrl C to stop")
    print("now touch the sensor")
    while(1):
        touchSensor.readTrill()
        if touchSensor.getMode() == "CENTROID" :
            if touchSensor.getNumTouches() !=0 : # only print when touched
                print("Touches",touchSensor.getNumTouches())
                for i in range(touchSensor.getNumTouches()):
                    print(f'{touchSensor.touchLocation(i):.3f}')
                    if touchSensor.is2D() :
                        print(f'{touchSensor.touchHorizontalLocation(i):.3f}')
        else: # in any other mode
            '''
            # one at a time printing
            for i in range(touchSensor.getNumChannels()) :
                print(f'{touchSensor.rawData[i]:.3f}')
            print("or")
            '''
            # or the whole list
            print(touchSensor.rawData)
            time.sleep(2.0)
        time.sleep(0.1)
    
    print("Finished")
       
# Main program logic:
if __name__ == '__main__':
   main()

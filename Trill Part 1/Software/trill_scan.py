#!/usr/bin/env python3
# Trill can- Mike Cook December 2020
# Checks to see what Trill sensors are on the bus
from trill_lib import TrillLib
import time

trillType = ["none", "bar", "square", "craft", "ring", "hex"]

def main():
    attachedSensors = []
    availableSensors = []
    for device in range(0x20, 0x41) : # look at all possible addresses 
        test = TrillLib(1, "none", 256)
        if test.testForI2CDevice(device, 0, 1): # a device is found
            print("Device found at address", hex(device))
            del test
            test = TrillLib(1, "none", device) # initialise with valid address
            testType = test.getTypeNumber()
            print("Device identifies as", testType, trillType[testType])
            attachedSensors.append([trillType[testType], device])
            availableSensors.append(testType)
        del test
    print("Final Report")
    print("We found", len(availableSensors), "sensors on the I2C bus") 
    print("List of sensor types attached with addresses (decimal) :-")
    print(attachedSensors) 
       
# Main program logic:
if __name__ == '__main__':
   main()

#!/usr/bin/env python3
# calibration tap class - Mike Cook August 2020

from stmpe610 import Stmpe610
touch = Stmpe610()
class CalTap:
    # values from the cal program
    corner1 = (270, 799, 18)
    corner2 = (3867, 3707, 209)
    led0  = (480, 1128, 140)
    led7  = (483, 3383, 150)
    led120  = (3658, 1063, 138)

    centerY = [-1] * 8
    centerX = [-1] * 16
    def __init__(self):
        self.touch = Stmpe610()
        self.centerY[0] = self.led0[1]
        self.centerY[7] = self.led7[1]
        self.centerX[0] = self.led0[0]
        self.centerX[15] = self.led120[0]
        self.interp()
        
    def interp(self):
        increment = (self.centerY[7] - self.centerY[0]) / 7
        #print("increment Y", increment)
        for i in range(1,7):
            newY = int(self.centerY[0] + increment * i)        
            self.centerY[i] = newY
            
        increment = (self.centerX[15] - self.centerX[0]) / 15
        #print("increment", increment)
        for i in range(1,15):
            newX = int(self.centerX[0] + increment * i)        
            self.centerX[i] = newX    
            
    def findClosest(self, point):
        closestDistance = 9999
        closestPixelY = -1
        for i in range(0,8):
            dist = abs(point[1] - self.centerY[i])
            if dist < closestDistance:
                closestDistance = dist
                closestPixelY = i
        closestDistance = 9999
        closestPixelX = -1
        for i in range(0,16):
            dist = abs(point[0] - self.centerX[i])
            if dist < closestDistance:
                closestDistance = dist
                closestPixelX = i
        #print("Pixel X", closestPixelX,"Pixel Y ",closestPixelY)
        # return X , Y, LED number        
        return (closestPixelX, closestPixelY, closestPixelX * 8 + closestPixelY, point[3])

    def touched(self):
        return touch.touched()

    def getPos(self):
        pos = touch.readPos()
        if pos[3] : return self.findClosest(pos)
        return pos
    
    def getRawMax(self): # get the maximum raw position
        return self.corner2
    
    def getRawMin(self): # get the minimum raw position
        return self.corner1

    def rawRead(self): # if being touched get the raw position
        if touch.touched() :
            pos = touch.readPos()
            return ( pos[0], pos[1], pos[2], True ) # a valid reading
        else : # if not being touched
           return ( 0, 0, 0, False ) # False no valid reading

    def getRaw(self): # if being touched get the cropped raw value
        if touch.touched() :
            pos = touch.readPos()
            #constrain values
            x = min(self.corner2[0], max(self.corner1[0], pos[0]))
            y = min(self.corner2[1], max(self.corner1[1], pos[1]))
            # remove offsets
            x -= self.corner1[0]
            y -= self.corner1[1]
            return ( x, y, pos[2], True ) # a valid reading
        else : # if not being touched
           return ( 0, 0, 0, False ) # False no valid reading

            

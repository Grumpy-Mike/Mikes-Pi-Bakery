'''
class to drive the Trill Touch sensor from the Pico
plus test as well to help development of a class libiary
by Mike Cook February 2021
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

from machine import Pin, I2C 
import time

kCentroidLengthDefault = 20
kCentroidLengthRing = 24
kCentroidLength2D = 32
kRawLength = 60
kCommandNone = 0
kCommandMode = 1
kCommandScanSettings = 2
kCommandPrescaler = 3
kCommandNoiseThreshold = 4
kCommandIdac = 5
kCommandBaselineUpdate = 6
kCommandMinimumSize = 7
kCommandAutoScanInterval = 1
kCommandIdentify = 255
kOffsetCommand = 0
kOffsetData = 4
kNumChannelsBar = 26
kNumChannelsRing = 28
kNumChannelsMax = 30
kMaxTouchNum1D = 5
kMaxTouchNum2D = 4
commandSleepTime = 0.01 
modeTypes = ["CENTROID", "RAW", "BASELINE", "DIFF"]
trillTypes = ["none", "bar", "square", "craft", "ring", "hex"]
trillAddress = [ [0x20, 0x48], [0x20 , 0x28], [0x28, 0x30], [0x30, 0x38], [0x38, 0x40], [0x40, 0x48] ]
#trillSize = [ [1, 0, 1], [3200, 0, 4566], [1792, 1792, 3780], [4096, 0, 1], [3584, 0, 5000], [1920, 1664,4000]]
# to fix divide by zero error that C doesn't throw + updates to allow 16 bit A/D
trillSize = [ [1.0, 1.0, 1.0], [3200.0, 1.0, 18264.0], [1792.0, 1792.0, 15120.0], [4096.0, 1.0, 1.0], [3584.0, 1.0, 25000.0], [1920.0, 1664.0, 20000.0]]

class PicoTrillLib:

    def __init__(self, bus, tt, addr, sclp, sdap): # tt - trill type string addr - I2C address
        self.dataBuffer = [0] * kRawLength
        self.rawData = [0] * kNumChannelsMax
        self.bus = bus
        self.i2c = I2C(bus, scl=Pin(sclp), sda=Pin(sdap), freq=400000) # selects from choice of pins on the Pico
        self.devices = self.i2c.scan() # get a list of all devices on the bus
        if addr >= 128 : return # so calling program will can and find a valid address        
        # been given a validate I2C address and trill type - now check they match
        if tt in trillTypes :
            self.typeNumber = trillTypes.index(tt)
        else :
            raise BaseException("Error - " + tt +" is not a valid Trill type")
            return        
        if not (addr >= trillAddress[self.typeNumber][0] and addr <= trillAddress[self.typeNumber][1]) :
            raise BaseException("Error - " + hex(addr) +" is not a Trill type " + tt + " address")
            return
        self.addr = addr
        self.tt = tt       
        self.modeNumber = 0
        self.max_touch_1D_or_2D = kMaxTouchNum1D
        # trill size [pos, posH, size] at index of trillTypes 
        self.deviceSize = trillSize[self.typeNumber]
        if tt == "craft" : self.setMode("DIFF")
        else: self.setMode("CENTROID") # default mode for all other types
        if self.setScanSettings(0, 12) : raise BaseException("Error - unable to set scan settings")        
        if self.updateBaseLine() : raise BaseException("Error - unable to set base line")      
        if self.prepareForDataRead() : raise BaseException("Error - unable to prepare for data read")
        # test read to see if we can access the device
        self.identify()
        self.typeNumber = self.device_type_
        #print('self.typeNumber is', self.typeNumber)
        tt = trillTypes[self.typeNumber]
        
    def getTypeNumber(self): # get the Trill type number of this instance 
        return self.typeNumber
    
    def getDeviceFromName(self, name): # get the Trill type string of this instance 
        if name in trillTypes : 
            return trillTypes.index(name)
        else:
            return "Invalid device name "
    
    def getNameFromMode(self, mode): # get the current Trill mode number 
        if mode < 0 or mode > 3: return "Invalid mode number"
        return modeTypes[mode]
    
    def getMode(self):    # get the current Trill mode name
        return modeTypes[self.modeNumber]
    
    def identify(self): # check that the address we have is that of a Trill device
        self.device_type_ = 0
        block = [kCommandIdentify]
        if self.txI2C(kOffsetCommand, block) : # set in the identity mode
            raise BaseException("Device not found for identify command")
        else:
            self.prepairedForDataRead_ = False
            time.sleep(commandSleepTime)
            self.rxI2C(kOffsetCommand, 4) # ignore first reading
            bytesRead = self.rxI2C(kOffsetCommand, 4)
            #print('identify returned', bytesRead[0], bytesRead[1], bytesRead[2], bytesRead[3], )
            if bytesRead[1] == 0 : # assume the device did not respond
                return -1
            self.device_type_ = bytesRead[1] 
            self.firmware_version_ = bytesRead[2]
    
    def updateRescale(self): # refresh scale factors
        scale = 1 << (16 - self.numBits)
        #scale += 0.1 ; scale -= 0.1
        self.posRescale = 1.0 / self.deviceSize[0]
        self.posHRescale = 1.0 / self.deviceSize[1]
        self.sizeRescale = scale / self.deviceSize[2]
        self.rawRescale = 1.0 / (1 << self.numBits)

    def printDetails(self): # print details of this device and this library to the console
        print("Device type",trillTypes[self.typeNumber])
        print("At I2C address:-", str(hex(self.addr)))
        print("Running in mode:-", modeTypes[self.modeNumber])
        print("Device size:-", self.deviceSize)
        print("Device version number", self.firmware_version_)
        print("Python library version Pico 1.0")
    
    def setMode(self, modeToSet): # set the current working mode from a mode number
        if modeToSet in modeTypes :
            self.modeNumber = modeTypes.index(modeToSet)
            block = [kCommandMode, self.modeNumber]            
            if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting mode")
            else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
        else:
            raise BaseException("Error - mode" + modeToSet + "is not a valid mode")
    
    def setScanSettings(self, speed, num_bits): # parameters of auto scan
        if speed > 3 : speed = 3
        if num_bits < 9 : num_bits = 9
        if num_bits > 16 : num_bits = 16
        block = [kCommandScanSettings, speed, num_bits]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting Scan")
        else:
            self.prepairedForDataRead_ = False
            self.numBits = num_bits
            self.updateRescale()
            time.sleep(commandSleepTime)       
    
    def setPrescaler(self, prescaler): # set the register of the I2C device
        block = [kCommandPrescaler, prescaler]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting Prescaler")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
    
    def setNoiseThreshold(self, threshold): # ignore readings lower than this
        threshold = threshold * (1 << self.numBits)
        if threshold > 255 : threshold = 255
        thByte = int(threshold + 0.5)
        block = [kCommandNoiseThreshold, thByte]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting noise threshold")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
    
    def setIDACValue(self, value): # A/D converter settings
        block = [kCommandIdac, value]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting IDAC value")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)

    def setMinimumTouchSize(self, minSize): # minimum size of touch considered valid
        maxMinSize = (1 << 16) - 1
        if(maxMinSize > minSize / self.sizeRescale): minSize = maxMinSize # clip to max value we can send
        else: size = minSize / self.sizeRescale        
        block[kCommandMinimumSize, size >> 8, size & 0xFF]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting minimum touch size")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
        return 0

    def setAutoScanInterval(self, interval): # set the auto scan speed
        block = [kCommandAutoScanInterval, int(interval >> 8), int(interval & 0xFF)]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting Auto Scan Interval")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
                          
    def updateBaseLine(self): # set the base line all readings have these values subtracted in the DIFF mode
        block = [kCommandBaselineUpdate]
        if self.txI2C(kOffsetCommand, block) : raise BaseException("Device not found setting base line")
        else: self.prepairedForDataRead_ = False ; time.sleep(commandSleepTime)
        return 0
    
    def prepareForDataRead(self): # set up the registers of the Trill device for a data reading
        if not self.prepairedForDataRead_ :
            #self.bus.write_byte(self.addr, kOffsetData) # send one byte
            self.i2c.writeto(self.addr, bytearray(kOffsetData))
            self.prepairedForDataRead_ = True
            time.sleep(commandSleepTime)
            return 0
        
    def readI2C(self) : # for compatibility with the C library
        self.readTrill()
        
    def readTrill(self) : # read the Trill device and process it according to the current mode
        self.prepareForDataRead()
        bytesToRead = kCentroidLengthDefault
        self.num_touches_ = 0
        if("CENTROID" == modeTypes[self.modeNumber]) :
            if self.tt == 'square' or self.tt == 'hex' :
                    bytesToRead = kCentroidLength2D;
            if self.tt == 'ring' :
                    bytesToRead = kCentroidLengthRing;
        else :
            bytesToRead = kRawLength   
        self.dataBuffer = self.rxI2C(kOffsetData, bytesToRead)
        if len(self.dataBuffer) != bytesToRead :
            print("only got", len(self.dataBuffer), "when asked for", bytesToRead) 
            return 1        
        
        if "CENTROID" != modeTypes[self.modeNumber] :
                for i in range (0, self.getNumChannels()) :
                    self.rawData[i] = (((self.dataBuffer[2 * i] << 8) + self.dataBuffer[2 * i + 1]) & 0x0FFF) * self.rawRescale
        else:   
            locations = 0
            #Look for 1st instance of 0xFFFF (no touch) in the buffer
            for locations in range(0,  self.max_touch_1D_or_2D + 1) :
                    if self.dataBuffer[2 * locations] == 0xFF and self.dataBuffer[2 * locations + 1] == 0xFF :
                        break
            self.num_touches_ = locations
            if self.tt == "square" or self.tt == 'hex' :
                # Look for the number of horizontal touches in 2D sliders
                # which might be different from number of vertical touches
                self.topHalf = bytesToRead // 2
                for locations in range(0,  self.max_touch_1D_or_2D) :
                    if self.dataBuffer[2 * locations + self.topHalf] == 0xFF and self.dataBuffer[2 * locations + self.topHalf + 1] == 0xFF :
                        break
                self.num_touches_ |= locations << 4 # pack into the top four bits
        return 0
    
    def is1D(self): # is this device a one dimensional device?
        if modeTypes[self.modeNumber] != "CENTROID" : return False
        if self.tt == 'bar' or self.tt == 'ring' or self.tt == 'craft' :
            return True;
        else :
            return False;
        
    def is2D(self): # is this device a two dimensional device?
        if self.tt == 'square' or self.tt == 'hex' :
            return True
        else:
            return False;
        
    def getNumTouches(self): # how many touches (vertical) are being detected?
            if modeTypes[self.modeNumber] != "CENTROID" : return 0
            # Lower 4 bits hold number of 1-axis or vertical touches
            return (self.num_touches_ & 0x0F)

    def getNumHorizontalTouches(self): # how many Horizontal touches are being detected?
        if modeTypes[self.modeNumber] != "CENTROID" or (self.tt != 'square' and self.tt != 'hex') :
            return 0
        return (self.num_touches_  >> 4)

    def touchLocation(self, touch_num): # where is the touch returns a value 0.0 to 1.0
        if modeTypes[self.modeNumber] != "CENTROID" : return -1
        if touch_num >= self.max_touch_1D_or_2D : return -1
        location = self.dataBuffer[2 * touch_num] << 8
        location |= self.dataBuffer[2 * touch_num + 1]
        return location * self.posRescale

    def getButtonValue(self, button_num): # Get the value of the capacitive "button" channels on the device
        if modeTypes[self.modeNumber] != "CENTROID" : return -1
        if button_num > 1 : return -1
        if self.tt != "ring" : return -1
        return ((self.dataBuffer[4 * self.max_touch_1D_or_2D + 2* button_num] << 8) +
                   self.dataBuffer[4 * self.max_touch_1D_or_2D + 2* button_num + 1] & 0xFFF) *self.rawRescale
           
    def touchSize(self, touch_num): # the size of the touch, if the touch exists, or 0 otherwise
        if modeTypes[self.modeNumber] != "CENTROID" : return -1
        if touch_num >= self.max_touch_1D_or_2D : return -1
        size = self.dataBuffer[2 * touch_num + 2* self.max_touch_1D_or_2D] * 256 
        size += self.dataBuffer[2 * touch_num + 2* self.max_touch_1D_or_2D + 1]
        return size * self.sizeRescale
         
    def touchHorizontalLocation(self, touch_num): # Get the location of a touch on the horizontal axis of the device.
        if(modeTypes[self.modeNumber] != "CENTROID" or (self.tt != 'square' and  self.tt != 'hex')):
            return -1
        if(touch_num >= self.max_touch_1D_or_2D):
            return -1
        location = self.dataBuffer[2 * touch_num + self.topHalf] << 8 | self.dataBuffer[2 * touch_num + self.topHalf+1]
        place = location * self.posHRescale
        if place >1.0 : place = 1.0
        return place
    
    def touchHorizontalSize(self, touch_num) : # get the size of the touch, if the touch exists, or 0 otherwise. 
        if(modeTypes[self.modeNumber] != "CENTROID"  or (self.tt != 'square' and  self.tt != 'hex')):
            return -1
        if(touch_num >=  self.max_touch_1D_or_2D):
            return -1;
        size = self.dataBuffer[2*touch_num + 6* self.max_touch_1D_or_2D] * 256
        size += self.dataBuffer[2*touch_num + 6* self.max_touch_1D_or_2D + 1]
        return size * self.sizeRescale;

    def compoundTouch(self, LOCATION, SIZE, TOUCHES) :
        favg = 0.0
        totalSize = 0.0
        numTouches = TOUCHES
        for i in range(0,  numTouches) :
            avg += LOCATION(i) * SIZE(i)
            totalSize += SIZE(i)
        if(numTouches) :
            avg = avg / totalSize;
        return avg

    def compoundTouchLocation(self): # Get the vertical location of the compound touch on the device.
        self.compoundTouch(touchLocation, touchSize, self.getNumTouches())

    def compoundTouchHorizontalLocation(self): # Get the horizontal location of the compound touch on the device.
        self.compoundTouch(touchHorizontalLocation, touchHorizontalSize, self.getNumHorizontalTouches())

    def compoundTouchSize(self): # Get the size of the compound touch on the device.
        size = 0.0
        for i in range(0, self.getNumTouches()): size += touchSize[i]        
        return size

    def getNumChannels(self): # Get the number of capacitive channels on this device
        if self.tt == 'bar': return kNumChannelsBar
        elif self.tt == 'ring':return kNumChannelsRing
        else: return kNumChannelsMax        
    
    ### I2C calls ###
        
    def rxI2C(self, reg, number):
        #print("reading from register", reg, "reading", number, "bytes")
        r = self.i2c.readfrom_mem( self.addr, reg, number)
        return r
    
    def testForI2CDevice(self, addr, reg, value):
        valid = False
        for i in range(len(self.devices)):
            if addr == self.devices[i] : valid = True           
        return valid
    
    def txI2C(self, reg, data):
        #print("sending reg", reg, "bytes", data)
        error = False
        try :
            self.i2c.writeto_mem( self.addr, reg, bytearray(data))
        except :
            error = True
        return error # error indication      

# Main program logic:
if __name__ == '__main__':
   main()
        

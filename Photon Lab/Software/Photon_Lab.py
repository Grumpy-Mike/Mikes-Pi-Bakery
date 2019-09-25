#!/usr/bin/env python3
# Photon Lab
# By Mike Cook August 2019

from smbus import SMBus
import RPi.GPIO as io
import os, pygame, sys, time
from tkinter import filedialog
from tkinter import *

pygame.init()  
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Photon Lab")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
sWidth = 500 ; sHight = 200 ; bk = (0,0,0)
screen = pygame.display.set_mode([sWidth,sHight],0,32)
textHeight = 22;font=pygame.font.Font(None,textHeight)
backCol = (200,130,0);displayUpdate=True;running=False

def main():
   global displayUpdate, sampleTime, enabledS
   init()
   while 1:
      while not running: # set up parameters
         time.sleep(0.2) ; checkForEvent()
         if displayUpdate:
            drawScreen(); displayUpdate = False
      # prepare to run      
      data_file = open(fileName,'w')
      data_file.write("Time,"+dataTypeT[dataType]+","+gainT[gain]+",Integration time:- "+intgTimeT[intgTime]+",Excitation time "+str(exiTime)+",Start delay:- "+str(startDelay/10)+" seconds \n")
      if ledOn : # Excitation phase
        io.output(4,1);time.sleep(exiTime)
        io.output(4,0);time.sleep(startDelay/10)
      sensorEnable() # start up sensor
      sampleTime=time.time()
      while running: # put samples in a file
         readSensor()
         data_file.write(str("%.3f" % round(sampleTime,3)+","+str(ch[dataType])+"\n"))         
         updateScreen(str(ch[dataType])); checkForEvent()         
      data_file.close() # finished run
      enabledS = False # shut down the light sensor
      readSensor() # remove the last reading
      sensorDisable() # shut it down
        
def readSensor():
    global ch0,sampleTime, sampleNumber
    done = False    
    while not done:
      status = bus.read_byte_data(luxAdd, 0xA0 | 0x13)
      if status & 1 == 1:
          done = True
          bus.write_byte_data(luxAdd, 0xA0, 0x01)
    adc = bus.read_i2c_block_data(luxAdd,0xA0 | 0x14,4) 
    ch[0] = adc[1] << 8 | adc[0] # IR
    if ch[0] == 0xffff: # overflow check
       ch[0] = -1 
    ch[1] = adc[3] << 8 | adc[2] # Visible
    if ch[1] == 0xffff:
       ch[1] = -1
    ch[2] = -1
    if ch[0] != -1 and ch[1] != -1:
       ch[2] = ch[0] + ch[1]   # Full spectrum
    if enabledS : # start new conversion cycle
       bus.write_byte_data(luxAdd, 0xA0, 0x03) # next
       sampleTime = time.time() - startTime 
       sampleNumber += 1
       
def init():
    global luxAdd, bus, gain, dataType, intgTime,gainT
    global ledOn, exiTime, fileName, startDelay, logo
    global sampleNumber, dataTypeT, intgTimeT, ch
    bus = SMBus(1) # use bus 1
    luxAdd = 0x29 # address of TSL2591
    io.setmode(io.BCM); io.setwarnings(False)    
    io.setup(4,io.OUT) ; io.output(4,0)    
    # confirm we have a sensor attached
    print("Checking for TSL2591 sensor")
    sec = bus.read_byte_data(luxAdd, 0xA0 | 0x12) # ID
    if sec != 0x50:
       print("TSL2591 not found")
    else :
       print("TSL2591 found")
    gain = 2 ; intgTime = 1 ;setGain() ;ledOn = True    
    gainT = ["low gain","medium gain","high gain","maximum gain"]
    intgTimeT = ["100 mS","200 mS","300 mS","400 mS","500 mS","600 mS"]    
    dataTypeT = ["IR","Visible","Full spectrum"]    
    exiTime = 2 ; dataType = 2 ; startDelay = 1 
    ch = [0,0,0]; sampleNumber = 0
    fileName = "/home/pi/my_data.csv"    
    logo = pygame.image.load("images/Logo.png").convert_alpha()
        
def sensorEnable():
    global enabledS,sampleNumber, startTime 
    bus.write_byte_data(luxAdd, 0xA0, 0x03) # AEN on
    enabledS = True; sampleNumber = 0
    startTime = time.time()

def sensorDisable():
    global enabledS 
    bus.write_byte_data(luxAdd, 0xA0, 0x01) # AEN off
    enabledS = False

def setGain(): # gain 00 to 11 - inter 000 to 101
    bus.write_byte_data(luxAdd,0xA1,(gain<<4)|intgTime)

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def wrap(newVal,min_val, max_val):
    retVal = newVal
    if newVal < min_val :
       retVal = max_val
    if newVal > max_val :
       retVal = min_val
    return retVal

def getFileName():
    global fileName
    root = Tk()
    root.filename = filedialog.asksaveasfilename(initialdir = "/home/pi",title = "file to save data to",filetypes = (("csv files","*.csv"),("all files","*.*")))
    temp = root.filename
    if len(temp) >3 :
       fileName = temp
    root.withdraw()
    
def updateScreen(data):
   white = (255,255,255)
   pygame.draw.rect(screen,white,(320,16,115,45),0)  
   drawW("Sample "+str(sampleNumber),335,20,bk,white)
   drawW("Value "+data,335,40,bk,white)
   pygame.display.update()
    
def drawScreen():
   screen.fill(backCol)
   screen.blit(logo, (5,5) )
   if running :
      drawW("Complete measurements ",15,60,bk,backCol)
   else:    
      drawW("Run measurements ",15,60,bk,backCol)
   drawW("Data type :- "+dataTypeT[dataType],15,80,bk,backCol)
   drawW("Gain mode :- "+gainT[gain],15,100,(0,0,0),backCol)
   drawW("Integration time :- "+intgTimeT[intgTime],15,120,bk,backCol)
   if ledOn:
       drawW("Led on :- Excitation time "+str(exiTime)+" seconds",15,140,bk,backCol) 
   else:
       drawW("Led off",15,140,bk,backCol)
   drawW("Start delay :- "+str(startDelay/10)+" seconds",15,160,bk,backCol)    
   drawW("File name :- "+fileName,15,180,bk,backCol)
   pygame.display.update()

def drawW(words,x,y,col,backCol) : # drawWords
    textSurface = font.render(words,True, col,backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)

def terminate(): # close down the program
    print ("Closing down")
    sensorDisable() ; io.cleanup()
    pygame.quit() # close pygame
    os._exit(1)
    
def checkForEvent(): # see if we need to quit
   global gain, intgTime, displayUpdate, dataType
   global running, startDelay, exiTime, ledOn
   event = pygame.event.poll()
   if event.type == pygame.QUIT :
      terminate()
   if event.type == pygame.KEYDOWN :
      if event.key == pygame.K_ESCAPE :
         terminate()
      if event.key == pygame.K_c : # data run Complete
         running = False
         displayUpdate = True
      if not running:   # don't look if running
         displayUpdate = True
         if event.mod == pygame.KMOD_LSHIFT or event.mod == pygame.KMOD_RSHIFT :
           inc = -1
         else:
            inc = 1           
         if event.key == pygame.K_g : # gain
            gain += inc
            gain = constrain(gain,0,3)
            setGain()
         if event.key == pygame.K_i: #integration time
            intgTime += inc 
            intgTime = constrain(intgTime,0,5)            
            setGain()
         if event.key == pygame.K_d: # data type to use
            dataType += inc 
            dataType = wrap(dataType,0,2)
         if event.key == pygame.K_l : # excitation LED
            ledOn = not ledOn 
         if event.key == pygame.K_e : # excitation time
            exiTime += inc
            exiTime = constrain(exiTime,0,13)
         if exiTime == 0:
            ledOn = False
         else:   
            ledOn = True
         if event.key == pygame.K_f : # file name
            getFileName() 
         if event.key == pygame.K_s : # start delay
            startDelay += inc
            startDelay = constrain(startDelay,0,20)         
         if event.key == pygame.K_r : # run
            running = True          

# Main program logic:
if __name__ == '__main__':    
    main()

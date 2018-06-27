# #!/usr/bin/env python3
# Scope - Pygame powered Oscilloscope
# By Mike Cook May 2018
import serial, pygame, os, time

pygame.init() 
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Arduino / Pi Oscilloscope")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT, pygame.MOUSEBUTTONUP])

textHeight=20 ; font = pygame.font.Font(None, textHeight)
screenWidth = 720 ; screenHight = 360
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
display = pygame.Surface((512,256))
backCol = (150,150,100) ; black = (0,0,0) # background colours
pramCol = (200,200,150) # parameter colour
logo = pygame.image.load("images/PyLogo.png").convert_alpha()

sampleInput = serial.Serial("/dev/ttyUSB0",115200, timeout = 5) # For Mega or nano
#sampleInput = serial.Serial("/dev/ttyACM0",115200, timeout = 5) # For Uno

displayWidth = 512 ; displayHight = 256
LedRect = [ pygame.Rect((0,0),(0,0))]*17
inBuf = [0]*512 # quick way of getting a 512 long buffer
chOff = displayHight//2 # Channel Offset
run = [True,False,False,True,False] # run controls
expandT = 1 ; expandV = 1 # voltage & time expansion

sampleTime = 17 # uS for 58KHz sample
smples_cm = 32 * sampleTime
volts_sample = 5/1024 # volts per sample
measureTime = False ; measureVolts = False;savedTime = 0;savedVoltage = 0
cursorT = 0; cursorV = 0; vMag = 1; svLed = False; stLed = False
triggerC = 512 ; savedVoltsC = -1 ; savedTimeC = -1

def main():
    pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight+2),0)
    defineControls()
    drawControls()
    time.sleep(0.1)
    sampleInput.flushInput() # empty any buffer contents
    sampleInput.write(b'2') # tell Arduino to get a new buffer
    while(1):
       time.sleep(0.001) # let other code have a look in 
       readArduino() # get buffer data
       plotWave() # draw waveform           
       if measureTime or measureVolts :
          updateControls(True)  
       drawScope() # display new screen
       checkForEvent()
       while run[4]: # if in hold mode wait here
         checkForEvent()
       if run[3]:
         sampleInput.write(b'1') # tell Arduino to get an other buffers
       else:
             sampleInput.write(b'2') # buffer but no trigger         
       
def drawGrid():
   pygame.draw.rect(display,(240,240,240),(0,0,displayWidth,displayHight),0)
   for h in range(32,256,32): # draw horizontal
       pygame.draw.line(display,(120,120,120),(0,h),(512,h),1)
   for v in range(32,512,32): # draw vertical
       pygame.draw.line(display,(120,120,120),(v,0),(v,256),1)
   pygame.draw.line(display,(0,0,0),(256,0),(256,256),1)
   pygame.draw.line(display,(0,0,0),(0,128),(512,128),1)

def drawControls():
    drawWords("Time Magnify",10,300,black,backCol)
    drawWords("Voltage Magnify",220,300,black,backCol)
    drawWords("Measure",440,300,black,backCol)
    drawWords("Time",440,320,black,backCol)
    drawWords("Volts",486,320,black,backCol)
    drawWords("Save",540,300,black,backCol)
    drawWords("Time",540,320,black,backCol)
    drawWords("Volts",586,320,black,backCol)
    drawWords("1/"+chr(0x394)+"Time",540,257,black,backCol)
    drawWords(chr(0x394)+"Time",540,237,black,backCol)
    drawWords("Saved Time",540,217,black,backCol)
    drawWords("Time",540,197,black,backCol)
    drawWords(chr(0x394)+"Voltage",540,167,black,backCol)
    drawWords("Saved Voltage",540,147,black,backCol)
    drawWords("Voltage",540,127,black,backCol)
    drawWords("Run Single Freeze Trigger",540,77,black,backCol)
    screen.blit(logo,(540,2))
    updateControls(True)

def updateControls(blank):
    global vDisp
    if blank:
      pygame.draw.rect(screen,backCol,resultsRect,0)  
    if expandT*smples_cm >= 1000:
       drawWords("Time "+str((expandT*smples_cm)//1000)+"mS per division   ",10,280,black,backCol)
    else:
        drawWords("Time "+str(expandT*smples_cm)+"uS per division    ",10,280,black,backCol)
    volts_cm = int(volts_sample*128*1000/expandV)
    drawWords("Voltage "+str(volts_cm)+"mV per division",220,280,black,backCol)
    for n in range(0,6): # time option LED
       drawWords("x"+str(1<<n),10+n*30,320,black,backCol)
       drawLED(n,expandT == 1<<n)
    for n in range(6,9): # voltage options
       drawWords("x"+str(1<<(n-6)),220+(n-6)*30,320,black,backCol)
       drawLED(n,expandV == 1<<(n-6))       
    drawLED(9,measureTime)
    drawLED(10,measureVolts)
    drawLED(11,stLed)
    drawLED(12,svLed)
    for n in range(13,17):
       drawLED(n,run[n-13])  
    if measureTime :
       t = (cursorT>>1)*sampleTime / expandT       
       drawWords(" "+trunk(t,5)+" "+chr(0x3bc)+"S",640,197,black,pramCol) # current time        
       drawWords(" "+trunk(savedTime,5)+" "+chr(0x3bc)+"S",640,217,black,pramCol)
       drawWords(" "+trunk(t-savedTime,5)+" "+chr(0x3bc)+"S",640,237,black,pramCol) # delta time
       if t-savedTime != 0 :
          drawWords((trunk(1000000 / abs(t-savedTime),5))+" Hz",640,257,black,pramCol)
    if measureVolts :
       vDisp = (((1024-cursorV)>>2)-128)*volts_sample * vMag
       delta = vDisp - savedVoltage
       drawWords(" "+trunk(delta,4)+" V",640,167,black,pramCol) 
       drawWords(" "+trunk(savedVoltage,4)+" V",640,147,black,pramCol)
       drawWords(" "+trunk(vDisp,4)+" V",640,127,black,pramCol)
       
def trunk(value, place): # truncate a value string
    v=str(value)+"000000"
    if value>0:
       v = v[0:place]
    else:
       v = v[0:place+1] # extra place for the minus sign
    return v   
    
def drawLED(n,state): # draw LED
    if state : 
        pygame.draw.rect(screen,(240,0,0),LedRect[n],0)
    else :   
        pygame.draw.rect(screen,(240,240,240),LedRect[n],0)
    
def defineControls():
   global LedRect, resultsRect
   for n in range(0,6):
       LedRect[n] = pygame.Rect((10+n*30,336),(15,15))
   for n in range(6,9):
       LedRect[n] = pygame.Rect((220+(n-6)*30,336),(15,15))
   LedRect[9] = pygame.Rect((440,336),(15,15))  # time
   LedRect[10] = pygame.Rect((486,336),(15,15)) # volts
   LedRect[11] = pygame.Rect((540,336),(15,15)) # save time
   LedRect[12] = pygame.Rect((586,336),(15,15)) # save volts
   LedRect[13] = pygame.Rect((545,100),(15,15)) # run
   LedRect[14] = pygame.Rect((580,100),(15,15)) # single
   LedRect[15] = pygame.Rect((628,100),(15,15)) # freeze
   LedRect[16] = pygame.Rect((676,100),(15,15)) # trigger
   resultsRect = pygame.Rect((639,125),(90,153))
    
def plotWave():
    global vMag
    lastX=0 ; lastY=0
    vMag = 2 # adjust voltage scale
    if expandV == 1:
        vMag = 4
    if expandV == 4:
        vMag =1
    drawGrid()
    s = 0 # sample pointer
    for n in range(0, displayWidth, expandT):
        y = (512-inBuf[s])//vMag + chOff
        if n != 0:
            pygame.draw.line(display,(0,200,0),(lastX ,lastY), (n ,y ),2)
        lastX = n
        lastY = y
        s += 1
    if measureTime :
       pygame.draw.line(display,(0,0,255),(cursorT>>1,0), (cursorT>>1,256),1)
       if savedTimeC != -1:
         for n in range(0,256,12):  
            pygame.draw.line(display,(0,0,255),(savedTimeC,n),(savedTimeC,n+6),1)
    if measureVolts :
       pygame.draw.line(display,(255,0,0),(0,cursorV>>2), (512,cursorV>>2),1)
       if savedVoltsC != -1:
         for n in range(0,512,12):  
            pygame.draw.line(display,(255,0,0),(n,savedVoltsC),(n+6,savedVoltsC),1)
    if run[3] : # use trigger
       y = (triggerC-512)//vMag + chOff                                  
       for n in range(0,512,12):  
          pygame.draw.line(display,(255,128,0),(n,y),(n+6,y),1)
      
def drawScope(): # put display onto scope controls
    screen.blit(display,(10,10))
    pygame.display.update()
    
def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x
    textRect.top = y    
    screen.blit(textSurface, textRect)

def readArduino(): # get buffer and controls
    global cursorT, cursorV, triggerC, run
    if run[2] : #if in freeze mode funnel data into junk
       for i in range(0,1024):
          junk = sampleInput.read() 
    else: # otherwise read into the buffer   
       for i in range(0,512):
           inBuf[i] = ((ord(sampleInput.read())) << 8) | ord(sampleInput.read())
    cursorT = ((ord(sampleInput.read())) << 8) | ord(sampleInput.read())
    cursorV = 1024 - (((ord(sampleInput.read())) << 8) | ord(sampleInput.read()))
    triggerC = 1024 - (((ord(sampleInput.read())) << 8) | ord(sampleInput.read())) 
    if run[1]: #single sweep requested
       run[1] = False
       run[2] = True # put in freeze mode
       updateControls(True)
    
def handleMouse(pos): # look at mouse down
   global expandT,expandV,measureTime,measureVolts,svLed,stLed
   global savedVoltsC, savedTimeC, run
   #print(pos)
   for n in range(0,6) :
      if LedRect[n].collidepoint(pos):
         expandT = 1<<n
   for n in range(6,9) :
      if LedRect[n].collidepoint(pos): 
         expandV = 1<<(n-6)
   if LedRect[9].collidepoint(pos): #toggle time measurement
       measureTime = not(measureTime)
       if not measureTime :
         savedTimeC = -1  
   if LedRect[10].collidepoint(pos):
       measureVolts = not(measureVolts) # toggle volts measurement
       if not measureVolts :
           savedVoltsC = -1
   if LedRect[11].collidepoint(pos) and measureTime: # save time
       stLed = True
       savedTimeC = cursorT>>1
   if LedRect[12].collidepoint(pos) and measureVolts: # save volts
       svLed = True
       savedVoltsC = cursorV>>2
   # run controls logic    
   if LedRect[13].collidepoint(pos) and not run[1]: # run
       run[0] = not(run[0])
       if not run[0]:
           run[2] = True
       else:
           run[2] = False
   if LedRect[14].collidepoint(pos): # single
         run[1] = True
         run[0] = False
         run[2] = False
         run[4] = True
         updateControls(False)
         drawScope()         
   if LedRect[15].collidepoint(pos) and not run[1]: # freeze
       run[2] = not(run[2])
       if not run[2]:
           run[0] = True
       else:
           run[0] = False
   if LedRect[16].collidepoint(pos): # trigger
       run[3] = not(run[3])       
   updateControls(False)

def handleMouseUp(pos): # look at mouse up
   global savedVoltage,savedTime, svLed, stLed, run 
   if LedRect[12].collidepoint(pos) and measureVolts:
       savedVoltage = vDisp
       svLed = False
       updateControls(False)
   if LedRect[11].collidepoint(pos) and measureTime:
       savedTime = (cursorT>>1)*sampleTime / expandT
       stLed = False
       updateControls(False)
   if LedRect[14].collidepoint(pos): # single
       run[4] = False
       updateControls(False)
    
def terminate(): # close down the program
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_s : # screen dump
          os.system("scrot -u")
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())                  
        
       
# Main program logic:
if __name__ == '__main__':    
    main()

# MIDI percussion sequencer with Pots control
# By Mike Cook February 2018
import pygame, os, time, random
import functools, rtmidi
from pymouse import PyMouse 
from tkinter import *
import spidev

midiout = rtmidi.MidiOut()
pygame.init()                   # initialise graphics interface

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("MIDI Percussion sequencer")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT, pygame.MOUSEBUTTONUP])
textHeight=26 ; font = pygame.font.Font(None, textHeight)
screenWidth = 1100 ; screenHeight = 670
padXm = screenWidth-100 # maximum X of pads
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)
instRect = [ pygame.Rect((0,0),(0,0)) for i in range(0,9) ] # instrument name rectangles
instNumber = [9, 8, 11, 14, 33, 34, 20, 21, 30] # default instrument numbers
stopRect = pygame.Rect((0,0),(0,0));startRect = pygame.Rect((0,0),(0,0))
instToChange = 0 ; step = -1 ; random.seed() ; showControls = False ; controls = 0
padCols = [(28,28,28),(180,180,0)] ; playCols = [(20,20,20),(50,200,200)]
lastStep = time.time() ; running = False ; bpm = 240 # beats per minute
potValue = [0,0,0,0] ; beat = 16 ; black= (8,8,8)

def main():
    global master
    createMatrix()
    initMIDI()
    loadResource()
    pygame.draw.rect(screen,black,(0,0,screenWidth,screenHeight),0)
    drawScreen()
    setBPM(0)
    while(1):
        checkForEvent()
        if showControls :
            readPots()
        if not running :
            time.sleep(0.05) # let other code have a look in
        if time.time() >= (stepTime + lastStep) and running:
           nextStep()

def nextStep():
   global step, lastStep
   lastStep = time.time()
   step += 1
   if step >= beat:
       step = 0
   drawLeds(step)
   drawPads() # wipe out last playing colour
   drawPadsC(step)
   pygame.display.update()
   
def drawScreen():
   global instRect,stopRect,startRect
   drawLeds(step)
   drawPads()
   drawControls()
   pygame.draw.rect(screen,black,(0,0,184,screenHeight),0)
   for lab in range(0,9):
      instRect[lab] = drawWords(iNames[instNumber[lab]],176,53+(lab*70),(180,180,0),black)
   if running :   
      startRect = drawWords("Start",75,18,(0,180,0),black)
      stopRect = drawWords("Stop",144,18,(180,180,0),black)
   else:
      startRect = drawWords("Start",75,18,(180,180,0),black)
      stopRect = drawWords("Stop",144,18,(0,180,0),black)       
   pygame.display.update()
   
def drawLeds(n):
   pygame.draw.rect(screen,black,(174,0,padXm-174,33),0) 
   for sq in range (0,beat):
      if n == sq: 
         pygame.draw.circle(screen,(190,28,28),(174+38+(50*sq),20),6,0)
      else:
         pygame.draw.circle(screen,(28,28,28),(174+38+(50*sq),20),6,0)
         
def drawPads():
   pygame.draw.rect(screen,black,(184,33,padXm-190,screenHeight),0) 
   for row in range(0,9):   
      for sq in range (0,16):
         pygame.draw.rect(screen,padCols[matrixCont[row][sq]],matrixRect[row][sq],0)

def drawPadsC(c):
   for row in range(0,9):   
      pygame.draw.rect(screen,playCols[matrixCont[row][c]],matrixRect[row][c],0)
   if running :
      for row in range(0,9):
         if matrixCont[row][c] > 0 : #play note
             ch = 15-row
             midiout.send_message([0x90 | ch,instNumber[row]+27,velocity[row]]) # channel note velocity

def drawControls():
    pygame.draw.rect(screen,black,(padXm-6,0,screenWidth,30),0)
    drawWords("BPM "+str(bpm),padXm+80,10,(180,180,0),black)
    pygame.draw.rect(screen,black,(padXm-6,38,4,screenHeight),0)
    if showControls :
       pygame.draw.line(screen,(180,180,0),(padXm-6,40+(controls * 70)),(padXm-6,84+(controls * 70)),2) 
    for c in range(0,9): # draw the pot controls
       drawPots(c) 
    pygame.display.update()

def drawPots(ch):
    sX = padXm+10
    pygame.draw.rect(screen,black,(sX,46+(ch * 70),66,48),0) 
    pygame.draw.line(screen,(0,180,0),(sX,47+(ch * 70)),(sX+(volume[ch]/2),47+(ch * 70)),2) 
    pygame.draw.line(screen,(180,0,0),(sX,57+(ch * 70)),(sX+(velocity[ch]/2),57+(ch * 70)),2)
    pygame.draw.line(screen,(0,180,180),(sX,67+(ch * 70)),(sX+64,67+(ch * 70)),2) 
    pygame.draw.line(screen,(0,0,180),(sX,67+(ch * 70)),(sX+(pan[ch]/2),67+(ch * 70)),2) 
    pygame.draw.line(screen,(80,80,80),(sX,77+(ch * 70)),(sX+(reverb[ch]/2),77+(ch * 70)),2)
    
def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.right = x
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def readPots():
   for i in range(0,4):
      adc = spi.xfer2([1,(8+i)<<4,0]) # request channel
      reading = (adc[1] & 3)<<8 | adc[2] # join two bytes together 
      if abs(reading - potValue[i]) > 8:
         potValue[i] = reading
         updatePots(i,reading>>3)

def updatePots(num, value):
    ch = controls # value of channel we want to change
    if num == 0:
        volume[controls] = value
        midiout.send_message([0xB0 | 15-ch,0x07,volume[ch]])  # set volume
    if num == 1:
        velocity[controls] = value
    if num == 2:
        pan[controls] = value
        midiout.send_message([0xB0 | 15-ch,0x0A,pan[ch]])  # set pan
    if num == 3:
        reverb[controls] = value
        midiout.send_message([0xB0 | 15-ch,0x5B,reverb[ch]])  # set reverb channel
    drawPots(controls)
    pygame.display.update()
    
def loadResource():
   global iNames,spi
   nameF = open("percussion.txt","r")
   iNames = []
   for i in nameF.readlines():
       n = i[:-1] # remove CR at end of name
       iNames.append(n)
   nameF.close()
   spi = spidev.SpiDev()
   spi.open(0,0)
   spi.max_speed_hz=1000000     
       
def initMIDI(): 
   available_ports = midiout.get_ports()
   print("MIDI ports available:-")
   for i in range(0,len(available_ports)):
      print(i,available_ports[i])  
   if available_ports:
       midiout.open_port(1)
   else:
       midiout.open_virtual_port("My virtual output") 
   for ch in range(7,16): # set up channels 
     midiout.send_message([0xB0 | ch,0x07,volume[15-ch]])  # set volume
     midiout.send_message([0xB0 | ch,0x0A,pan[15-ch]])  # set pan
     midiout.send_message([0xB0 | ch,0x5B,reverb[15-ch]])  # set reverb channel
     midiout.send_message([0xB0 | ch,0x00,0x78]) # set drum bank
     midiout.send_message([0xC0 | ch,0x00]) # set instrument
   midiout.send_message([0xB0 | 7,0x0C,127])  # set global reverb  
   
def createMatrix(): # create variables
   global matrixRect, matrixCont, volume, velocity, pan, reverb
   matrixRect = [] ; matrixCont = []
   rowSq = [] ; cont = []
   for row in range(0,9):
      t = [] ; c = [] # blank row and contents list  
      for sq in range (15,-1,-1):
         t.append(pygame.Rect((padXm-60-(50*sq),40+(row * 70),46,46)))
         c.append(0)
      matrixRect.append(t) ; matrixCont.append(c)
   volume =   [ 127-c*8 for c in range(0,9) ] # channel volume
   velocity = [ 120-c*8 for c in range(0,9) ] # striking strength
   pan = [ 64 for c in range(0,9) ] # position in stereo field
   reverb = [ 127-(c*10) for c in range(0,9) ] # off by default
   
def clearPads():
   global matrixCont,step,running 
   for row in range(0,9):
      for sq in range(0,15):
        matrixCont[row][sq] = 0
   running = False
   step = 0
   drawScreen()

def randomSetup():
   clearPads()
   for row in range(0,9):
      for sq in range(0,15):
        if random.randint(0,100) > 90 : # random chance 10% 
          matrixCont[row][sq] = 1
   drawScreen()
   
def setBPM(inc):
   global stepTime,bpm
   bpm +=inc
   stepTime = 1/(bpm / 60)
   drawControls()
    
def runTk():
   global master 
   master = Tk()
   menubar = Menu(master)
   menu = AutoBreakMenu(menubar, tearoff=0)
   fillMenu(menu)
   menubar.add_cascade(label="Instrument", menu=menu)
   mouse = PyMouse()
   x = mouse.position()[0] # move menu to mouse position
   y = mouse.position()[1]
   master.config(menu=menubar)
   master.geometry('%dx%d+%d+%d' % (78,0,x-8,y-46))
   mainloop() # run drop down menu

def clicked(n): # instrument is chosen from menu 
    global instNumber
    instNumber[insToChange] = n
    master.destroy() # remove menu window
    
def handleMouse(pos): # look at mouse down
   global insToChange, running 
   #print(pos)
   if pos[0] > 184 : # look at triggers
     for row in range(0,9):
        for place in range(0,16):
           if matrixRect[row][place].collidepoint(pos):
              #print("click in pad",row,place)
              matrixCont[row][place] ^= 1 # toggle pad
              drawPads()
              pygame.display.update()
   else:
     for i in range(0,9): # look at instrument rectangles
       if instRect[i].collidepoint(pos):
         insToChange = i
         pygame.draw.rect(screen,(128,8,8),instRect[i],2)
         pygame.display.update()
         return
     if startRect.collidepoint(pos):
        running = True
     if stopRect.collidepoint(pos):
        running = False
              
def handleMouseUp(pos): # look at mouse up
   if pos[0] < 184: # instruments and controls
      for i in range(0,9): # look at instrument rectangles
         if instRect[i].collidepoint(pos):
            runTk()  # launch the instrument menu
         drawScreen()
   
def terminate(): # close down the program
    global midiout
    print ("Closing down")
    del midiout
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # handle events
    global step,controls,showControls,beat
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_c: # clear pads
           clearPads()
       if event.key == pygame.K_r: # reset sequence
           if not running:
             drawLeds(0)
             pygame.display.update()
           step = -1
       if event.key == pygame.K_i: # inspiration 
           randomSetup()
       if event.key == pygame.K_EQUALS: # increment bpm 
           setBPM(10)
       if event.key == pygame.K_MINUS: # decrement bpm 
           setBPM(-10)
       if event.key == pygame.K_w: # whole beat 
           beat = 4 ; drawLeds(step)
           pygame.display.update()
       if event.key == pygame.K_h: # half beat 
           beat = 8 ; drawLeds(step)
           pygame.display.update()
       if event.key == pygame.K_q: # quarter beat 
           beat = 16 ; drawLeds(step)
           pygame.display.update()
       if event.key >= pygame.K_1 and event.key <= pygame.K_9: # set control channel 
           controls = int(event.key - pygame.K_0)-1           
           showControls = True ; setBPM(0)
       if event.key == pygame.K_0: # cancel control channel 
           showControls = False ; setBPM(0)
          
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())                  
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())                  

def fillMenu(menu):
    for i in range(len(iNames)):
       menu.add_command(label=iNames[i], command=functools.partial(clicked,i))
    menu.add_command(label="Exit", command=functools.partial(clicked,-1))
           
class AutoBreakMenu(Menu):
   MAX_ENTRIES = 21
   def add(self, itemType, cnf={}, **kw):
     entryIndex =  1 + (self.index(END) or 0)
     if entryIndex % AutoBreakMenu.MAX_ENTRIES == 0:
       cnf.update(kw)
       cnf['columnbreak'] = 1
       kw = {}
     return Menu.add(self, itemType, cnf, **kw)

# Main program logic:
if __name__ == '__main__':    
    main()

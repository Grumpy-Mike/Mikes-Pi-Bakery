#!/usr/bin/env python3
# coding=utf-8
# Si-clops Colour Sequencer
# By Mike Cook March 2019

import time
#from pylgbst import *
#from pylgbst.movehub import MoveHub, COLORS
#from pylgbst.peripherals import EncodedMotor
import pygame, os
import functools, rtmidi

midiout = rtmidi.MidiOut()
pygame.init()
pygame.display.set_caption("Si-clops -> Colour Sequencer")
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP])
screenWidth = 430 ; screenHight = 400
cp = screenWidth // 2
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
textHeight=18 ; font = pygame.font.Font(None, textHeight)

tileColours = [ (0,0,0), (0,0,0),(0,0,0), (0,0,255), (128,128,255), (0,255,255),
                (0,255,0), (255,255,0), (255,128,0), (255,0,0), (255,255,255)]

#scannedBlock = [3,10,9,0,7,6,9,10]
scannedBlock = [3,3,3,0,7,7,7,7]
colourToTrack = [5,-1,-1,0,-1,-1,1,2,-1,3,4]
chan = [1]*6 ; velocity = [64]*6 ; mute = [False]*6
note = [56+i for i in range(0,6)]
lastNote = [0] *8
lastChan = [-1] *8
shutDown = False
update = False
tempo = 200 # BPM
nextStep = time.time()
running = False # MIDI sequencer
lastColour = 255 ; updateColour = 0
tileDistance = 0.0
currentMotor = 0
motorUpdate = True
step = 0
midiStep = 0
samples = 8
newScan = False
lineCol = (128,128,0)
backCol = (160,160,160)
hiCol = (0,255,255) # highlight colour
instNames = ["Piano","Harpsichord","Glockenspiel","Marimba","Bells","Organ","Guitar",
         "Bass","Timpani","Percusion","Alto Sax","Clarinet","Rain","Goblins",
         "Banjo","Tinkle Bell"]
insNums = [0,6,9,12,14,19,27,32,47,52,65,71,96,101,105,112] 

def main():
  global update,movehub, shutDown, step, newScan, currentMotor, newScan
  print("Colour sensor tracker test down pointing sensor")
  print("press the green button now")
  #conn=get_connection_auto()
  print("Looking for Hub")
  #movehub = MoveHub(conn)
  print("Hub connected")
  init()
  initMIDI()
  print("Initilised - press Green button to end")
  drawScreen()
  while not shutDown:
    checkForEvent()
    if newScan: 
      sensorScan()
    if time.time() > nextStep:
        doMIDIstep()    
 
def doMIDIstep():
   global nextStep, midiStep, lastNote, lastChan
   if not running:
     time.sleep(0.1) # yeald for other programs
     return
   tileNumber = colourToTrack[scannedBlock[midiStep]] 
   #print("Tile number",tileNumber)
   #turn off the note you are about to play
   if lastChan[midiStep] != -1:
      midiout.send_message([0x90 | lastChan[midiStep],lastNote[midiStep],0])

   if not mute[tileNumber]:
     #print("send to channel",chan[tileNumber],"the note",note[tileNumber],"vel",velocity[tileNumber])
     midiout.send_message([0x90 + chan[tileNumber]-1,note[tileNumber],velocity[tileNumber]]) 
   lastNote[midiStep]= note[tileNumber]
   lastChan[midiStep]= chan[tileNumber]-1
   nextStep = time.time() + stepTime
   updateSamples(midiStep)
   midiStep += 1
   if midiStep > 7:
     midiStep =0

def allOff():
  for i in range(0,16):
    midiout.send_message([0xB0 | i,120,0]) # normally only one is needed
    midiout.send_message([0xB0 | i,123,0])
    
def sensorScan():
    while step < 8:
      checkForEvent()
      displayPrams()
    movehub.motor_AB.angled(-currentMotor, .4) # back to start
    currentMotor = 0
    time.sleep(2)
    newScan = False
    step = 0

def initMIDI():
   global midiout
   available_ports = midiout.get_ports()
   print("MIDI ports available:-")
   for i in range(0,len(available_ports)):
      print(i,available_ports[i])  
   if available_ports:
     try:
        midiout.open_port(1)
     except:
       print("No MIDI port found opening virtual port")
       midiout.open_port(0)
   for ch in range(0,16): # set up channels
     if ch != 9:
        midiout.send_message([0xC0 | ch,insNums[ch]]) # set instrument
     midiout.send_message([0xB0 | ch,0x07,127])  # set volume
   setTime()    

def init():
   global motor, markerRect, shutDown, driveRect, incRect, decRect, icon, decRect, muteRect, voiceRect, sampleRect, rsRect
   #motor = None
   #movehub.button.subscribe(call_button)
   #movehub.color_distance_sensor.subscribe(callback_colour, granularity=0)
   icon = [pygame.image.load("icons/"+str(i)+".png").convert_alpha()
           for i in range(0,2) ]
   incRect = [pygame.Rect((0,0),(15,15))]*20
   decRect = [pygame.Rect((0,0),(15,15))]*20
   for j in range(0,3):
      for i in range(0,6):
         incRect[i+j*6] = pygame.Rect((76 + j*80,76+i*40),(15,15))
         decRect[i+j*6] = pygame.Rect((76 + j*80,96+i*40),(15,15))
   incRect[18] = pygame.Rect((76,326),(15,15))
   decRect[18] = pygame.Rect((76,346),(15,15))
   incRect[19] = pygame.Rect((116,326),(15,15))
   decRect[19] = pygame.Rect((116,346),(15,15))
   driveRect = pygame.Rect((176,335),(54,22))
   rsRect = pygame.Rect((296,335),(38,22))
   muteRect = [pygame.Rect((0,0),(15,15))]*6
   voiceRect = [pygame.Rect((0,0),(15,15))]*6
   for i in range(0,6):
      muteRect[i] = pygame.Rect((370,80+i*40),(28,20))
      voiceRect[i] =pygame.Rect((268,85+i*40),(100,20))
   sampleRect = [pygame.Rect((0,0),(15,15))]*8     
   for i in range(0,8):
      sampleRect[i] = pygame.Rect((58+i*40,20),(20,20))
   markerRect = [pygame.Rect((0,0),(15,15))]*8     
   for i in range(0,8):
      markerRect[i] = pygame.Rect((63+i*40,25),(10,10))
   setTime() # calculate MIDI time interval    

def displayPrams():
    global lastColour, updateColour, motorUpdate,scannedBlock, shutDown
    if updateColour >= 2 and motorUpdate:
      print("Colour %s number %s: motor angle: %s" %
            (COLORS[correctColour(lastColour)],correctColour(lastColour), step))
      scannedBlock[step] = tileColours[correctColour(lastColour)]
      updateSamples(-1)
      updateColour = 0
      motorUpdate = True
      incMotor()
    else:
      updateColour = 0   
        
def drawScreen():
   screen.fill(backCol)
   for i in range(0,20): # increment / decrement icons
      screen.blit(icon[0],(incRect[i].left,incRect[i].top))
      pygame.draw.rect(screen,lineCol,incRect[i],1)
      screen.blit(icon[1],(decRect[i].left,decRect[i].top))
      pygame.draw.rect(screen,lineCol,decRect[i],1)
      
   # draw all tiles
   playingToLego = [3,6,7,9,10,0]
   for i in range(0,6):
      pygame.draw.rect(screen, tileColours[playingToLego[i]], (10,82+40*i,20,20),0)
      
   drawWords("Tile",10,54,(0,0,0), backCol)
   drawWords("Channel",58,54,(0,0,0), backCol)
   drawWords("Note",138,54,(0,0,0), backCol)
   drawWords("Velocity",218,54,(0,0,0), backCol)
   drawWords("Voice",285,54,(0,0,0), backCol)
   drawWords("Mute",370,54,(0,0,0), backCol)
   drawWords("Tempo",10,324,(0,0,0), backCol)
   drawWords("X10",112,366,(0,0,0), backCol)
   drawWords("BPM",40,366,(0,0,0), backCol)
   drawWords("Sample",180,340,(0,0,0), backCol)
   
   pygame.draw.rect(screen, lineCol,driveRect,1)
   updateValues()    
   updateSamples(-1)

def updateSamples(point):
   for i in range(0,samples): # draw sample sequence
     #pygame.draw.rect(screen, scannedBlock[i], (10+i*40,20,20,20),0)
     pygame.draw.rect(screen, tileColours[scannedBlock[i]], sampleRect[i],0)
     pygame.draw.rect(screen, (200,128,0),sampleRect[i],1) # outline
     if point != -1:
        pygame.draw.rect(screen, (200,128,0),markerRect[point],0)           
   pygame.display.update()  

def updateValues():
   for i in range(0,6): 
     drawWords(str(chan[i])+"   ",48,85+i*40,(0,0,0), backCol)
     drawWords(str(note[i])+"   ",124,85+i*40,(0,0,0), backCol)
     drawWords(str(velocity[i])+"   ",204,85+i*40,(0,0,0), backCol)
     pygame.draw.rect(screen,backCol,voiceRect[i],0)
     drawWords(str(instNames[chan[i]-1]),270,85+i*40,(0,0,0), backCol)
     pygame.draw.rect(screen,backCol,muteRect[i],0)
     pygame.draw.rect(screen,lineCol,muteRect[i],1)
     if mute[i]:
       pygame.draw.rect(screen,backCol,muteRect[i],0)
       drawWords("Mute",370,85+i*40,(0,0,0), backCol)
   drawWords(str(tempo)+"   ",10,366,(0,0,0), backCol)
   pygame.draw.rect(screen,backCol,rsRect,0)
   if running:
     drawWords("Stop",300,340,(0,0,0), backCol)
   else:
     drawWords("Run ",300,340,(0,0,0), backCol)
   pygame.draw.rect(screen,lineCol,rsRect,1)
   if not newScan:
     pygame.draw.rect(screen, backCol,driveRect,0)
     pygame.draw.rect(screen, lineCol,driveRect,1)
     drawWords("Sample",180,340,(0,0,0), backCol)
   pygame.display.update()

def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def setTime(): # calculates the step time from the tempo (BPM)
   global stepTime,tempo
   stepTime = 1/(tempo / 60)
   updateValues()
   #print("step time",stepTime)
   
def angle_distance(position):
   dist = 31.5 * position / 1480.0
   return dist
  
def callback_colour(colour, distance): 
    global lastColour, updateColour, tileDistance
    lastColour = colour
    tileDistance = distance
    updateColour += 1

def correctColour(colour):                 
    correctColour = colour
    if colour == 5: # to correct for error in sensor
      correctColour = 6
    return correctColour

def incMotor():
   global currentMotor, motorUpdate, updateColour, step
   inc = 76.39
   currentMotor += inc
   movehub.motor_AB.angled(inc, .4)
   step += 1 # number of steps taken

def handleMouse(pos): # look at mouse down
   global pramClick, pramInc
   #print(pos)
   if driveRect.collidepoint(pos):
       pygame.draw.rect(screen,hiCol,driveRect,0)
       pygame.display.update()     
   if rsRect.collidepoint(pos):
       pygame.draw.rect(screen,hiCol,rsRect,0)
       pygame.display.update()
   for i in range(0,6):
     if muteRect[i].collidepoint(pos):
       pygame.draw.rect(screen,hiCol,muteRect[i],0)
       pygame.display.update()
       
   pramClick = -1
   pramInc = 0
   for i in range(0,20):
      if incRect[i].collidepoint(pos):
         pramClick = i
         pramInc = 1
         pygame.draw.rect(screen,hiCol,incRect[pramClick],1)
         pygame.display.update()
   for i in range(0,20):
      if decRect[i].collidepoint(pos):
         pramClick = i
         pramInc = -1
         pygame.draw.rect(screen,hiCol,decRect[pramClick],1)
         pygame.display.update()
   if pramClick == 19: # for tempo X10
      pramInc = pramInc * 10
       
def handleMouseUp(pos): # look at mouse up
  global mute, velocity, note, chan, tempo,running,newScan, midiStep,lastChan
  if rsRect.collidepoint(pos):
    running = not running
    if not running:
      allOff()
      midiStep = 0
    else:
      for i in range(0,samples):
        lastChan[i]=-1
    updateValues()
    updateSamples(-1)
  if driveRect.collidepoint(pos):
    newScan = True
    updateValues()

  if pramClick != -1: 
    if pramClick < 6:
      chan[pramClick] += pramInc
      chan[pramClick] = constrain(chan[pramClick],1,16)
    elif pramClick < 12:
      note[pramClick-6] += pramInc
      note[pramClick-6] = constrain(note[pramClick-6],15,127)
    elif pramClick < 18:
      velocity[pramClick-12] += pramInc
      velocity[pramClick-12] = constrain(velocity[pramClick-12],0,127)
    elif pramClick >= 18:   
        tempo += pramInc
        tempo = constrain(tempo,30,800)
        setTime()
    if pramInc !=0:
      if pramInc < 0:
         screen.blit(icon[1],(decRect[pramClick].left,decRect[pramClick].top))
         pygame.draw.rect(screen,lineCol,decRect[pramClick],1)
      else:   
         screen.blit(icon[0],(incRect[pramClick].left,incRect[pramClick].top))
         pygame.draw.rect(screen,lineCol,incRect[pramClick],1)
      updateValues()
  for i in range(0,6):
    if muteRect[i].collidepoint(pos):
      mute[i] = not mute[i]
      updateValues()
      
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))
  
def call_button(is_pressed): # shut down on hub button press
   global newScan
   if not is_pressed :
     #newScan = True
     fred = True

def terminate(): # close down the program
    #global midiout
    print ("Closing down")
    allOff()
    #movehub.button.unsubscribe(call_button)
    #movehub.color_distance_sensor.unsubscribe(callback_colour)
    #conn.disconnect()
    #del midiout
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    global shutDown, newScan
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          newScan = True
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())                  
            
if __name__ == '__main__':
    main()

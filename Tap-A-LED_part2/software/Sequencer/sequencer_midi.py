#!/usr/bin/env python3
# Sequencer_MIDI by Mike Cook August 2020

import time
import os
import rtmidi
import pygame
import board
import neopixel
from caltap import CalTap

def main():
    global markTime, stepTime
    init()
    setTime()
    drawScreen()
    print("Tap to change a sample")
    beingTouched = False
    while 1:
        if time.time() - markTime >=stepTime :
            markTime = time.time()
            nextStep()
            checkForEvent()
        if tap.touched() and not beingTouched:
            pos = tap.getPos()
            if pos[3] : # a valid reading
                if pixels[pos[2]] != [0, 0, 0]:
                   pixels[pos[2]] = (0, 0, 0) # turn off
                else:
                   pixels[pos[2]] = colours[pos[1]]
                beingTouched = True   
                pixels.show()
        else :
            if not tap.touched() : beingTouched = False  
            
def init():
    global colours, tap, pixels, posScan , stepTime, markTime
    global colBuffer, instNames, instNums, screen, textHeight
    global motor, markerRect, shutDown, incRect, midiout
    global decRect, icon, decRect, muteRect, voiceRect, sampleRect
    global font, rsRect, tempo, lastNote, lastChan, chan, note
    global velocity, mute, shutDown, update, lineCol, backCol, hiCol
    global running, stepTime, step, samples, newScan
    # put your own colours here if you like
    colours = [(255, 0, 0), (255, 170, 0), (169, 255, 0),
               (0, 255, 0), (0, 255, 171), (0, 168, 255),
               (1, 0, 255), (172, 0, 255) ]
    tap = CalTap()
    midiout = rtmidi.MidiOut()
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.1 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)
    pixels.fill((0, 0, 0)) ; pixels.show()
    posScan = 0 ; stepTime = 0.3 ; markTime = time.time()
    colBuffer = [(0,0,0)] * 8
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT,
                              pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP])

    pygame.display.set_caption("Tap-A-LED - MIDI Sequencer")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    sWide = 430 ; sHigh = 480
    padCo = (sWide//2 - 100, 48) # top of screen
    screen = pygame.display.set_mode([sWide,sHigh],
                                     0, 32)
    instNames = ["Piano","Harpsichord","Glockenspiel","Marimba","Bells","Organ","Guitar",
         "Bass","Timpani","Percusion","Alto Sax","Clarinet","Rain","Goblins",
         "Banjo","Tinkle Bell"]
    instNums = [0,6,9,12,14,19,27,32,47,52,65,71,96,101,105,112]
    textHeight=18 ; font = pygame.font.Font(None, textHeight)
    icon = [pygame.image.load("icons/"+str(i)+".png").convert_alpha()
        for i in range(0,2) ]
    incRect = [pygame.Rect((0,0),(15,15))]*26
    decRect = [pygame.Rect((0,0),(15,15))]*26
    for j in range(0,3):
       for i in range(0,8):
          incRect[i+j*8] = pygame.Rect((76 + j*80,76+i*40),(15,15))
          decRect[i+j*8] = pygame.Rect((76 + j*80,96+i*40),(15,15))
    incRect[24] = pygame.Rect((76,418),(15,15))
    decRect[24] = pygame.Rect((76,438),(15,15))
    incRect[25] = pygame.Rect((116,418),(15,15))
    decRect[25] = pygame.Rect((116,438),(15,15))
    rsRect = pygame.Rect((296,407),(38,22))
    muteRect = [pygame.Rect((0,0),(15,15))]*8
    voiceRect = [pygame.Rect((0,0),(15,15))]*8
    for i in range(0,8):
       muteRect[i] = pygame.Rect((370,80+i*40),(28,20))
       voiceRect[i] =pygame.Rect((268,85+i*40),(100,20))
    sampleRect = [pygame.Rect((0,0),(15,15))]*16     
    for i in range(0,16):
        sampleRect[i] = pygame.Rect((16+i*25,20),(16,16))
    markerRect = [pygame.Rect((0,0),(15,15))]*16     
    for i in range(0,16):
        markerRect[i] = pygame.Rect((19+i*25,23),(10,10))
    lastNote = [0] *16 ; lastChan = [-1] *16    
    chan = [1]*8 ; velocity = [64]*8 ; mute = [False]*8
    shutDown = False ; update = False
    lineCol = (128,128,0) ; backCol = (160,160,160)
    hiCol = (0,255,255) # highlight colour
    scale = [72, 71, 69, 67, 65, 64, 62, 60] # key of C major
    note = [scale[i] for i in range(0, 8)]
    running = False # MIDI sequencer
    tempo = 60 # BPM to start
    setTime() # determine time interval between samples
    step = 0 ; samples = 16 ; newScan = False
    initMIDI()
    
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
       print("No MIDI port 1 found opening virtual port")
       midiout.open_port(0)
   for ch in range(0,16): # set up channels
     if ch != 9:
        midiout.send_message([0xC0 | ch,instNums[ch]]) # set instrument
     midiout.send_message([0xB0 | ch,0x07,127])  # set volume    

def nextStep():
    global posScan
    if not running:
        time.sleep(0.1) # yeald for other programs
        return
    putCol(posScan)
    posScan +=1
    if posScan > 15 : posScan = 0
    getCol(posScan)
    for i in range(8):
        pixels[i + posScan * 8] = dimCol(i)
    pixels.show()
    updateSamples(posScan)

def dimCol(i):
    thresh = 40
    r = colBuffer[i][0]
    g = colBuffer[i][1]
    b = colBuffer[i][2]
    if r > thresh :
        r -= thresh
    else: r += thresh    
    if g > thresh :
        g -= thresh
    else: g += thresh    
    if b > thresh :
        b -= thresh
    else: b += thresh
    return ( r, g, b )

def putCol(pos): # restores old column of colours
    for i in range(8):
        pixels[i + pos * 8] = colBuffer[i] 
        
def getCol(pos):
    for i in range(8):
        colBuffer[i] = pixels[i + pos * 8]
        #print(colBuffer[i])
        if (colBuffer[i] != [0, 0, 0] and running):
            doMIDIout(7-i, pos)

def doMIDIout(tileNumber, midiStep):
    #turn off the note you are about to play
    if lastChan[midiStep] != -1:
        midiout.send_message([0x90 | lastChan[midiStep],lastNote[midiStep],0])
    if not mute[tileNumber]:
        #print("send to channel",chan[tileNumber],"the note",note[tileNumber],"vel",velocity[tileNumber])
        midiout.send_message([0x90 + chan[tileNumber]-1, note[tileNumber],velocity[tileNumber]]) 
    lastNote[midiStep] = note[tileNumber]
    lastChan[midiStep] = chan[tileNumber]-1

    
def drawScreen():
   screen.fill(backCol)
   for i in range(0,26): # increment / decrement icons
      screen.blit(icon[0],(incRect[i].left,incRect[i].top))
      pygame.draw.rect(screen,lineCol,incRect[i],1)
      screen.blit(icon[1],(decRect[i].left,decRect[i].top))
      pygame.draw.rect(screen,lineCol,decRect[i],1)
      
   # draw all tiles
   for i in range(8):
       pygame.draw.rect(screen, colours[7 - i], (10,82+40*i,20,20),0)

   drawWords("Colour",10,54,(0,0,0), backCol)
   drawWords("Channel",58,54,(0,0,0), backCol)
   drawWords("Note",138,54,(0,0,0), backCol)
   drawWords("Velocity",218,54,(0,0,0), backCol)
   drawWords("Voice",285,54,(0,0,0), backCol)
   drawWords("Mute",370,54,(0,0,0), backCol)
   drawWords("Tempo",10,416,(0,0,0), backCol)
   drawWords("X10",112,458,(0,0,0), backCol)
   drawWords("BPM",40,458,(0,0,0), backCol)
   #drawWords("Sample",180,412,(0,0,0), backCol)
   
   updateValues()    
   updateSamples(posScan)

def updateValues():
    for i in range(0,8): 
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
    drawWords(str(tempo)+"   ",10,458,(0,0,0), backCol)
    pygame.draw.rect(screen,backCol,rsRect,0)
    if running:
        drawWords("Stop",300,412,(0,0,0), backCol)
    else:
        drawWords("Run ",300,412,(0,0,0), backCol)
    pygame.draw.rect(screen,lineCol,rsRect,1)
    pygame.display.update()

def updateSamples(point):
   for i in range(0,samples): # draw sample progress
       pygame.draw.rect(screen, backCol, sampleRect[i],0)
       pygame.draw.rect(screen, (200,128,0),sampleRect[i],1) # outline
       if point != -1:
           pygame.draw.rect(screen, (190,190,190),markerRect[point],0)           
   pygame.display.update()  

def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True, col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def setTime(): # calculates the step time from the tempo (BPM)
   global stepTime, tempo
   stepTime = 1/((tempo/60)*4) # assume 1/4 notes per sample
   updateValues()
   
def handleMouse(pos): # look at mouse down
   global pramClick, pramInc
   #print(pos)
   if rsRect.collidepoint(pos):
       pygame.draw.rect(screen,hiCol,rsRect,0)
       pygame.display.update()
   for i in range(0,8):
     if muteRect[i].collidepoint(pos):
       pygame.draw.rect(screen,hiCol,muteRect[i],0)
       pygame.display.update()       
   pramClick = -1
   pramInc = 0
   for i in range(0,26):
      if incRect[i].collidepoint(pos):
         pramClick = i
         pramInc = 1
         pygame.draw.rect(screen,hiCol,incRect[pramClick],1)
         pygame.display.update()
   for i in range(0,26):
      if decRect[i].collidepoint(pos):
         pramClick = i
         pramInc = -1
         pygame.draw.rect(screen,hiCol,decRect[pramClick],1)
         pygame.display.update()
   if pramClick == 25: # for tempo X10
      pramInc = pramInc * 10
       
def handleMouseUp(pos): # look at mouse up
  global mute, velocity, note, chan, tempo, running, newScan, lastChan
  global posScan, markTime
  if rsRect.collidepoint(pos):
      running = not running
      if not running:
          allOff() # stop note playing
          putCol(posScan) # restore sample colours
          pixels.show()
          posScan = 0
          updateSamples(posScan) # window display
          updateValues()
      else:
          for i in range(0, samples):
              lastChan[i]=-1
          getCol(posScan)    
          for i in range(8):    
              pixels[i + posScan * 8] = dimCol(i)   
          pixels.show()
          updateValues()
          markTime = time.time()    
  if pramClick != -1: 
    if pramClick < 8:
      chan[pramClick] += pramInc
      chan[pramClick] = constrain(chan[pramClick],1,16)
    elif pramClick < 16:
      note[pramClick-8] += pramInc
      note[pramClick-8] = constrain(note[pramClick-8],15,127)
    elif pramClick < 24:
      velocity[pramClick-16] += pramInc
      velocity[pramClick-16] = constrain(velocity[pramClick-16],0,127)
    elif pramClick >= 24:   
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
  for i in range(0,8):
      if muteRect[i].collidepoint(pos):
          mute[i] = not mute[i]
          updateValues()
      
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def allOff():
  for i in range(0,16):
    midiout.send_message([0xB0 | i,120,0]) # normally only one is needed
    midiout.send_message([0xB0 | i,123,0])

def terminate(): # close down the program
    global midiout
    allOff() # all mapped MIDI notes off
    del midiout
    pixels.fill((0, 0, 0))
    pixels.show()
    pygame.quit() # close pygame
    os._exit(1)

def checkForEvent():   
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
            
    
# Main program logic:
if __name__ == '__main__':    
    main()

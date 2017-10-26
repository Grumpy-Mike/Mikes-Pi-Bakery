#!/usr/bin/env python3
# MIDI Instrument / Voice test
# By Mike Cook - = September 2017

import pygame, time, os
import rtmidi

midiout = rtmidi.MidiOut()

pygame.init()                   # initialise graphics interface

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Genral MIDI Instrument test")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT, pygame.MOUSEBUTTONUP])

screenWidth = 1030 ; screenHeight = 530
screen = pygame.display.set_mode([screenWidth,screenHeight],0,32)
textHeight = 18 ; sq = 12 # square size
font = pygame.font.Font(None, textHeight)
font2 = pygame.font.Font(None, textHeight*4)
backCol = (220,200,128) # background colour
xList = [5,184,368,542,740,880] # column positions
currentVoice = 0 ; currentNote = -1
whiteNotes = [48,50,52,53,55,57,59,60,62,64,65,67,69,71,72]
blackNotes = [49,51,54,56,58,61,63,66,68,70]
channel = 0 # change from 0 to 15 use 9 for percussion
keyboardShift = 0

def main():
   print("MIDI Sound Box - Instrument test")
   init() # open MIDI port
   loadResorces()
   drawScreen()
   initMIDI()
   findBox((10,17)) # hi-light initial voice
   while True:
      checkForEvent()
          
def loadResorces():
    global whiteKeys, blackKeys,iNames,voiceBox
    whiteKeys = []
    blackKeys = []
    voiceBox = []
    for i in range(0,15):
      whiteKeys.append((280+i*34,420,30,80)) 
    for i in range(0,13):
      if not(i ==2 or i == 6 or i == 9):
        blackKeys.append((299+i*34,420,26,40))
    nameF = open("GM_Instruments.txt","r")
    iNames = []
    for i in nameF.readlines():
       n = i[:-1] # remove CR at end of name
       iNames.append(n)
    nameF.close()   
    #print(iNames)   

def init():
   available_ports = midiout.get_ports()
   print("MIDI ports available:-")
   for i in range(0,len(available_ports)):
      print(i,available_ports[i])  
   if available_ports:
       midiout.open_port(1)
   else:
       midiout.open_virtual_port("My virtual output")
       
def initMIDI():
   midiout.send_message([0xB0 | channel,0x07,127])  # set to max volume
   midiout.send_message([0xB0 | channel,0x00,0x00]) # set default bank
   
def drawScreen():
   cp = screenWidth/2
   pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHeight),0)
   for i in range(0,len(whiteKeys)):
      pygame.draw.rect(screen,(255,255,255),whiteKeys[i],0)
   for i in range(0,len(blackKeys)):
      pygame.draw.rect(screen,(0,0,0),blackKeys[i],0)
   drawLables()   
   drawWords("Voice",60,400,4)
   drawWords("Note",847,400,4)   
   pygame.display.update()

def updateNote(n): # note displayed
   pygame.draw.rect(screen,backCol,(870,462,103,49),0)
   if n != -1:
      drawWords(str(n),874,460,4)
   pygame.display.update()

def updateVoice(n):
   pygame.draw.rect(screen,backCol,(87,462,103,49),0)
   drawWords(str(n),88,460,4)
   pygame.display.update()
   midiout.send_message([0xC0 | channel,n]) # program change message
      
def drawWords(words,x,y,s) :
        textSurface = pygame.Surface((14*s,textHeight*s))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        if s == 1: # font size
           textSurface = font.render(words, True, (0,0,0), (20,20))
        else:
           textSurface = font2.render(words, True, (0,0,0), (20,20))
        screen.blit(textSurface, textRect)
      
def drawLables():
   for i in range(0,128):
      point = getPoint(i)
      pygame.draw.rect(screen,(0,0,0),(point[0],point[1],sq,sq),1)
      drawWords(iNames[i],point[0]+20,point[1],1)

def getPoint(index):
    x = xList[ index // 22 ]
    y = 10+(index % 22)*18
    return (x,y)
   
def findBox(point):
    global currentVoice
    i=0 ; found = False
    while(i<128 and not found):
       testPoint = getPoint(i)
       testRect = pygame.Rect(testPoint[0],testPoint[1],sq,sq)
       if testRect.collidepoint(point) :
          found = True
       else:
          i += 1
    if found :
       oldPoint = getPoint(currentVoice) # remove previously checked box
       pygame.draw.rect(screen,backCol,(oldPoint[0],oldPoint[1],sq,sq),0)
       pygame.draw.rect(screen,(0,0,0),(oldPoint[0],oldPoint[1],sq,sq),1)
       pygame.draw.rect(screen,(200,0,0),(testPoint[0],testPoint[1],sq,sq),0)
       updateVoice(i)
       currentVoice = i
    
def handleMouse(pos):
    #print(pos)
    if pos[0] > 275 and pos[0] < 790 and pos[1] > 409 :
       i = 0; found = False      
       while(i<len(blackKeys) and not found):
          currentRect = pygame.Rect(blackKeys[i])
          if currentRect.collidepoint(pos):
             found = True
          else:
             i +=1
       if found :
          #print("black key number",i)
          playNote(blackNotes[i])          
       else :
          i = 0; found = False          
          while(i<len(whiteKeys) and not found):
             currentRect = pygame.Rect(whiteKeys[i])
             if currentRect.collidepoint(pos):
                found = True
             else:
                i +=1
          if found :
             #print("white key number",i)
             playNote(whiteNotes[i])
    if pos[1] < 409 :
       findBox(pos)

def playNote(note):
   global currentNote
   note += keyboardShift
   note = note  & 0x7F
   if note != currentNote:         
      midiout.send_message([0x90 | channel,note,68]) # channel 1, note, velocity 68
      currentNote = note
      updateNote(note)
            
def terminate(): # close down the program
    global midiout
    print ("Closing down please wait")
    del midiout
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # handle events
    global currentNote, keyboardShift
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_EQUALS :
          keyboardShift += 12 # move up an octave
          if keyboardShift > 55 :
             keyboardShift -= 12
          print("Shift",keyboardShift // 12, "octaves")   
       if event.key == pygame.K_MINUS :
          keyboardShift -= 12 # move up an octave
          if keyboardShift < -48 :
             keyboardShift += 12
          print("Shift",keyboardShift // 12, "octaves")           
       if event.key == pygame.K_s : # screen dump
          os.system("scrot")
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        
    if event.type == pygame.MOUSEBUTTONUP :
       if currentNote != -1:
          midiout.send_message([0x80 | channel,currentNote,0])
          currentNote = -1 # no note playing
          updateNote(currentNote)
        
# Main program logic:
if __name__ == '__main__':    
    main()

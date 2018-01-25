#!/usr/bin/env python3
# L-system with increasing multi channel sonifacation
# By Mike Cook - December 2017

import pygame, time, os, copy
import rtmidi
pygame.init()                   # initialise graphics interface

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Fractal Music L-system")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenWidth = 1000 ; screenHight = 230
screen = pygame.display.set_mode([screenWidth,screenHight],0,32)
textHeight= 20  
font = pygame.font.Font(None, textHeight)
backCol = (220,220,190) # background colour

midiout = rtmidi.MidiOut()

notes = [57,59,60,62,64,65,67]
noteDuration = 0.3
recursion = 6 # how deep to go

axiom = "AD"
rules = [("A->","AB"),("B->","BC"),("C->","ED"),("D->","AF"),
         ("E->","FG"),("F->","B"),("G->","D") ]
newAxiom = axiom

def main():
    global newAxiom
    init() # open MIDI port
    initDisplay()
    offMIDI()
    initMIDI(0,50)
    composition = [newAxiom]
    for r in range(0,recursion): # change for deeper levels / longer composition
       newAxiom = applyRules(newAxiom)
       composition.append(newAxiom)
    while 1:   
       sonify(composition)
       print()

def applyRules(start):
    expand = ""
    for i in range(0,len(start)):
       rule = start[i:i+1] +"->"
       for j in range(0,len(rules)):
          if rule == rules[j][0] :
              expand += rules[j][1]
    return expand

def sonify(data):
   global scale, noteH, lastNoteH
   noteH=0
   melodyLines = 3 # change for more or less lines
   # for more melody lines add more elements to the next three lists
   instruments = [112, 0, 96] # instruments for each line
   volume = [50, 60, 65] # volume for each instrument
   track = [[(250,0,0),(200,0,0),(150,0,0)],[(0,250,0),(0,200,0),(0,150,0)],
            [(0,250,250),(0,200,200),(0,150,150)]] # track colour
   lastNote = []
   index = []
   startTime = []
   interval = []
   lineLength = []
   scale = []
   lastNoteH = []
   for i in range(0,melodyLines): 
       initMIDI(i,volume[i]) # set up MIDI channel
       midiout.send_message([0xC0 | i,instruments[i]]) # set voice
       startTime.append(time.time()) # set up lists
       index.append(0)
       lastNote.append(0)
       interval.append(noteDuration * len(data[len(data)-1])/len(data[len(data)-1-i]))
       lineLength.append(len(data[len(data)-1-i]))
       scale.append(screenWidth/lineLength[i] )
       lastNoteH.append(0)
   for j in range(melodyLines-1,-1,-1):
      print("line",j,"voice",instruments[j],"length",lineLength[j],
             "notes of duration",interval[j],"seconds")
      for i in range(0,melodyLines):
         index[i] = 0 # restart all lines
      while notFinished(melodyLines,lineLength,index) :
         for i in range(melodyLines-1,j-1,-1):    
            if time.time() - startTime[i] > interval[i]:
               lastNote[i] = playNext(i,index[i],lastNote[i],data,len(data)-1)
               lastNoteH[i] = updateScreen(i,scale[i],index[i],interval[i],lastNoteH[i],track[i][j])
               index[i] += 1
               startTime[i] = time.time()
   time.sleep(noteDuration)   
   for i in range(0,melodyLines):
       midiout.send_message([0x80 | i,lastNote[i],68]) # last note off
   pygame.draw.rect(screen,backCol,(0,76,screenWidth,144),0)    
   time.sleep(noteDuration*4)    

def notFinished(playingLines,length, point):
    notDone = True
    for i in range(0,playingLines):
        if point[i] >= length[i] :
            notDone = False
    return notDone

def playNext(midiChannel, i , lastNote, data, line):
    global noteH
    checkForEvent()
    noteH = ord(data[line][i:i+1]) - ord('A')
    note = notes[noteH] # get note given by letter
    midiout.send_message([0x80 | midiChannel,lastNote,68]) # last note off
    midiout.send_message([0x90 | midiChannel,note,68]) # next note on
    return note

def updateScreen(i,scale,index,length,lastNh,col):
    vs = 216-(noteH*18) -i*3
    vsl = 216-(lastNh*18) -i*3
    hp = scale * (index+1)
    lhp = scale * index
    pygame.draw.line(screen,col,(lhp ,vsl ), (lhp ,vs ),2) # draw up
    pygame.draw.line(screen,col,(hp,vs),(lhp,vs),2) # draw along
    pygame.display.update()
    return noteH
    
def initDisplay():
    col = (180,64,0)
    pygame.draw.rect(screen,backCol,(0,0,screenWidth,screenHight),0)
    drawWords("Rules",5,5,col)
    drawWords(str(rules),22,22,col)
    drawWords("Axiom "+str(axiom),5,44,col)
    pygame.display.update()

def drawWords(words,x,y,col) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        textSurface = font.render(words, True, col, backCol)
        screen.blit(textSurface, textRect)
    
def init():
   available_ports = midiout.get_ports()
   print("MIDI ports available:-")
   for i in range(0,len(available_ports)):
      print(i,available_ports[i])  
   if available_ports:
       midiout.open_port(1)
   else:
       midiout.open_virtual_port("My virtual output")
       
def initMIDI(ch,vol):
   midiout.send_message([0xB0 | ch,0x07,vol])  # set to volume  
   midiout.send_message([0xB0 | ch,0x00,0x00]) # set default bank

def offMIDI():
   for ch in range(0,16):
      midiout.send_message([0xB0 | ch,0x78,0])  # notes off  

def terminate(): # close down the program
    offMIDI()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
          
# Main program logic:
if __name__ == '__main__':
         main()


#!/usr/bin/env python3
# L-system with arbatery multi channel sonifacation
# By Mike Cook - December 2017

import time, random, copy
import rtmidi

midiout = rtmidi.MidiOut()

notes = [57,59,60,62,64,65,67]
noteDuration = 0.3
channel = 0

axiom = "AD"
rules = [("A->","AB"),("B->","BC"),("C->","ED"),("D->","AF"),
         ("E->","FG"),("F->","B"),("G->","D") ]
newAxiom = axiom

def main():
    global newAxiom
    init() # open MIDI port
    offMIDI()
    initMIDI(0,50)
    print("Rules :-")
    print(rules)
    print("Axiom :-")
    print(axiom)
    composition = [newAxiom]
    for r in range(0,6): # change for deeper levels / longer composition
       newAxiom = applyRules(newAxiom)
       composition.append(newAxiom)
    sonify(composition)

def applyRules(start):
    expand = ""
    for i in range(0,len(start)):
       rule = start[i:i+1] +"->"
       for j in range(0,len(rules)):
          if rule == rules[j][0] :
              expand += rules[j][1]
    return expand

def sonify(data):
   melodyLines = 3 # change for more or less lines
   # for more melody lines add more elements to the next two lists
   instruments = [112, 0, 96] # instruments for each line
   volume = [50, 60, 65] # volume for ech line
   lastNote = []
   index = []
   startTime = []
   interval = []
   lineLength = []
   for i in range(0,melodyLines): 
       initMIDI(i,volume[i]) # setu up MIDI channel
       midiout.send_message([0xC0 | i,instruments[i]]) # set voice
       startTime.append(time.time()) # set up lists
       index.append(0)
       lastNote.append(0)
       interval.append(noteDuration * len(data[len(data)-1])/len(data[len(data)-1-i]))
       lineLength.append(len(data[len(data)-1-i]))
   print() ; print("Playing")
   for i in range(0,melodyLines):
       print("line",i,"voice",instruments[i],"length",lineLength[i],
             "notes of duration",interval[i],"seconds")
   while notFinished(melodyLines,lineLength,index) :
      for i in range(0,melodyLines):    
         if time.time() - startTime[i] > interval[i]:
             lastNote[i] = playNext(i,index[i],lastNote[i],data,len(data)-1)
             index[i] += 1
             startTime[i] = time.time()
   time.sleep(noteDuration)   
   for i in range(0,melodyLines):
       midiout.send_message([0x80 | i,lastNote[i],68]) # last note off

def notFinished(playingLines,length, point):
    notDone = True
    for i in range(0,playingLines):
        if point[i] >= length[i] :
            notDone = False
    return notDone

def playNext(midiChannel, i , lastNote, data, line):
    note = notes[ord(data[line][i:i+1]) - ord('A')] # get note given by letter
    midiout.send_message([0x80 | midiChannel,lastNote,68]) # last note off
    midiout.send_message([0x90 | midiChannel,note,68]) # next note on
    return note

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

# Main program logic:
if __name__ == '__main__':
    try:
         main()
    except:
        offMIDI()

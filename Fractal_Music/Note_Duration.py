#!/usr/bin/env python3
# L-system with MIDI output and note duration
# By Mike Cook - December 2017

import time, random, copy
import rtmidi

midiout = rtmidi.MidiOut()

notes = [57,59,60,62,64,65,67]
noteDuration = 0.3

axiom = "qAhD"
rules = [("A->","ABc"),("B->","BCh"),("C->","EDq"),("D->","AFc"),
         ("E->","FGh"),("F->","Bq"),("G->","Dc"),("q->","hA"),("h->","qF"),("c->","hF") ]
newAxiom = axiom

def main():
    global newAxiom
    init() # open MIDI port
    offMIDI()
    print("Rules :-")
    print(rules)
    print("Axiom :-")
    print(axiom)
    composition = [newAxiom]
    for r in range(0,6):
       newAxiom = applyRules(newAxiom)
       composition.append(newAxiom)
    sonify(composition)

def applyRules(start):
    expand = ""
    for i in range(0,len(start)):
       rule = start[i:i+1] +"->"
       #print("we are looking for rule",rule)
       for j in range(0,len(rules)):
          if rule == rules[j][0] :
              #print("found rule", rules[j][0],"translates to",rules[j][1])
              expand += rules[j][1]
    return expand

def sonify(data): # turn data into sound
   initMIDI(0,65) # set volume 
   midiout.send_message([0xC0 | 0,19]) # voice 19 Church organ    
   lastNote = 1
   for j in range(0,len(data)):
      duration = noteDuration # start with same note length 
      if j==0: 
         print("Axiom     ",j,data[j])
      else:
         print("Recursion ",j,data[j]) 
      for i in range(0,len(data[j])):
         symbol = ord(data[j][i:i+1])  
         if symbol >= ord('A') and symbol <= ord('G') : # it is a note
            note = notes[symbol - ord('A')] # get note given by letter
            midiout.send_message([0x80 | 0,lastNote,68]) # last note off
            midiout.send_message([0x90 | 0,note,68]) # next note on
            lastNote = note
            time.sleep(duration)
         else : # it is a note duration
            if symbol == ord('h'):
                duration = noteDuration * 2
            if symbol == ord('c'):
                duration = noteDuration
            if symbol == ord('q'):
                duration = noteDuration / 2                
      midiout.send_message([0x80 | 0,lastNote,68]) # last note off
      time.sleep(2.0)
       
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

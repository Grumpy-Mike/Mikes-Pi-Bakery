#!/usr/bin/env python3
# L-system with MIDI output state machine
# set production rules to match Inkscape
# By Mike Cook - December 2017

import time, copy
import rtmidi

midiout = rtmidi.MidiOut()

noteDuration = 0.3

axiom = "++F" # Bush
rules = [("F->","FF-[-F+F+F]+[+F-F-F]")]

newAxiom = axiom

def main():
    global newAxiom
    init() # open MIDI port
    offMIDI()
    initKey()
    print("Rules :-")
    print(rules)
    print("Axiom :-")
    print(axiom)
    composition = [newAxiom]
    for r in range(0,4): # change for deeper levels
       newAxiom = applyRules(newAxiom)
       composition.append(newAxiom)
    sonify(composition)

def applyRulesOrginal(start):
    expand = ""
    for i in range(0,len(start)):
       rule = start[i:i+1] +"->"
       for j in range(0,len(rules)):
          if rule == rules[j][0] :
              expand += rules[j][1]
    return expand

def applyRules(start):
    expand = ""
    for i in range(0,len(start)):
       symbol = start[i:i+1]
       rule =  symbol +"->"
       found = False       
       for j in range(0,len(rules)):
           
          if rule == rules[j][0] :
             expand += rules[j][1]
             found = True
       if not found :
             expand += symbol 
    return expand

def sonify(data): # turn data into sound
   initMIDI(0,65) # set volume
   noteIncrement = 1
   notePlay = len(notes) / 2
   midiout.send_message([0xC0 | 0,19]) # voice 19 Church organ    
   lastNote = 1
   for j in range(0,len(data)):
      duration = noteDuration # start with same note length
      notePlay = len(notes) / 2 # and same start note
      noteIncrement = 1 # and same note increment
      stack = [] # clear stack
      print("")
      if j==0: 
         print("Axiom     ",j,data[j])
      else:
         print("Recursion ",j,data[j]) 
      for i in range(0,len(data[j])):
         symbol = ord(data[j][i:i+1])  
         if symbol >= ord('A') and symbol <= ord('F') : # play current note
            #print(" playing",notePlay)
            note = notes[int(notePlay)]
            #print("note", note, "note increment",noteIncrement )
            midiout.send_message([0x80 | 0,lastNote,68]) # last note off
            midiout.send_message([0x90 | 0,note,68]) # next note on
            lastNote = note
         if symbol >= ord('A') and symbol <= ord('L') : # move note  
            notePlay += noteIncrement
            if notePlay < 0: # wrap round playing note
                notePlay = len(notes)-1
            elif notePlay >= len(notes):
                 notePlay = 0
            time.sleep(duration)
         if symbol == ord('+'):
            noteIncrement += 1
            if noteIncrement > 6:
                noteIncrement = 1
         if symbol == ord('-'):
            noteIncrement -= 1
            if noteIncrement < -6:
                noteIncrement = -1
         if symbol == ord('|'): # turn back
            noteIncrement = -noteIncrement
         if symbol == ord('['): # push state on stack
            stack.append((duration,notePlay,noteIncrement))
            #print("pushed",duration,notePlay,noteIncrement,"Stack depth",len(stack))            
         if symbol == ord(']'): # pull state from stack 
            if len(stack) != 0 :
               recovered = stack.pop(int(len(stack)-1))
               duration = recovered[0]
               notePlay = recovered[1]
               noteIncrement = recovered[2]
               #print("recovered",duration,notePlay,noteIncrement,"Stack depth",len(stack))
            else:
               print("stack empty")                 
      midiout.send_message([0x80 | 0,lastNote,68]) # last note off
      time.sleep(2.0)
      
def initKey():
   global startNote,endNote,notes
   key = [2,1,2,2,1,2] # defines scale type - a Major scale
   notes =[] # look up list note number to MIDI note
   startNote = 24 # defines the key (this is C )
   endNote = 84
   i = startNote
   j = 0
   while i< endNote:
      notes.append(i)
      i += key[j]
      j +=1
      if j >= 6:
        j = 0
   #print(notes)        
    
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


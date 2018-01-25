# L-system with MIDI output and note duration
# New code to add to Listing 1
# By Mike Cook - December 2017

axiom = "qAhD"
rules = [("A->","ABc"),("B->","BCh"),("C->","EDq"),("D->","AFc"),
         ("E->","FGh"),("F->","Bq"),("G->","Dc"),("q->","hA"),("h->","qF"),("c->","hF") ]

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
 
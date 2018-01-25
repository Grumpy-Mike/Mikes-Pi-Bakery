# L-system with multi channel sonifacation
# New functions for Listing 1
# By Mike Cook - December 2017

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

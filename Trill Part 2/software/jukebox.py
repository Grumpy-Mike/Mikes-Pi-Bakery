#!/usr/bin/env python
#Trill Ring Jukebox  - plays files in the Music Directory
# use one finger round the ring to see the files, make a second touch to play it
# make three touches to stop the track
# by Mike Cook - Jan 2021
# need to do pip3 install omxplayer-wrapper first
 
import os
import time
from omxplayer.player import OMXPlayer
from pathlib import Path
from trill_lib import TrillLib

ringSensor = TrillLib(1, "ring", 0x38)
ringSensor.setPrescaler(3)
lastIndex = 0
lastTouched = time.time()
fileNumber = 0

def main():
    global lastIndex, lastTouched, fileNumber
    print ("Trill Ring Jukebox")
    print ("Press Ctrl-C to stop.")
    getFiles()
    print(soundList[fileNumber] )
    while 1:
        ringSensor.readTrill()
        numTouch = ringSensor.getNumTouches()
        if numTouch !=0 : # when touched
            if numTouch == 2 :
                print("playing ", soundList[fileNumber])
                fn = "/home/pi/Music/"+str(soundList[fileNumber])
                playFile(fn)
                print("Finished playing")
                while ringSensor.getNumTouches() != 0 :
                    time.sleep(1.0) # time to take your fingers off
                    ringSensor.readTrill()
            else :    
                index = int(ringSensor.touchLocation(0) * 10) # only use first touch
                if time.time() - lastTouched > 0.5 : # new touch after release
                    lastIndex = index
                lastTouched = time.time()    
                if abs(index - lastIndex) > 0 : # found a change
                    delta = index - lastIndex
                    #print(delta)
                    lastIndex = index
                    fileNumber += delta
                    if delta == -9 : # gone round once clockwise
                        fileNumber -= delta
                        fileNumber += 1
                    if delta == 9 :  # gone round once anticlockwise
                        fileNumber -= delta
                        fileNumber -= 1                    
                    fileNumber = constrain(fileNumber, 0, len(soundList)-1)
                    #print(fileNumber, soundList[fileNumber] )
                    print(soundList[fileNumber] )
                    time.sleep(0.1)
                    
def playFile(audioPath):
    player = OMXPlayer(audioPath, 
        dbus_name = 'org.mpris.MediaPlayer2.omxplayer1')
    time.sleep(2.5) # establish player
    try :
        while player.is_playing() :
            time.sleep(0.3)
            ringSensor.readTrill()
            if ringSensor.getNumTouches() >= 3 :
                print("3 ring sensor touches - stopping")
                player.pause()
    except :
        player.quit()
    player.quit()    
                    
def getFiles():
   global soundList
   path = os.path.abspath("/home/pi/Music/")
   #get a list of files
   soundList = [fn for fn in next(os.walk(path))[2]]
   list.sort(soundList) # put in alphabetical order
   print (len(soundList), "files found")

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))
   
# Main program logic:
if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass

            

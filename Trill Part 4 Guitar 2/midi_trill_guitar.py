# MIDI Trill Guitar - by Mike Cook March 2021
from machine import UART
from machine import Pin
import time
from ssd1306 import SSD1306_I2C
from pico_trill_lib import PicoTrillLib

# set uo the I2C display
sda=machine.Pin(16)
scl=machine.Pin(17)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=1000000)  
oled = SSD1306_I2C(128, 64, i2c)
port = UART(1, 31250, tx=Pin(8), rx=None) # no receiver

# set up play / configure switch
playPin = Pin(2, Pin.IN, Pin.PULL_UP)
playMode = True

# global variables
cmd3 = bytearray(3)
cmd2 = bytearray(2)
channel = 0
stringsPlaying = [False] *6
stringTouched = [False] *6
stringNotePlaying = [0] *6
playVelocity = [38] *6
lastTouch = 0
sustainTime = 700 # number of mS before note off message
capo = 0 # number of semitones to add or subtract from the base note
stringStartTime = [time.ticks_ms()] *6
leftHanded = False # change to invert the square touch sensor
fret = 0
editParameter = 0 # for temporarily editing current set
maxSong = 40 # maximum length of song
chordProgress = [0] * maxSong 
infNum = [0] * maxSong

chordName =  ['o', 'E', 'F', 'G', 'A', 'B', 'C', 'D',
             'Em', 'Fm', 'Gm', 'Am', 'Bm', 'Cm', 'Dm',
             'E7', 'F7', 'G7', 'A7', 'B7', 'C7', 'D7',
             'E7m', 'F7m', 'G7m', 'A7m', 'B7m', 'C7m', 'D7m',
             'Eb', 'Fb', 'Gb', 'Ab', 'Bb', 'Cb', 'Db',
             'Es4', 'Fs4', 'Gs4', 'As4', 'Bs4', 'Cs4', 'Ds4']
chordBank = [
            [            40, 45, 50, 55, 59, 64],  # open strings 0
            [            40, 47, 52, 56, 59, 64],  # E major     1
            [  41, 48,           53, 57, 60, 65],  # F major     2                   
            [            43, 47, 50, 55, 59, 67],  # G major     3
            [  33,           45, 52, 57, 61, 64],  # A major     4
            [  35,           47, 54, 59, 63, 66],  # B major     5
            [  36,           48, 52, 55, 60, 64],  # C major     6
            [  38,           45, 50, 57, 62, 66],  # D major     7
                                             
            [            40, 47, 52, 55, 59, 64],  # E minor     8
            [ 41,  41,           53, 56, 60, 65],  # F minor     9 
            [            43, 50, 55, 58, 62, 67],  # G minor    10                                                
            [ 33,            45, 52, 57, 60, 64],  # A minor    11                  
            [ 35,            47, 54, 59, 62, 66],  # B minor    12
            [ 36,            48, 55, 60, 63, 67],  # C minor    13
            [ 38,            45, 50, 57, 62, 65],  # D minor    14                  
                        
            [            40, 47, 50, 56, 59, 64],  # E7 major   15
            [ 41, 41,            51, 57, 60, 65],  # F7 major   16
            [            43, 47, 50, 55, 59, 65],  # G7 major   17
            [  33,           45, 52, 57, 61, 67],  # A7 major   18
            [  35,           47, 51, 57, 59, 66],  # B7 major   19
            [  36,           48, 52, 58, 60, 64],  # C7 major   20
            [  38,  38,          50, 57, 60, 66],  # D7 major   21                 
                       
            [            40, 47, 52, 55, 62, 64],  # E7 minor   22
            [            41, 48, 51, 56, 60, 65],  # F7 minor   23
            [             43, 0, 53, 58, 62, 67],  # G7 minor   24
            [             45, 0, 55, 60, 64, 69],  # A7 minor   25
            [ 35,            47, 54, 57, 62, 66],  # B7 minor   26
            [ 36,            48, 55, 58, 63, 67],  # C7 minor   27
            [ 38,            45, 50, 57, 60, 65],  # D7 minor   28
                        
            [              0, 0, 50, 58, 63, 67],  # E flat     29                
            [ 0, 0,                  0, 0, 0, 0],  # F flat     30 - no such chord
            [ 0, 0,              54, 58, 61, 66],  # G flat     31
            [ 0, 0,              56, 60, 63, 68],  # A flat     32
            [ 0, 0,              53, 58, 62, 65],  # B flat     33
            [                  0, 0, 0, 0, 0, 0],  # C flat     34 - no such chord
            [              0, 0, 53, 56, 61, 65],  # D flat     35
                        
            [            40, 47, 52, 57, 59, 64],  # E sus 4    36
            [             0, 53, 53, 58, 60, 65],  # F sus 4    37
            [             0, 43, 50, 55, 60, 67],  # G sus 4    38
            [             0, 46, 52, 57, 62, 64],  # A sus 4    39
            [             0, 46, 53, 58, 63, 65],  # B sus 4    40
            [              0, 48, 53, 55, 60, 0],  # C sus 4    41
            [              0, 0, 50, 57, 62, 67]   # D sus 4    42  
          ]  

# File format
# first line name max 16 characters & relative link to next set
# second line file type & MIDI Channel
# third line capo value and sustain note time before sending note off message
# fourth line voice change, bank LSB
# subsequent lines fret number - chord number - 8 of these
# giving 12 lines in a set of file type 0
def loadFile():
    global config, sets, setOffsets, currentSet
    setOffsets = [0]
    nameF = open("guitarConfig.txt","r")
    config = []
    #line = 0
    for i in nameF.readlines():
       n = i[:-1] # remove CR at end of name
       f, c = n.split(',') # separate the two numbers on each line
       config.append((f, c)) # fret , chord number for file type 0 or message chord for file type 1       
    # look through config file to find address of each set
    i = 0 ; sets = 1
    while i < (len(config)-1):
        #print("offset value", int(config[i][1]), "at line", i)
        setOffsets.append(int(config[i][1]) + setOffsets[sets-1]) # make it cumulative
        i = setOffsets[sets]
        #print(setOffsets[sets])
        sets +=1
    sets -= 1
    currentSet = 0 
    #print("Loaded in ", sets, "sets")
    #print(setOffsets)
    nameF.close()
    
def iniGuitar(base): 
    global capo, sustainTime, chordProgress, fret, name, channel, fileType, link
    global voice, bank, infNum, songPointer, chorusPointer
    songPointer = 0 # current place in song
    chorusPointer = -1 # place in song for a chorus (only one per song type 1 file)
    chordProgress = [0] * maxSong
    infNum = [0] * maxSong
    s = setOffsets[base]
    name = config[s][0]
    link = int(config[s][1])
    fileType = int(config[s+1][0])
    channel = int(config[s+1][1])    
    capo = int(config[2+s][0])
    sustainTime = int(config[2+s][1])
    fret = 0        
    voice = int(config[s+3][0])
    bank = int(config[3+s][1])
    changeVoice() # 25 to 31 are General MIDI guitars, 0 bank number for GM
    if fileType == 0:
        for i in range(8):
            chordProgress[int(config[s+4+i][0]) & 0x7] = int(config[s+4+i][1])
        #print("Chord progression", chordProgress)    
    if fileType == 1:
        for i in range(4, link): # to end of song
            chordProgress[i-4] = int(config[s+i][1])
            infNum[i-4] = int(config[s+i][0])
        makeSongList(name, link - 4, s)      
        #print("Chord progression for song", chordProgress)
        
def changePram(inc): # where editPrameter = sustain, voice, capo, MIDI channel
    global sustainTime, voice, capo, channel 
    pramInc = [100, 1, 1, 1]
    pramLim = [6000, 127, 8, 15]
    pramLow = [100, 0, -8, 0 ]
    s = setOffsets[currentSet]
    inc = inc * pramInc[editParameter]
    if editParameter == 0: # Sustain time
        pram = sustainTime
        pram += inc
        if pram > pramLim[editParameter] or pram < pramLow[editParameter] : return
        sustainTime = pram
    elif editParameter == 1: # voice
        pram = voice
        pram += inc
        if pram > pramLim[editParameter] or pram < pramLow[editParameter] : return
        voice = pram
        changeVoice()
    elif editParameter == 2: # capo
        pram = capo
        pram += inc
        if pram > pramLim[editParameter] or pram < pramLow[editParameter] : return
        capo = pram
    elif editParameter == 3: # MIDI channel
        pram = channel
        pram += inc
        if pram > pramLim[editParameter] or pram < pramLow[editParameter] : return
        channel = pram
 
def displayPlay(): # display for the playing mode
    oled.fill(0)
    oled.text(name,0,0)
    px = -1 ; py = 19
    chordSet = ""
    for i in range(4):
        if i == fret : px = len(chordSet) * 8 + 8 # find the position of the first letter of chord set
        chordSet += " " + chordName[chordProgress[i]]
    oled.text(chordSet, 0, 19)
    chordSet = ""    
    for i in range(4, 8):
        if i == fret : px = len(chordSet) * 8 + 8 ; py = 33
        chordSet += " " + chordName[chordProgress[i]]
    oled.text(chordSet, 0, 33)
    oled.rect(px - 3, py - 3, len(chordName[chordProgress[fret]])*8 + 6, 13, 1)
    oled.show()

def makeSongList(name, length, offset):
    global songList, firstInLine, chorusPointer
    lines = 1
    px = 2
    firstInLine = [2]
    songList = [name]
    songList.append(length)
    for chord in range(length):
        songList.append((chordName[chordProgress[chord]], px, lines))
        px += len(chordName[chordProgress[chord]])*8 + 8 # x position for next chord
        if infNum[chord] & 0x8 == 0x8:
            px = 2
            lines += 1
            firstInLine.append(chord + 3) # the number of the chord that is the first on a new display line
        if infNum[chord] & 0x4 == 0x4: # detected a chorus marker
            chorusPointer = chord
    lines -= 1
    songList.append(lines)
    #print("song list", songList)
    #print("First in line", firstInLine)
        
def displayPlaySong():
    oled.fill(0)
    oled.text(songList[0],0,0) # display name
    posY = [19, 33, 47]
    numberOfLines = songList[len(songList)-1]
    #print("chorus Pointer", chorusPointer)
    #print("number of lines in song", numberOfLines)
    #print("song pointer", songPointer)
    lineCount = 1 ; scroll = 0
    #print(songList[songPointer + 2][2])
    if songList[songPointer + 2][2] > 3: scroll = songList[songPointer + 2][2] - 3
 
    i = firstInLine[scroll] # first chord in song list to display
    #print("first chord to display", i)
    while lineCount < 4 and lineCount <= numberOfLines:
        #print("i =", i, songList[i], "scroll", scroll)
        #print("placed at X Y", songList[i][1],  posY[songList[i][2] - 1 - scroll])
        oled.text(songList[i][0], songList[i][1], posY[songList[i][2] - 1 - scroll])
        i += 1 # next chord in list
        if i >= songList[1] +2: #number of chords in song
            lineCount = 4
        else :    
            lineCount = songList[i][2] - scroll # what line of the display we are on
                           
    oled.rect(songList[songPointer +2][1] -2, posY[songList[songPointer+2][2]-1 - scroll] - 3, len(songList[songPointer+2][0])*8 + 6, 13, 1)
    oled.show()    
    #len(chordName[chordProgress[songPointer]])*
    
def displayConfig(): # display for configuration mode
    editLine = [16, 28, 39, 51]
    oled.fill(0)
    oled.text(name, 0, 0)
    oled.text("Sustain ",0, editLine[0])
    oled.text(str(sustainTime), 64, editLine[0])
    oled.text("Voice " + str(voice), 0, editLine[1])
    oled.text("Capo = "+ str(capo),0, editLine[2])
    oled.text("MIDI Ch = "+ str(channel + 1),0, editLine[3])
    oled.text("<", 112, editLine[editParameter])
    oled.line(113, editLine[editParameter] +3 , 127, editLine[editParameter] +3, 1)
    oled.show()
    
def changeVoice():
    #print("changing voice", voice, bank, "on channel", channel)
    cmd3[0] = 0xB0 | channel
    cmd3[1] = 0x00 # write bank msb
    cmd3[2] = 0x00 # always zero for General MIDI
    port.write(cmd3)
    cmd3[1] = 0x20 # LSB of bank address
    cmd3[2] = bank
    port.write(cmd3)
    cmd2[0] = 0xC0 | channel # program change
    cmd2[1] = voice # new voice number
    port.write(cmd2)

def sendNoteOn(note, vel):
    cmd3[0] = 0x90 | channel
    cmd3[1] = note
    cmd3[2] = vel
    port.write(cmd3)
    
def sendNoteOff(note, vel):
    cmd3[0] = 0x80 | channel
    cmd3[1] = note
    cmd3[2] = vel
    port.write(cmd3)

def play(toPlay): # play the string being released
    global stringStartTime, stringsPlaying, stringNotePlaying
    if stringsPlaying[toPlay] == True:
        sendNoteOff(stringNotePlaying[toPlay], 0) # turn off if still playing
    elif chordBank[chordProgress[fret]][toPlay] != 0 : 
        sendNoteOn(chordBank[chordProgress[fret]][toPlay] + capo, playVelocity[toPlay])
        stringsPlaying[toPlay] = True
        stringNotePlaying[toPlay] = chordBank[chordProgress[fret]][toPlay] + capo
        stringStartTime[toPlay] = time.ticks_ms()
            
def getStringNumber(stringNumber, stringVelocity):
    global playVelocity, lastStringVel    
    if leftHanded :
        stringNumber = 1 - stringNumber
        stringVelocity = 1 - stringVelocity    
    if abs(stringVelocity) >= 1.0 : # sometimes we get a spurious 1.0 or more for the reading
        stringVelocity = lastStringVel
        #print("vel corrected")
    toPlay = -1  
    toPlay = int(stringNumber * 7)
    if toPlay > 5 : toPlay = 5
    playVelocity[toPlay] = (int(stringVelocity * 94) + 33) & 0x7F # map to a range of volumes
    if playVelocity[toPlay] == 0 : playVelocity[toPlay] = 1 # stop a string on the edge turning note off
    lastStringVel = stringVelocity
    #print("Velocity", playVelocity[toPlay], "string", toPlay, stringVelocity )
    return toPlay

def changeChord(place):
    global fret, lastTouch, songPointer
    touch = int(place * 8)
    if touch > 7 : touch = 7
    if touch != lastTouch :
        if fileType == 0:
            fret = touch
            displayPlay()
        if fileType == 1:
            if touch == 7 : #move on to next chord in song                
                songPointer +=1
                if songPointer >= songList[1] : songPointer = 0
            elif touch == 0: # back to start of song
                songPointer = 0
            elif touch == 4 and songPointer != 0: # move back one chord
                songPointer -= 1
            elif touch == 2 and chorusPointer != -1:
                songPointer = chorusPointer
            fret = songPointer    
            displayPlaySong()
    lastTouch = touch
    time.sleep(0.01)
        
def scanPlay():
    global stringTouched
    for i in range(6):
        if stringTouched[i]:
           play(i)
           stringTouched[i] = False

def playing() : # operations in playing mode
    global stringsPlaying, stringNotePlaying, stringTouched, playMode, chords
    global strings, lastTouch
    if not playMode : # if changing to play mode display the playing screen
        playMode = True
        if fileType == 0 :displayPlay()
        else : displayPlaySong()
    chords.readTrill()
    if chords.getNumTouches() == 1 : changeChord(chords.touchLocation(0)) # only look at one touch
    elif fileType == 1 : lastTouch = -1
    strings.readTrill()
    heldDown = -1
    if strings.getNumTouches() !=0 : # see what string has been touched
        heldDown = getStringNumber(1-strings.touchLocation(0), strings.touchHorizontalLocation(0) )
        if heldDown != -1 :
            if stringTouched[heldDown] == False :
                scanPlay() # see if other strings are waiting to be played                   
                stringTouched[heldDown] = True
            elif stringsPlaying[heldDown] :
                sendNoteOff(stringNotePlaying[heldDown], 0) # 
                stringsPlaying[heldDown] = False                    
    if strings.getNumTouches() == 0 or heldDown == -1:    
        # no string held down so play all notes that have been touched
        scanPlay()
    # check if time to turn off note
    for i in range(6):
        if stringsPlaying[i] == True and time.ticks_diff(time.ticks_ms(), stringStartTime[i]) > sustainTime:    
                sendNoteOff(stringNotePlaying[i],0)
                stringsPlaying[i] = False

def get(place):
    global fret, lastTouch
    touch = int(place * 8)
    if touch > 7 : touch = 7
    if touch != lastTouch :   
        #print("fret", touch)
        fret = touch
        if fileType == 0 :displayPlay()
        else : displayPlaySong()
    lastTouch = touch

def configure():
    global chords, currentSet, editParameter
    #print("In configuration function")
    currentParameter = 0
    touch = -1
    while playPin.value() == 0:
        displayConfig()
        chords.readTrill()
        while chords.getNumTouches() != 0 and playPin.value() == 0: # wait for no touch
            chords.readTrill()
            time.sleep(0.1)                   
        while chords.getNumTouches() != 1 and playPin.value() == 0: # wait for touch
            chords.readTrill()
            time.sleep(0.1)
        touch = int(chords.touchLocation(0) * 8)
        if touch > 7 : touch = 7
        if playPin.value() != 0: touch = -1
        #print("Touch in configure", touch)
        if touch == 0:
            changePram(1)
        elif touch == 2:
            changePram(-1)
        elif touch == 4: # Move on to next parameter
            editParameter += 1
            if editParameter > 3 : editParameter = 0    
        elif touch == 7: # move on to next set
            currentSet += 1                 
            if currentSet >= sets : currentSet = 0
            #print("now have", currentSet, "of", sets, "sets")
            iniGuitar(currentSet)
            time.sleep(0.2);
    if fileType == 0 :displayPlay()
    else : displayPlaySong()
    
def main():
    global stringStartTime, lastStringVel, chords, strings, currentSet 
    loadFile()
    currentSet = 0
    iniGuitar(currentSet) # first set of parameters in config file
    if fileType == 0 :displayPlay()
    else : displayPlaySong()
    chords = PicoTrillLib(1, "bar", 0x20, 15, 14, 400000)
    chords.setPrescaler(5)
    chords.updateBaseLine()
    strings = PicoTrillLib(1, "square", 0x28, 15, 14, 400000)
    strings.setPrescaler(3) # change for other values
    strings.updateBaseLine()
    for i in range(6) : stringStartTime[i] = time.ticks_ms()
    currentTouch = -1
    lastStringVel = 38
    while(1):
        if playPin.value() :
            playing()
        else :
            configure()
                             
# Main program logic:
if __name__ == '__main__':    
    main()
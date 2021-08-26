# MIDI Hex Keys as discribed in the MagPi magizine number 109 by Mike Cook
# Save in the Pico USB file window as code.py to run automatically
import time
import random
import board
import digitalio
import os
import busio
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.program_change import ProgramChange
from encoder import IncrementalEncoder

def main():
    global keysHeld, keysHeld
    init()
    initOLED()
    chanChange(0) # set default channel
    while True:
        #time.sleep(0.5)    
        for coloum in range(0, 14):
            setMux(coloum)
            for row in range(0, 7):
                keyNumber = coloum + (row * 15)
                if col[row].value : # no key pressed                                      
                    if any( number == keyNumber for number in keysHeld):
                        #print("Keynumber", keyNumber, "found in list")
                        index = keysHeld.index(keyNumber)
                        midi.send(NoteOff(key2MIDI[keyNumber]+keysShift, 0))
                        keysHeld[index] = 74 # a nothing key
                        displayOff()
                else :        
                    if any(number == keyNumber for number in keysHeld):
                        pass # alread held down key from last pass                     
                    else : # first time a key held down has been seen
                        if mode == 0 or mode == 2: midi.send(NoteOn(key2MIDI[keyNumber] + keysShift, noteVel))
                        displayNote(keyNumber)
                        index = keysHeld.index(74) # find blank space in keysHeld list
                        keysHeld[index] = keyNumber # store note on key in the list                         
            muxAdd[3].value = True ; muxAdd[4].value = True
        checkControlkeys()
        checkEncoder()

def init():
    global key2MIDI, midi, muxAdd, col, lastCkeys, keysHeld, pecussion
    global octave, keyName, voiceGroups, gmVoices, mode, keysShift, octShift
    global noteVel, chan, rotaryEncoder, pushSwitch, encoderTop, lastEncoder
    midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
    key2MIDI = [81, 78, 82, 79, 83, 80, 84, 81, 36, 82, 83, 83, 38, 84, # 13
                128, 74, 71, 75, 72, 76, 73, 77, 74, 78, 75, 79, 76, 80, # 27
                77, 129, 67, 64, 68, 65, 69, 66, 70, 67, 71, 68, 72, 69, # 41
                73, 71, 130, 60, 57, 61, 58, 62, 59, 63, 60, 64, 61, 65, # 55
                62, 66, 63, 132, 53, 50, 54, 51, 55, 52, 56, 53, 57, 54, # 69
                58, 55, 59, 56, 133, 46, 43, 47, 44, 48, 45, 49, 37, 50, # 83
                47, 51, 48, 52, 49, 135, 39, 36, 40, 37, 41, 38, 42, 39, # 97
                43, 40, 44, 41, 45, 42]
    
    octave = [4, 4, 4, 4, 4, 4, 5, 4, 1, 4, 1, 4, 1, 5, 0, 4, 3, 4, 4, 4,
              4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
              4, 3, 4, 3, 0, 3, 2, 3, 2, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 0,
              2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 2,
              1, 2, 1, 2, 1, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1]
    
    keyName = ["A", "F#", "Bb", "G", "B", "G#", "C", "A", "C", "Bb", "C#",
               "B", "D", "C", "Left", "D", "B", "Eb", "C", "E", "C#", "F",
               "D", "F#", "Eb", "G", "E", "G#", "F", "Right", "G", "E", "G#",
               "F", "A", "F#", "Bb", "G", "B", "G#", "C", "A", "C#", "Bb",
               "Up", "C", "A", "C#", "Bb", "D", "B", "Eb", "C", "E", "C#", # 54
               "F", "D", "F#", "Eb", "Down", "F", "D", "F#", "Eb", "G", "E", # 65
               "G#", "F", "A", "F#", "Bb", "G", "B", "G#", "Nh1", "Bb", "G", # 76
               "B", "G#", "C", "A", "C#", "Bb", "D", "B", "Eb", "C", "E", "C#", # 88
               "Nh2", "Eb", "C", "E", "C#", "F", "D", "F#", "Eb", "G", "E", # 99
               "G#", "F", "A", "F#"]
    
    # percussion names start at note number 35 and go to note number 81 - 10 char limit
    pecussion = ["Bass Drum", "Bass Drum1", "Side Stick", "Acou Snare",
                 "Hand Clap", "Elec Snare", "LowFlo Tom", "Clo Hi Hat",
                 "Hi Flo Tom", "Ped Hi-Hat", "Low Tom", "OpenHi-Hat", "Low-MidTom",
                 "Hi-Mid Tom", "Crash Cym1", "High Tom", "Ride Cymb1", "Chin Cymb",
                 "Ride Bell", "Tambourine", "Splash Cym", "Cowbell", "Crash Cym2",
                 "Vibraslap", "Ride Cymb2", "Hi Bongo", "Low Bongo", "MuteHiCong",
                 "OpenHiCong", "Low Conga", "Hi Timbale", "LowTimbale", "High Agogo",
                 "Low Agogo", "Cabasa", "Maracas", "Sh Whistle", "Long Whist",
                 "ShortGuiro", "Long Guiro", "Claves", "Hi Wood Bk", "LowWood Bk",
                 "Mute Cuica", "Open Cuica", "Mute Tri", "Open Tri"]
    
    voiceGroups = ["Piano", "Chromatic Percussion", "Organ", "Guitar", "Bass",
                   "Strings", "Ensemble", "Brass", "Reed", "Pipe", "Synth Lead",
                   "Synth Pad", "Synth Effects", "Ethnic", "Percussive", "Sound Effects"]   
    gmVoices = ["Acoustic Grand", "Bright Acoustic", "Electric Grand", "Honky-tonk Piano",
                "Electric Piano 1", "Electric Piano", "Harpsichord", "Clavi", "Celesta",
                "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells",
                "Dulcimer", "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
                "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoutic Guitar nylon",
                "Acoustic Guitar steel", "Elecric Guitar jazz", "Electric Guitar clean", "Electric Guitar muted",
                "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics", "Acoustic Bass",
                "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass",
                "Synth Bass 1", "Synth Bass", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings",
                "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensembles 1", "String Ensembles",
                "Synth Strings 1", "Synth Strings", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
                "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1",
                "Synth Brass", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn",
                "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi",
                "Whistle", "Ocarina", "Square Lead 1", "Saw Lead", "Calliope Lead", "Chiff Lead", "Charang Lead",
                "Voice Lead", "Fifths Lead", "Bass + Lead", "New Age (Pad 1)", "Warm Pad (Pad)", "Polysynth (Pad)",
                "Choir (Pad)", "Bowed (Pad)", "Metallic (Pad)", "Halo (Pad)", "Sweep (Pad)", "Rain (FX 1)",
                "Sound Track (FX)", "Crystal (FX)", "Atmosphere (FX)", "Brightness (FX)", "Goblins (FX)",
                "Echoes (FX)", "Sci-fi (FX)", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag Pipe", "Fiddle",
                "Shanai", "Tinkle Bell", "Agogo", "Pitched Percussion", "Woodblock", "Taiko Drum", "Melodic Tom",
                "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet",
                "Telephone Ring", "Helicopter", "Applause", "Gunshot"]
    muxAdd = [board.GP16] * 5
    muxAddPins = [board.GP16, board.GP17, board.GP18, board.GP19, board.GP20]
    for i in range(0,5):
        muxAdd[i] = digitalio.DigitalInOut(muxAddPins[i])
        muxAdd[i].direction = digitalio.Direction.OUTPUT
    col = [board.GP2] * 7
    colPins = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8]
    for i in range(0,7):
        col[i] = digitalio.DigitalInOut(colPins[i])
        col[i].switch_to_input(pull=digitalio.Pull.UP)        
    keyNumber = 127
    pushSwitch = digitalio.DigitalInOut(board.GP12)
    pushSwitch.switch_to_input(pull=digitalio.Pull.UP)
    
    lastCkey = 0
    lastCkeys = [4, 4, 4, 4]
    keysHeld = [74] * 10 # 74 can not be produced by hex keys being held
    mode = 0 # 0 for play mode 1 for edit mode
    keysShift = 0
    octShift = 0    
    chan = 0 # defult to channel 1
    rotaryEncoder = IncrementalEncoder(board.GP10, board.GP11, 0) # for play mode
    rotaryEncoder.setCounter(90)
    noteVel = 90
    encoderTop = [127, 15, 127]
    lastEncoder = 90
    
def checkControlkeys():
    global lastCkeys, lastEncoder
    setMux(14)
    for row in range(0, 4):
        cKey = col[row].value
        if cKey != lastCkeys[row] :
            lastCkeys[row] = cKey
            if not cKey :
                if mode == 0:
                    if row == 3 : octaveShift(-1)
                    if row == 2 : octaveShift(1)
                    if row == 1 : chanChange(-1)
                    if row == 0 : chanChange(1)
                if mode == 1:    
                    if row == 3 : changeMode(2) # down
                    if row == 2 : changeMode(0) # up
                if mode == 2:
                    if row == 3 : changeVoice(rotaryEncoder.value) # down
                    if row == 2 :
                        #print("rotaryEncoder.value", rotaryEncoder.value, "new value",  int(rotaryEncoder.value / 8)) 
                        lastEncoder = int(rotaryEncoder.value / 8)
                        rotaryEncoder.setCounter(lastEncoder)
                        setupList(lastEncoder, voiceGroups)
                        changeMode(1) # up
                    if row == 1 : chanChange(-1)
                    if row == 0 : chanChange(1)
                
    muxAdd[3].value = True ; muxAdd[4].value = True  

def setMux(colN):
    muxAdd[3].value = True ; muxAdd[4].value = True
    if colN & 1 : muxAdd[0].value = True
    else: muxAdd[0].value = False
    if colN & 2 : muxAdd[1].value = True
    else: muxAdd[1].value = False
    if colN & 4 : muxAdd[2].value = True
    else: muxAdd[2].value = False
    if colN & 8 : muxAdd[3].value = False
    else: muxAdd[4].value = False        
    
def initOLED():
    global display, playGroup, title_text, note_text, chan_text, shift_text, vel_text
    global selectLine, select_title, selectGroup, pecus_display, note_display, smNote_text
    WIDTH = 128
    HEIGHT = 64
    CENTER_X = int(WIDTH/2)
    CENTER_Y = int(HEIGHT/2)

    displayio.release_displays()

    SDA = board.GP14
    SCL = board.GP15
    i2c = busio.I2C(SCL, SDA)

    if(i2c.try_lock()):
        i2c.unlock()
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    
    # Make the display context
    splash = displayio.Group(max_size=10)
    NUM_OF_COLOR = 2
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, NUM_OF_COLOR)
    bitmap_palette = displayio.Palette(NUM_OF_COLOR)
    bitmap_palette[0] = 0x000000
    bitmap_palette[1] = 0xFFFFFF
    '''
    tileGrid = displayio.TileGrid(bitmap,
                                  pixel_shader=bitmap_palette,
                                  x=0, y=0)
    splash.append(tileGrid)
    '''    
    # Define the splash screen
    text_group1 = displayio.Group(max_size=10, scale=3, x=0, y=30)
    text1 = "HexKeys"
    text_area1 = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF)
    text_group1.append(text_area1)
    splash.append(text_group1)
    
    text_group2 = displayio.Group(max_size=13, scale=1, x=34, y=55)
    text2 = "By Mike Cook"
    text_area2 = label.Label(terminalio.FONT, text=text2, color=0xFFFFFF)
    text_group2.append(text_area2)
    splash.append(text_group2)
    
    display.show(splash)    
    time.sleep(1.0) # show the splash screen for a short time
    
    # Define the select screen for picking a MIDI voice This is used when mode = 1 or 2
    selectLine =[" "] * 5
    selectGroup = displayio.Group(max_size=10)
    hilightRect = Rect(0, 36, 128, 13, fill=0xFFFFFF)
    selectGroup.append(hilightRect)
    
    text_select = displayio.Group(max_size=21, scale=1, x=0, y=6)
    select_title = " Change Voice - Group"
    select_title = label.Label(terminalio.FONT, text=select_title, color=0xFFFFFF)
    text_select.append(select_title)
    selectGroup.append(text_select)

    text_line1 = displayio.Group(max_size=21, scale=1, x=0, y=19)
    select_line1 = " "    
    select_line1 = label.Label(terminalio.FONT, text=select_line1, color=0xFFFFFF)
    selectLine[0] = select_line1
    text_line1.append(select_line1)
    selectGroup.append(text_line1)

    text_line2 = displayio.Group(max_size=21, scale=1, x=0, y=29)
    select_line2 = " "
    select_line2 = label.Label(terminalio.FONT, text=select_line2, color=0xFFFFFF)
    selectLine[1] = select_line2
    text_line2.append(select_line2)
    selectGroup.append(text_line2)
    
    text_line3 = displayio.Group(max_size=21, scale=1, x=0, y=42)
    select_line3 = voiceGroups[0]
    select_line3 = label.Label(terminalio.FONT, text=select_line3, color=0x0)
    selectLine[2] = select_line3
    text_line3.append(select_line3)
    selectGroup.append(text_line3)

    text_line4 = displayio.Group(max_size=21, scale=1, x=0, y=54)
    select_line4 = voiceGroups[1]
    select_line4 = label.Label(terminalio.FONT, text=select_line4, color=0xFFFFFF)
    selectLine[3] = select_line4
    text_line4.append(select_line4)
    selectGroup.append(text_line4)
    
    text_line5 = displayio.Group(max_size=21, scale=1, x=0, y=63)
    select_line5 = voiceGroups[2]
    select_line5 = label.Label(terminalio.FONT, text=select_line5, color=0xFFFFFF)
    selectLine[4] = select_line5
    text_line5.append(select_line5)
    selectGroup.append(text_line5)

    # Define the play screen    
    playGroup = displayio.Group(max_size=10)
    text_group2 = displayio.Group(max_size=21, scale=1, x=0, y=6)
    title_text1 = "      Play Mode"
    title_text = label.Label(terminalio.FONT, text=title_text1, color=0xFFFFFF)
    text_group2.append(title_text)
    playGroup.append(text_group2)
        
    text_group4 = displayio.Group(max_size=5, scale=1, x=0, y=55)
    chan_text = "Ch 1"
    chan_text = label.Label(terminalio.FONT, text=chan_text, color=0xFFFFFF)
    text_group4.append(chan_text)    
    playGroup.append(text_group4)

    text_group5 = displayio.Group(max_size=7, scale=1, x=34, y=55)
    shift_text = "Shift 0"
    shift_text = label.Label(terminalio.FONT, text=shift_text, color=0xFFFFFF)
    text_group5.append(shift_text)    
    playGroup.append(text_group5)

    text_group6 = displayio.Group(max_size=7, scale=1, x=85, y=55)
    vel_text = "Vel 64"
    vel_text = label.Label(terminalio.FONT, text=vel_text, color=0xFFFFFF)
    text_group6.append(vel_text)    
    playGroup.append(text_group6)
    
    note_display = displayio.Group(max_size=5, scale=3, x=20, y=30)
    note_text = " "
    note_text = label.Label(terminalio.FONT, text=note_text, color=0xFFFFFF)
    note_display.append(note_text)    
    #playGroup.append(note_display)
    
    pecus_display = displayio.Group(max_size=22, scale=2, x=0, y=30)
    smNote_text = " "
    smNote_text = label.Label(terminalio.FONT, text=smNote_text, color=0xFFFFFF)
    pecus_display.append(smNote_text)
    playGroup.append(pecus_display)
    
    playGroup.pop()
    playGroup.append(note_display)   
    
def displayNote(number):
    global note_text, smNote_text
    if mode == 0:
        if chan == 9: # percussion channel
            num = key2MIDI[number] + keysShift
            #print("number is", number, "keysShift", keysShift, "num", num)
            if num >= 35 and num <= 81:
                smNote_text.text = pecussion[num - 35]
            else:
                smNote_text.text = "--------------------"
        else :
            note_text.text = keyName[number]+" "+str(octave[number]+octShift)
        display.show(playGroup)
    
def displayOff(): # if a key is still held show one of those
    global note_text, smNote_text
    if mode == 0:
        if chan == 9:
            smNote_text.text = " "
        else:    
            note_text.text = " "
        held = -1
        for i in range(0, len(keysHeld)):
            if keysHeld[i] != 74 :
               held = keysHeld[i]
        if held != -1 :
            displayNote(held)
        else :    
            display.show(playGroup)

def octaveShift(direction):
    global keysHeld, octShift, keysShift, shift_text
    for i in range(0, len(keysHeld)):
        if keysHeld[i] != 74 : # turn off all notes being held
            midi.send(NoteOff(key2MIDI[keysHeld[i]]+keysShift, 0))
            keysHeld[i] = 74
    octShift += direction    
    if octShift > 3 or octShift < -2 :
        octShift -= direction
    keysShift = octShift * 12
    shift_text.text = "Shift " + str(octShift)
    note_text.text = " "
    display.show(playGroup)

def chanChange(amount):
    global chan, chan_text, midi, select_title, playGroup
    chan += amount
    if chan > 15 : chan = 15
    if chan < 0 : chan = 0
    chan_text.text = "Ch "+ str(chan + 1)
    midi = adafruit_midi.MIDI(
        midi_in=usb_midi.ports[0], in_channel=chan, midi_out=usb_midi.ports[1], out_channel=chan )
    if chan == 9: # percussion channel
            playGroup.pop()
            playGroup.append(pecus_display)
            #print("percussion display activated")
    else :
            playGroup.pop()
            playGroup.append(note_display)


    if mode == 0:
       display.show(playGroup)
    elif mode == 2:
       select_title.text = " Change Voice - Ch "+str(chan + 1) 
       display.show(selectGroup) 
 
def checkEncoder():
    global rotaryEncoder, vel_text, noteVel, lastEncoder   
    value = rotaryEncoder.value   
    if lastEncoder != value:
        if value < 0 :
            rotaryEncoder.setCounter(0)
            value = 0
        if value > encoderTop[mode] :
            rotaryEncoder.setCounter(encoderTop[mode])
            value = encoderTop[mode]
        lastEncoder = value
        if mode == 0: # change note velocity
            noteVel = value
            vel_text.text = "Vel "+ str(noteVel)
            display.show(playGroup)
        if mode == 1: # setup group list
            setupList(value, voiceGroups)
        if mode == 2: # setup voice list
            setupList(value, gmVoices)
    if pushSwitch.value == 0 and mode == 1 : changeMode(2)        
    if pushSwitch.value == 0 and mode == 0 : rotaryEncoder.setCounter(0) ; allOff() ; changeMode(1)
    if pushSwitch.value == 0 and mode == 2 : changeVoice(value)
            
def setupList(value, group):
    global selectLine
    selectLine[2].text = group[value]
    if value -2 >= 0:
        selectLine[0].text = group[value -2]
    else :    
        selectLine[0].text = " "
    if value -1 >= 0:
        selectLine[1].text = group[value -1]
    else :    
        selectLine[1].text = " "        
    if encoderTop[mode] - value > 0:
        selectLine[3].text = group[value +1]
    else :    
        selectLine[3].text = " "
    if encoderTop[mode] - value > 1:
        #print("encoderTop[mode] - value",encoderTop[mode], value)
        selectLine[4].text = group[value +2]
    else :    
        selectLine[4].text = " "
    display.show(selectGroup)
    
def changeMode(newMode):
    global select_title, mode, rotaryEncoder
    mode = newMode
    if newMode == 1 :
        select_title.text = " Change Voice - Group"
        rotaryEncoder.setScale(2) # for select mode
        #rotaryEncoder.setCounter(0)
        display.show(selectGroup)
        while pushSwitch.value == 0:
            pass
        
    elif newMode == 0 :
        rotaryEncoder.setScale(0) # for play mode
        rotaryEncoder.setCounter(noteVel)
        display.show(playGroup)
        
    elif newMode == 2 : #change to display
        select_title.text = " Change Voice - Ch "+str(chan +1)
        rotaryEncoder.setCounter(rotaryEncoder.value * 8)
        setupList(rotaryEncoder.value, gmVoices)
        display.show(selectGroup)        
        while pushSwitch.value == 0:
            pass

def changeVoice(voiceNumber):
    #print("change voice to number", voiceNumber, gmVoices[voiceNumber])
    midi.send(ProgramChange(voiceNumber))   #chan
    while pushSwitch.value == 0:
        pass

def allOff():
    #print("turn all notes off")
    # send CC message 123 (all notes off) value 0 - to all channels
    chanPreserve = chan
    for c in range(0,16):
        midi = adafruit_midi.MIDI(
        midi_in=usb_midi.ports[0], in_channel=c, midi_out=usb_midi.ports[1], out_channel=c )
        midi.send(ControlChange(123, 0))
    # restore current channel       
    midi = adafruit_midi.MIDI(
        midi_in=usb_midi.ports[0], in_channel=chanPreserve, midi_out=usb_midi.ports[1], out_channel=chanPreserve )    
     
    
# Main program logic:
if __name__ == '__main__':    
    main()    
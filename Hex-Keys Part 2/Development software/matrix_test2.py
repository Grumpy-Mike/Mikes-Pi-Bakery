import time
import board
import digitalio

print("Testing the matrix pins only one button pressed at a time")
print("short out one row and coloum to see key number")
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
    
lastKey = 999

keyName =["A5", "F#5", "Bb5", "G5", "B5", "G#5", "C6", "A5", "C2", "Bb5", "C#2", "Bb5",
          "D2", "C6", "Left", "D5", "B4", "Eb5", "C5", "E5", "C#5", "F5", "D5", "F#5",
          "Eb5", "G5", "E5", "G#5", "F5", "Right", "G4", "E4", "G#4", "F4", "A4", "F#4",
          "Bb4", "G4", "B4", "G#4", "C5", "A4", "C#5", "Bb4", "Up", "C4", "A3", "C#4",
          "Bb3", "D4", "B3", "Eb4", "C4", "NH1", "C#4", "F4", "D4", "F#4", "Eb4", "Down",
          "F3", "D3", "F#3", "Eb3", "G3", "E3", "G#3", "F3", "A3", "F#3", "Bb3", "G3", "B3",
          "G#3", "Nh2", "Bb2", "G2", "B2", "G#2", "C3", "A2", "G#3", "Bb2", "D3", "B2",
          "Eb3", "NH3", "E3", "C#3", "Nh4", "Eb2", "C2", "E2", "C#2", "F2", "D2", "F#2",
          "Eb2", "G2", "C#2", "G#2", "F2", "A2", "F#2" ]
while True:
    #time.sleep(0.5)    
    for coloum in range(0, 15):
        muxAdd[3].value = True ; muxAdd[4].value = True
        if coloum & 1 : muxAdd[0].value = True
        else: muxAdd[0].value = False
        if coloum & 2 : muxAdd[1].value = True
        else: muxAdd[1].value = False
        if coloum & 4 : muxAdd[2].value = True
        else: muxAdd[2].value = False
        if coloum & 8 : muxAdd[3].value = False
        else: muxAdd[4].value = False        
        time.sleep(0.001)
        for row in range(0, 7):
            keyNumber = coloum + (row * 15)
            if not col[row].value and keyNumber != lastKey:
                #print("coloum", coloum, "row", row)
                lastKey = keyNumber
                print("key ", keyName[keyNumber])
                time.sleep(0.1)
        muxAdd[3].value = True ; muxAdd[4].value = True       
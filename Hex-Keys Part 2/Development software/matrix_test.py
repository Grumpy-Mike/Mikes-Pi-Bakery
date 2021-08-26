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

while True:
    time.sleep(0.5)    
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
                print("coloum", coloum, "row", row)
                lastKey = keyNumber
                print("this is key number", keyNumber)
                time.sleep(0.4)
        muxAdd[3].value = True ; muxAdd[4].value = True       
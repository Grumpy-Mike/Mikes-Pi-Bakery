#! python
import pyautogui, sys, time
print('Press Ctrl-C to quit.')
print " screen size ", pyautogui.size()
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print positionStr,
        print '\b' * (len(positionStr) + 2)
        sys.stdout.flush()
        time.sleep(0.5)
except KeyboardInterrupt:
    print '\n'

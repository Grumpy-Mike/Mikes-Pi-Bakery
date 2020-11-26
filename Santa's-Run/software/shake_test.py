# Shake test for one shakers
# By Mike Cook - November 2020

import RPi.GPIO as io

leftCount = 0
rightCount = 0

def shake(pin):
    global leftCount
    print("shake OK")
    leftCount += 1
    if leftCount > 10 :
        print("Shaker test done")
        io.remove_event_detect(2)

print("Test shakers, shake now")
print("Press return when tests is finished")
io.setwarnings(False)
io.setmode(io.BCM)
io.setup(2, io.IN)
io.add_event_detect(2, io.FALLING, callback = shake, bouncetime=30)

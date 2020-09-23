#!/usr/bin/env python3
# Free draw by Mike Cook August 2020
# prints out stream of points when touching the screen
# using external CalTap class

from caltap import CalTap
tap = CalTap()
print("touch anywhere")
while 1:
    pos = tap.getRaw()
    if pos[3] > 0 :
        print("x",pos[0], " y", pos[1], " z", pos[2])

#!/usr/bin/env python3
# coding=utf-8
# Colour Simon
# By Mike Cook March 2019

import time, random, os
from pylgbst import *
#import pylgbst
from pylgbst.movehub import MoveHub
from espeak import espeak  # sudo apt install python3-espeak
espeak.set_voice = 'en'

random.seed()
shutDown = False
lastColour = 255 ; updateColour = 0
maxLength = 25 # maximum sequence before we decide you are cheating
sequence = [ random.randint(0,3) for c in range(0,maxLength)] 
maxFails = 3 # number of fails before game ends
playingColours = ["blue","green","yellow","red","white","black"]
translateColours = [5,5,5,0,5,1,5,2,5,3,4]
playingToLego = [3,5,7,9,10,0]

def main():
  global shutDown, movehub
  print("Colour tile Simon - press the green hub button to connect")
  conn=get_connection_auto()
  print("Trying to connect Hub")
  try:
    movehub = MoveHub(conn)
    print("Hub now connected - press Green button to end")
    init()
    espeak.synth("Colour Simon game")
    time.sleep(1)
    while not shutDown:
      fail = 0  # number of fails
      #generate new sequence
      for c in range(0,maxLength):
         sequence[c] = random.randint(0,4) #use five colours  
      far = 2
      while fail < maxFails and not shutDown: # number of fail attempts before reset
         print("a sequence of length",far)
         saySeq(far)
         if getSeq(far) != -1 and not shutDown:# if entered sequence is correct  
            far = far + 1            
            if far <= maxLength:
               espeak.synth("yes")
               print("Yes - now try a longer one")
               time.sleep(1)
               espeak.synth("adding one more")
               time.sleep(1)
            fail = 0 # reset number of fails
         else:
             if not shutDown:
                fail = fail +1
                print("Wrong",fail,"fail")
                if fail < maxFails:
                   espeak.synth("no")
                   print("try that one again")
                   espeak.synth("try that one again")
                else :
                  print("maximum tries exceeded")
                  espeak.synth("maximum tries exceeded")
                  time.sleep(2)
                  espeak.synth("your score is")
                  time.sleep(1)
                  espeak.synth(str(far- 1))
                time.sleep(1.5)
         if far > maxLength and not shutDown:
            print("Well done Master Mind")
            espeak.synth("this is too easy for you")
            shutDown = True
      if not shutDown:
         espeak.synth("Game over")
         print("Game over - Your score is",far-1)
         print("Try again")
         time.sleep(2.0)
      else:
        espeak.synth("closing down  good bye")
      
  finally:
    print("shutting down")
    movehub.button.unsubscribe(call_button)
    movehub.color_distance_sensor.unsubscribe(callback_colour)
    conn.disconnect()

def init():
   movehub.led.set_color(playingToLego[5])
   movehub.button.subscribe(call_button)
   movehub.color_distance_sensor.subscribe(callback_colour, granularity=0)

def getTile():
    global lastColour, updateColour
    while updateColour < 3 :
      if shutDown:
        return 5
    #print("colour",playingColours[correctColour(lastColour)])
    updateColour = 0
    espeak.synth(playingColours[correctColour(lastColour)])
    movehub.led.set_color(playingToLego[correctColour(lastColour)]) # turn on LED
    return correctColour(lastColour)     
      
def saySeq(length):
    for num in range(0,length):
      espeak.synth(playingColours[sequence[num]])
      movehub.led.set_color(playingToLego[sequence[num]])
      time.sleep(0.8) # time between saying colour
      movehub.led.set_color(playingToLego[5])
      time.sleep(0.5)

def getSeq(length):
    movehub.led.set_color(playingToLego[5]) # turn off LED
    espeak.synth("Now you try")
    print("Now you try")
    for press in range(0, length):
       if shutDown:
         return 1
       attempt = getTile()
       movehub.led.set_color(playingToLego[5]) # turn off LED
       if attempt != sequence[press]:
          time.sleep(0.8)
          return -1
    return 1

def callback_colour(colour, distance): 
    global lastColour, updateColour
    if distance <= 1.2:      
       if colour != 255 and lastColour != colour and colour!= 0: # ignore no colour
         updateColour += 1
         #print(colour)
         if updateColour > 2 :
             lastColour = colour
       if colour == 255 :
           lastColour = 255
    else:
       lastColour = 255

def correctColour(colour): # translate LEGO colours to playing colours
    if colour == 255:
      correctColour = 5 # black
    else:  
      correctColour = translateColours[colour]
    return correctColour

def call_button(is_pressed):
   global shutDown, updateColour
   if not is_pressed :
     print("Closing Down")
     shutDown = True
     updateColour = 0
   
if __name__ == '__main__':
    main()

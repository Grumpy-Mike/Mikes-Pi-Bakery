#!/usr/bin/env python
"""
SkyWriter Hat Web Browser Driver
By Mike Cook March 2016
"""
import time
import random
import os, sys
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import pyautogui
import skywriter
import signal

#locationd in screen to click
# on a 1024 X 768 VGA monitor
browserIcon = (112,19)
newTab = (957,80)
refreshPage = (912,80)
typeURL = (697,80);
tabBar = 118
tabOffset = 105
tabIncrement = 200

sitesfile = open("/home/pi/MagPi Projects/MagicMirror/sites.txt","r")
sites = list()
numberOfPages = 0
for line in sitesfile.readlines():
        sites.append(line)
        numberOfPages +=1
sitesfile.close()
numberOfPages -=1
increment = 0
scroll = 0
visited = 0
air_value = 0

def main():
    global increment,numberOfPages, visited, scroll, air_value
    setupBrowser()
    print "number of pages in the file ",numberOfPages
    while True :
       while increment == 0 and scroll == 0 and air_value < 500:
               time.sleep(0.5)
       if increment != 0 :
          showNewTab()
       if scroll !=0 :
          scrollPage()
       if air_value >=500:
          refreshAll()     

def refreshAll():
   global air_value
   for page in range(0,numberOfPages):
      xClick = tabOffset + (tabIncrement * page)
      pyautogui.click(x=xClick,y=tabBar)
      time.sleep(0.4)
      pyautogui.click(x=refreshPage[0],y=refreshPage[1])
      time.sleep(0.8)  
   air_value = 0 
   
def scrollPage():
   global scroll     
   screenWidth, screenHeight = pyautogui.size()
   pyautogui.moveTo(screenWidth/2, screenHeight /2)
   time.sleep(0.2)
   pyautogui.scroll(scroll * 5)
   print"scroll ",scroll  
   scroll = 0
    
def showNewTab():
    global increment, visited    
    visited += increment
    if visited >= numberOfPages :
       visited = 0
    if visited < 0 :
       visited = numberOfPages -1
    increment = 0
    # click on the appropiate tab
    xClick = tabOffset + (tabIncrement * visited)
    print"tab ",visited," location ",xClick
    pyautogui.click(x=xClick,y=tabBar)
       
def setupBrowser():
    global numberOfPages
    pyautogui.doubleClick(x=browserIcon[0],y=browserIcon[1])
    time.sleep(3.0) # let the browser open up
    pyautogui.click(x=typeURL[0],y=typeURL[1])
    pyautogui.typewrite(sites[0]+"\n", interval= 0.0)
    time.sleep(1.0)
    for page in range(1,numberOfPages):
        pyautogui.click(x=newTab[0],y=newTab[1])
        pyautogui.click(x=typeURL[0],y=typeURL[1])
        time.sleep(0.5)
        print " opening up ",sites[page]
        pyautogui.typewrite(sites[page]+"\n", interval= 0.0)
        time.sleep(1.0)
    pyautogui.click(x=tabOffset,y=tabBar)    
        
@skywriter.flick()
def flick(start,finish):
  global increment, scroll      
  print("Got a sensor flick!", start, finish)
  if start == "east" and finish == "west":
     increment = -1
  if start == "west" and finish == "east" :
     increment = 1     
  if start == "north" and finish == "south":
     scroll = -1
  if start == "south" and finish == "north" :
     scroll = 1     
  
@skywriter.airwheel()
def spinny(delta):
  global air_value
  air_value += abs(delta)
  print("Airwheel:", air_value)
       
@skywriter.double_tap()
def doubletap(position):
  print"Double tap! clocsing down"
  os.system("sudo shutdown -h now")
            
if __name__ == '__main__':
    main()   

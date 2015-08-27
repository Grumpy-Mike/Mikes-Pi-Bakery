#!/usr/bin/env python
# Video sequencer with track bars
# and multi pixel sampling
import time, pygame, pickle
import os, sys, math, copy
import cv2

pygame.init()                   # initialise pygame
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=4, buffer=512)

pygame.event.set_allowed(None)
samples =["clap","closedhat","cowbell","crash","hitom","lotom"]
colours = ["Red","Orange","Yellow","Green","Blue","Magenta"]
maxCol = 6
seqSound = [ pygame.mixer.Sound("sounds/"+samples[sound]+".wav")
                  for sound in range(0,maxCol)]

cv2.namedWindow("Video Sequencer", cv2.CV_WINDOW_AUTOSIZE)
camera_index = 0
capture = cv2.VideoCapture(camera_index)
if not capture.isOpened():
    capture.open(camera_index)    
hList = [ 0.0 for h in range (0,64)]
cList = [ 0.0 for c in range (0,64)]
nextNote = time.time()
cromaThresh = 0.23 # threshold for a colour
def track_mouse(event,x,y,flags,param):
    pass
cv2.setMouseCallback("Video Sequencer",track_mouse)

def main():
 global capture,samplePoint
 f = open('grid16x4.txt','r') # change to use another points file
 samplePoint = pickle.load(f)
 f.close()
 print"type Esc to quit - d to save colours to a CSV file and quit"
 for c in range(0,maxCol):
    print colours[c],"for",samples[c] 
 cv2.createTrackbar('BPM',"Video Sequencer",120,200,nothing)
 switch = '0 : Stop \n1 : Run'
 cv2.createTrackbar(switch,"Video Sequencer",0,1,nothing)
 startTime = time.time() + 3
 while startTime > time.time(): # let web cam's AGC settle
    ret, frame = capture.read()
    cv2.imshow("Video Sequencer", frame)
    c = cv2.waitKey(1)

 while True:
    ret = True
    for i in range (0,5) : #read off 5 frames
      ret, frame = capture.read()
    points(frame)
    cv2.imshow("Video Sequencer", frame)
    getKey()
    if cv2.getTrackbarPos(switch,"Video Sequencer") == 1 :
       soundOut(frame)
       
def getKey():
        k = cv2.waitKey(1)& 0xFF
        if k == 27:
            terminate(False)
        if k == ord('d'):
            terminate(True)        

def soundOut(frame):
    global nextNote
    bpm = 60.0 / float(cv2.getTrackbarPos('BPM',"Video Sequencer"))
    if bpm > 2.0:
      bpm = 2.0
    for i in range(0,16):
        temp = cv2.copyMakeBorder(frame,0,0,0,0,1)
        cv2.line(temp,samplePoint[i],samplePoint[i+16],(0,255,0),3)
        cv2.line(temp,samplePoint[i+16],samplePoint[i+32],(0,255,0),3)
        cv2.line(temp,samplePoint[i+32],samplePoint[i+48],(0,255,0),3)
        while nextNote > time.time() :
            pass
        nextNote = time.time() + bpm
        cv2.imshow("Video Sequencer", temp)
        getKey()
        for j in range(0,4):
          index = i + (j*16)
          if cList[index] > cromaThresh :
             seqSound[getColour(hList[index])].play()
                
def nothing(x): #dummy call back function for track bars
    pass

def output(): # CSV format
  print"Saving colours to file - colours.csv"
  with open('colours.csv','w') as f:
     f.write("Hole, Hue, Croma, Colour \n")
     for c in range(0,16):
       f.write("\n")  
       for r in range(0,4):
          i=(r*16) + c
          entry = str(i)+ ", "+"%.2f" % hList[i]
          f.write(entry+", ")
          entry = "%.2f" % cList[i]
          f.write(entry+", ")
          if cList[i] > cromaThresh :
             f.write(describeColour(hList[i])+"\n")
          else :
             f.write("neutral \n")
  f.close()
   
def getColour(h):
    colour = -1
    if h < 1 or h > 340:
        colour = 0
    if h>1 and h< 30:
        colour = 1
    elif h>30 and h< 90 :
        colour = 2
    elif h > 90 and h < 190 :
        colour = 3
    elif h> 190 and h< 300 :
        colour = 4
    elif h> 300 and h < 340 :
        colour = 5
    return colour    
            
def describeColour(h):
    colourNumber = getColour(h)
    if colourNumber == -1:
       colour = str(h)+" is unknown"
    else:
       colour = colours[colourNumber]
    return colour

def points(frame): # outline sample area and get the colours        
    for point in range(0,64):
      surround(samplePoint[point][0],samplePoint[point][1] ,(0,0,0),frame,point)
         
def surround(x, y, col, frame, place):
    getCol(x,y, frame, place)    
    frame[y, x-2] = col
    frame[y+2,x-2] = col
    frame[y-2,x-2] = col
    frame[y+2,x,] = col
    frame[y-2,x] = col            
    frame[y,x+2] = col
    frame[y+2,x+2] = col
    frame[y-2,x+2] = col
    
def getCol(x,y, frame,place):
    global hList,cList
    bt = rt = gt = 0
    m = 255.0 * 9.0
    for ox in range(-1,2):
       for oy in range(-1,2):
          blue, green, red = frame[y+oy,x+ox]
          bt += blue
          gt += green
          rt += red 
    r = float(rt) / m # normalise colours
    g = float(gt) / m
    b = float(bt) / m
    alp = 0.5*(2*r - g - b)
    bet = 0.866*(g - b)
    hList[place] = math.degrees(math.atan2(bet,alp))
    if hList[place] <0 :
        hList[place] = 360 + hList[place]
    cList[place] = math.sqrt(alp * alp + bet * bet)
    
def terminate(debug): # close down the program
    if debug :
       output() # colours to a csv file
    print ("Closing down please wait")
    pygame.quit() # close pygame
    capture.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    os._exit(1)
        
if __name__ == '__main__':    
    main()
    

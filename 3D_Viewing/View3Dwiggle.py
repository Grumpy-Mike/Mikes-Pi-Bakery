#View3D - wiggle image show, shows each image alternately
#By Mike Cook June 2015

import pygame
from pygame.locals import *
import time, os
from cStringIO import StringIO
from Tkinter import Tk
from tkFileDialog import askopenfilename

pygame.init()
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
debug = False
screen = pygame.display.set_mode((1000, 580))
pygame.display.set_caption("Wiggle 3D Slide Show")
xs, ys = screen.get_size()
back1 = pygame.Surface(screen.get_size())
back2 = pygame.Surface(screen.get_size())
errase = pygame.Surface(screen.get_size())
back1 = back1.convert()
displayTime = 4.0 # time to show each image
ditherTime = 0.2 # time to show each image
hold = False
advance = False
back = False
newList = False
Tk().withdraw()

def main():
   global newList, hold, advance, back, imageList, displayTime
   getFolder() # get the directory to show
   newList = False
   interval = time.time()
   while True:
     image = -1
     while image < len(imageList)-1 :
        checkForEvent()
        if newList:
            newList = False
            break
        image += 1
        fName = imageList[image]
        ext = fName[len(fName)-3:len(fName)]
        if ext== "mpo" or ext == "MPO":
           processMPO(fName)
           interval = time.time() + displayTime                        
        elif ext== "jpg" or ext == "JPG" or ext== "jps" or ext == "JPS":
           processSBS(fName)           
           interval = time.time() + displayTime
        if hold :
           interval = time.time() + 3600 # hold = image on for 1 hour
        left = True   
        while time.time() < interval : # wait for next slide
          checkForEvent()
          dither(left)
          left = not left
          if advance or newList:
               advance = False
               interval = time.time()
          if back :
               back = False
               image -= 2 # set picture back
               if image < 0 :
                  image = len(imageList)-1
               interval = time.time()                
             
def processMPO(name): #process a MPO image
   with open(name,'rb') as imgfile:
      imgbuf = StringIO(imgfile.read())
      image1 = pygame.image.load(imgbuf) 
   statinfo = os.stat(name)
   fileSize = statinfo.st_size
   #print"file length of",name,"is",statinfo.st_size
   with open(name,'rb') as imgfile:
      imgbuf2 = StringIO(imgfile.read())
      jpegFound=0
      startSeek = int(float(fileSize) * 0.49) #speed up search
      imgbuf2.seek(startSeek)
      #startSearch = time.time()
      while jpegFound < 1 and startSeek < fileSize:
         fb= imgbuf2.read(4)
         imgbuf2.seek(-3, os.SEEK_CUR)
         if fb == "\xff\xd8\xff\xe1":
            jpegFound +=1
         startSeek += 1   
      #print"search took",time.time() - startSearch,"at position",startSeek    
      if jpegFound == 1:      
         imgbuf2.seek(-1, os.SEEK_CUR)
         image2 = pygame.image.load(imgbuf2)
         scale_show(image1,image2)
      else :
         print "no second image found in",name
         
def processSBS(name): # process a side by side image
   rootImage = pygame.image.load(name)
   xi, yi = rootImage.get_rect().size # size of the image
   image1 = pygame.Surface(((xi/2),yi))
   image2 = pygame.Surface(((xi/2),yi))
   image1.blit(rootImage,(0,0))
   image2.blit(rootImage,(0,0),((xi/2),0,(xi/2),yi))
   scale_show(image1,image2)

def scale_show(image1,image2):
   global screen, back1
   scale = 1.0   
   xi, yi = image1.get_rect().size # size of the image
   if xi> xs or yi > ys: # scalling needed
         scalex = float(xi) / float((xs-30)) # -30 to give a gap
         scaley = float(yi) / float(ys)
         scale = scaley
         if scalex > scaley :
            scale = scalex
   newX = int(float(xi) / scale)
   newY = int(float(yi) / scale)
   #print"origional x&y ",xi,yi,"new X&Y", newX,newY
   image1 = pygame.transform.scale(image1,(newX,newY)) # scale the image
   image2 = pygame.transform.scale(image2,(newX,newY)) # scale the image
   imRec = image1.get_rect().size # get scaled size of the image
   ofsetY = (ys/2) - (imRec[1]/2 )
   ofsetX1 = (xs/2) - (imRec[0]/2)
   ofsetX2 = (3*(xs/4))- (imRec[0]/2)
   #print "offset",ofsetX,ofsetY
   back1.blit(errase,(0,0))
   back2.blit(errase,(0,0))
   back1.blit(image1,(ofsetX1,ofsetY))
   back2.blit(image2,(ofsetX1,ofsetY))
   
def dither(image):
   if image :
      screen.blit(back1,(0,0))
      pygame.display.flip()
      time.sleep(ditherTime)
   else:   
      screen.blit(back2,(0,0))
      pygame.display.flip()
      time.sleep(ditherTime)
      

   
def getFolder():  # get the list of pictures to show
   global imageList, newList, screen
   filename = askopenfilename()
   path = os.path.dirname(filename)
   imageList = [os.path.join(path,fn) for fn in next(os.walk(path))[2]]
   list.sort(imageList) # put in alphbetical order
   newList = True
   pygame.display.set_caption("Dithered 3D Slide Show - showing "+path)

def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global hold , advance , back
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_SPACE :
          getFolder()
       if event.key == pygame.K_UP :
          hold = True
       if event.key == pygame.K_DOWN :
          hold = False
       if event.key == pygame.K_RIGHT :
          advance = True
       if event.key == pygame.K_LEFT :
          back = True
          
# Main program logic:
if __name__ == '__main__':
#  try:   
     main()
#  except:
#    terminate()


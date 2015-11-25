#View3D - full screen slide show for Side by Side 3D Displays
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
screen = pygame.display.set_mode((0, 0)) # with window bar - use for debugging
if not debug :   
   pygame.display.toggle_fullscreen()
pygame.display.set_caption("3D Slide Show")
xs, ys = screen.get_size()
back1 = pygame.Surface(screen.get_size())
errase = pygame.Surface(screen.get_size())
back1 = back1.convert()
displayTime = 4.0 # seconds to show each image
hold = False
advance = False
back = False
newList = False
sbsSwap = True  # swap left and right on sbs files
mpoSwap = True  # swap left and right on mpo files
Tk().withdraw()

def main():
   global newList, hold, advance, back, imageList
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
        while time.time() < interval : # wait for next slide
          checkForEvent()
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
      startSeek = int(float(fileSize) * 0.47) #speed up search
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
         if mpoSwap :
             scale_show(image2, image1)
         else:    
             scale_show(image1, image2)
      else :
         print "no second image found in",name
         
def processSBS(name): # process a side by side image
   rootImage = pygame.image.load(name)
   xi, yi = rootImage.get_rect().size # size of the image
   image1 = pygame.Surface(((xi/2),yi))
   image2 = pygame.Surface(((xi/2),yi))
   image1.blit(rootImage,(0,0))
   image2.blit(rootImage,(0,0),((xi/2),0,(xi/2),yi))
   if sbsSwap :
      scale_show(image1, image2)
   else :   
      scale_show(image2, image1)

def scale_show(image1,image2):
   global screen, back1
   scale = 1.0   
   xi, yi = image1.get_rect().size # size of the image
   if xi> xs or yi > ys: # scalling needed
         scalex = float(xi) / float((xs-60)/2) # -60 to give a gap in the center
         scaley = float(yi) / float(ys/2)
         scale = scaley
         if scalex > scaley :
            scale = scalex
   newX = int(float(xi) / scale)
   newY = int(float(yi) / (scale/2)) # twice height to compensate for streatch
   #print"origional x&y ",xi,yi,"new X&Y", newX,newY
   image1 = pygame.transform.scale(image1,(newX,newY)) # scale the image
   image2 = pygame.transform.scale(image2,(newX,newY)) # scale the image
   imRec = image1.get_rect().size # get scaled size of the image
   ofsetY = (ys/2) - (imRec[1]/2 )
   ofsetX1 = (xs/4) - (imRec[0]/2)
   ofsetX2 = (3*(xs/4))- (imRec[0]/2)
   #print "offset",ofsetX,ofsetY
   back1.blit(errase,(0,0))
   back1.blit(image1,(ofsetX1,ofsetY))
   back1.blit(image2,(ofsetX2,ofsetY))
   screen.blit(back1,(0,0))
   pygame.display.flip()

def getFolder():  # get the list of pictures to show
   global imageList, newList, screen
   if not debug:
      pygame.display.toggle_fullscreen()
   filename = askopenfilename(title = "Select a file directory for the show")
   path = os.path.dirname(filename)
   imageList = [os.path.join(path,fn) for fn in next(os.walk(path))[2]]
   list.sort(imageList) # put in alphbetical order
   newList = True
   if not debug:
      pygame.display.toggle_fullscreen()

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


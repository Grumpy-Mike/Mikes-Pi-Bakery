#!/usr/bin/env python3
# Kaleido Cam - kaleidoscope web Cam or Raspberry Pi camera 
# By Mike Cook - October 2017

import pygame, pygame.camera, os
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

os.system("sudo modprobe bcm2835-v4l2") # needed for Pi camera
Tk().withdraw()
pygame.init()
pygame.camera.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Kaleido Cam")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

cs = 320 # basic image size
cs2 = cs * 2 # window size
screen = pygame.display.set_mode([cs2,cs2],0,32)

#find, open and start camera
cam_list = pygame.camera.list_cameras()
print(pygame.camera.list_cameras())
webcam = pygame.camera.Camera(cam_list[0],(640,480))
webcam.start()
preRot = 0 ; autoRotate = False
savePath = "" ; shotNumber = 0 ; saveSource = False
flipH = False ; flipV = False

def main():
   while True:
    checkForEvent()
    showScreen()

def showScreen(): #grab image, scale and blit to screen
    global camFrame, preRot    
    camFrame = webcam.get_image()
    if autoRotate :
       preRot += 0.5
       if preRot > 360:
          preRot -= 360
       rotFrame = pygame.transform.scale(camFrame,(cs2,cs2)) # make square
       rotFrame = rot_center(rotFrame,preRot) # rotate  
       sqFrame = pygame.Surface((cs,cs))
       sqFrame.blit(rotFrame,(0,0),(cs//2,cs//2,cs,cs))
    else :
       sqFrame = pygame.transform.scale(camFrame,(cs,cs)) # make square    
    if flipV or flipH: # flip origional image option
       sqFrame = pygame.transform.flip(sqFrame, flipH,flipV)
    # prepare master segment
    primary = pygame.Surface((cs,cs2))
    primary.blit(sqFrame,(0,0))
    primary.set_colorkey((0, 255, 0))
    primary2 = pygame.transform.flip(primary, False,True)
    primary2.blit(sqFrame,(0,0))
    primary2.set_colorkey((0, 255, 0))
    # mask out part of image
    pygame.draw.polygon(primary2,(0,255,0), ((0,cs),(cs,0),(0,0)),0)
    pygame.draw.polygon(primary2,(0,255,0), ((0,cs),(cs,cs2),(0,cs2)),0)
    # draw master segment in various positions
    screen.fill((0, 0, 0))
    screen.blit(primary2,(cs-1,0))
    primary = pygame.transform.flip(primary2,True, False)
    screen.blit(primary,(1,-1))
    primary3 = pygame.transform.rotate(primary2, 90.0)
    screen.blit(primary3,(0,1))    
    primary3 = pygame.transform.rotate(primary2, -90.0)
    screen.blit(primary3,(0,cs-1))
    
    pygame.display.update() # display screen
    
def rot_center(image, angle):
    # rotate an image while keeping its center and size
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def saveScreen():
    global shotNumber,savePath
    if savePath == "" :
        savePath = asksaveasfilename()
        shotNumber = 0
        print("save path",savePath)
    rect = pygame.Rect(1,1,cs2-2,cs2-2) # remove black lines    
    sub = screen.subsurface(rect)    
    pygame.image.save(sub, savePath+"_"+str(shotNumber)+".jpg")
    if saveSource:
       rect = pygame.Rect(0,0,640,480)
       sub = camFrame.subsurface(rect)
       pygame.image.save(sub, savePath+"_"+str(shotNumber)+"_source.jpg")
    print("saved as", savePath+"_"+str(shotNumber)+".jpg")
    shotNumber +=1
    
def terminate(): # close down the program
    webcam.stop()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global savePath,autoRotate, saveSource,preRot,flipH,flipV
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_s :
          savePath = ""
          saveScreen()
       if event.key == pygame.K_RETURN :
          saveScreen()
       if event.key == pygame.K_r :
          autoRotate =  not autoRotate
          print("Auto rotate =",autoRotate)
          if autoRotate:
             preRot = 0
       if event.key == pygame.K_o :
          saveSource = not saveSource
          print("Save the source file =",saveSource)
       if event.key == pygame.K_h :
          flipH = not flipH
          print("Flip horizontal now =",flipH)   
       if event.key == pygame.K_v :
          flipV = not flipV
          print("Flip vertical now =",flipV)   
          
# Main program logic:
if __name__ == '__main__':    
    main()

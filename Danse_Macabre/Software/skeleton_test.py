# Pi skeleton test create multiple rotation of limbs
# Plotted in a window and anamated a little
# By Mike Cook - August 2016

import pygame, time, os, math
pygame.init()                   # initialise graphics interface

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Skeleton test")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screen = pygame.display.set_mode([600,600],0,32)

bodyFrame  = pygame.image.load("skImages/body.png").convert_alpha()
xPovitBodyLarm = 17   ; yPovitBodyLarm = 153
xPovitBodyLleg = 37   ; yPovitBodyLleg = 306
xPovitBodyRarm = 126  ; yPovitBodyRarm = 159
xPovitBodyRleg = 98   ; yPovitBodyRleg = 322
xPovitBodyThighL = 37 ; yPovitBodyThighL = 306
xPovitBodyThighR = 98 ; yPovitBodyThighR = 321

def main():
   global strokeState, boneTest, boneMove
   print"skeleton test"
   loadImages()
   aRate = 0.01
   foreArmInc = 1; foreArmPos = -1;foreArmMax = 36
   ArmInc = 1; ArmPos = -1; ArmMax = 36
   thighInc = 1; thighPos = -1; thighMax = 40
   legInc = 1; legPos = -1; legMax = 36
   while True:      
      ArmPos += ArmInc
      if ArmPos == ArmMax or ArmPos < 0:
         ArmInc = ArmInc * -1
         ArmPos += ArmInc
         foreArmPos += foreArmInc
         if foreArmPos == foreArmMax or foreArmPos < 0:
               foreArmInc = foreArmInc * -1
               foreArmPos += foreArmInc
      thighPos += thighInc
      if thighPos == thighMax or thighPos < 0:
         thighInc = thighInc * -1
         thighPos += thighInc
         legPos += legInc
         if legPos == legMax or legPos < 0:
            legInc = legInc * -1
            legPos += legInc

      showPicture(ArmPos,ArmPos,foreArmPos,foreArmPos,thighPos,thighMax-thighPos-1,legPos,legPos,220,20)
      checkForEvent()
      time.sleep(aRate)
              
def showPicture(armLpos,armRpos,farmLpos,farmRpos,thighLpos,thighRpos,legLpos,legRpos, x,y):
   pygame.draw.rect(screen,(102,204,255), (0,0,600,600), 0)
   screen.blit(bodyFrame,(x,y))
   screen.blit(thighFrames[thighRpos],(x - thighPlot+xPovitBodyThighR,y-thighPlot+yPovitBodyThighR))  
   screen.blit(rightLegFrames[legRpos],(x - rightLegPlot + xPovitBodyThighR+dXthigh[thighRpos],y-rightLegPlot+yPovitBodyThighR+dYthigh[thighRpos]))

   screen.blit(thighFrames[thighLpos],(x - thighPlot+xPovitBodyThighL,y-thighPlot+yPovitBodyThighL))
   screen.blit(leftLegFrames[legLpos],(x - leftLegPlot + xPovitBodyThighL+dXthigh[thighLpos],y-leftLegPlot+yPovitBodyThighL+dYthigh[thighLpos]))
 
   screen.blit(armFramesL[armLpos],(x - armPlot+xPovitBodyLarm,y-armPlot+yPovitBodyLarm))  
   screen.blit(foreArmFramesL[farmRpos],(x - foreArmPlot + xPovitBodyLarm+dXarmL[armLpos],y-foreArmPlot+yPovitBodyLarm+dYarmL[armLpos]))
   
   screen.blit(armFramesR[armRpos],(x - armPlot+xPovitBodyRarm,y-armPlot+yPovitBodyRarm))   
   screen.blit(foreArmFramesR[farmRpos],(x - foreArmPlot+xPovitBodyRarm+dXarmR[armRpos],y-foreArmPlot+yPovitBodyRarm+dYarmR[armRpos]))
   pygame.display.update()

def loadImages():
    global foreArmFramesR,foreArmFramesL,foreArmPlot,armFramesR,armFramesL,armPlot,dXarmR,dYarmR,dXarmL,dYarmL
    global thighFrames, thighPlot, dYthigh, dXthigh, leftLegFrames, leftLegPlot,rightLegFrames, rightLegPlot
    print"creating and scaling images"
    print"creating legs"
    leftLegFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/leftLegzero.png").convert_alpha(),angle),(360,360))
                  for angle in range(90,-90,-5)]
    leftLegPlot = leftLegFrames[0].get_width()/2    
    rightLegFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/rightLegzero.png").convert_alpha(),angle),(360,360))
                  for angle in range(-90,90,5)]
    rightLegPlot = rightLegFrames[0].get_width()/2

    print"creating thighs"
    thighFrames = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/thighzero.png").convert_alpha(),angle),(267,267))
                  for angle in range(100,-100,-5)]
    thighPlot = thighFrames[0].get_width()/2
    dYthigh = [ 101.56*math.cos(math.radians(angle))  for angle in range(100,-100,-5)]              
    dXthigh = [ 101.56*math.sin(math.radians(angle))  for angle in range(100,-100,-5)]

    print"creating arms"
    armFramesR = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/armzero.png").convert_alpha(),angle),(224,224))
                  for angle in range(150,-30,-5)]
    armPlot = armFramesR[0].get_width()/2
    dYarmR = [ 85.2*math.cos(math.radians(angle))  for angle in range(150,-30,-5)]              
    dXarmR = [ 85.2*math.sin(math.radians(angle))  for angle in range(150,-30,-5)]
    armFramesL = [ pygame.transform.flip(armFramesR[i], True,False)
                  for i in range(0,36)]
    dYarmL = [ 85.2*math.cos(math.radians(angle))  for angle in range(150,-30,-5)]              
    dXarmL = [ -85.2*math.sin(math.radians(angle))  for angle in range(150,-30,-5)]

    print"creating forearms"
    foreArmFramesL = [ pygame.transform.smoothscale(rot_center(pygame.image.load("skImages/forearmzero.png").convert_alpha(),angle),(334,334))
                  for angle in range(60,240,5)]
    foreArmPlot = foreArmFramesL[0].get_width()/2
    foreArmFramesR = [  pygame.transform.flip(foreArmFramesL[i], True,False)
                  for i in range(0,36)]

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
    
def terminate(): # close down the program
    print "Closing down please wait"
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global hide
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()         
          
# Main program logic:
if __name__ == '__main__':    
    main()

# Mains control - Hunt the Snark
# By Mike Cook - January 2016

import pygame, time, os, random
import wiringpi2 as io
from copy import deepcopy

pygame.init()                   # initialise graphics interface
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Control Central")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT,pygame.MOUSEBUTTONDOWN])
screen = pygame.display.set_mode([1050,480],0,32)
textHeight = 22
font = pygame.font.Font(None, textHeight)
random.seed()

try :
   io.wiringPiSetupGpio()
except :
   print"start IDLE with 'gksudo idle' from command line"
   os._exit(1)

plugState = [ False for n in range(0,16)]  
groupPins = [17,17,17,17, 27,27,27,27, 23,23,23,23, 10,10,10,10]
channelPins = [4, 18, 22, 24, 4, 18, 22, 24, 4, 18, 22, 24, 4, 18, 22, 24]
A_11Pin = 25
sendPin = 9
plugName = ["Lounge1","Lounge2","Dining Room","Kitchen","Bedroom 1","Bedroom 2",
            "Bedroom 3","Hall 1","Landing","Garage","Porch","Attic",
            "TV Lamp","Kitchen Lamp","Hall 2","Computer Room"]
plugPicture = pygame.image.load("images/plug.png").convert_alpha()
scPicture = [pygame.image.load("images/sc"+str(n)+".png").convert_alpha()
                  for n in range(1,5)]
sgPicture = [pygame.image.load("images/sg"+str(n)+".png").convert_alpha()
                  for n in range(1,5)]

def main():
   print"Mains Controller - Hunt the Snark"
   print"Press h - to hunt"
   
   initGPIO()
   showPicture()
   while True:
     checkForEvent()
     time.sleep(0.2)

def togglePlug(click):
   global plugState
   plug = (click[0] / 130) + (8 *(click[1] /240))
   plugState[plug] = not(plugState[plug])
   setPlug(plug,plugState[plug])
   showPicture()

def setPlug(p,on):
   io.digitalWrite(groupPins[p],1)
   io.digitalWrite(channelPins[p],1)
   if on :
      io.digitalWrite(A_11Pin,0)
      io.digitalWrite(sendPin,1)
      time.sleep(0.32)
      io.digitalWrite(sendPin,0)
   else :
      io.digitalWrite(A_11Pin,1)                                                                                                                                                                                                                                                                                                                                             
      time.sleep(0.32)
      io.digitalWrite(A_11Pin,0)
   time.sleep(0.2)
   io.digitalWrite(channelPins[p],0)
   io.digitalWrite(groupPins[p],0)

def huntSet():
   global plugState
   print"Seting the Snark"
   changeState = deepcopy(plugState)
   changed = False
   maxiumChanges = 8 # alter for more potential changes
   while not(changed):
      for n in range(0,random.randint(1,maxiumChanges)):
        p=random.randint(0,15)
        changeState[p] = not(changeState[p])
      for n in range(0,16):
         if changeState[n] != plugState[n] :
            plugState[n] = changeState[n]
            setPlug(n,plugState[n])
            changed = True
            showPicture()
   print"Ready for the hunt"
       
def initGPIO():
   for pin in range (0,16):
      io.pinMode(groupPins[pin],1)
      io.digitalWrite(groupPins[pin],0)
      io.pinMode(channelPins[pin],1)
      io.digitalWrite(channelPins[pin],0)      
   io.pinMode(A_11Pin,1)
   io.digitalWrite(A_11Pin,0)
   io.pinMode(sendPin,1)
   io.digitalWrite(sendPin,0)
     
def showPicture():
   for row in range(0,2):
      for plug in range(0,8):
         screen.blit(scPicture[plug % 4],[(plug * 130)+35,(row * 240)+9])
         screen.blit(sgPicture[((plug / 4)+ row*2)],[(plug * 130)+41,(row * 240)+152])
         screen.blit(plugPicture,[plug * 130,row * 240])
   for plug in range(0,16):
      x = (plug % 8)*130
      y = (plug / 8)*240
      drawWords(plugName[plug],x+15,y+97)
      if plugState[plug]:
         pygame.draw.circle(screen,[180,0,0],[x+66,y+80],6,0)      
   pygame.display.update()
   time.sleep(0.4)
   
def drawWords(words,x,y) :
        textSurface = pygame.Surface((2+len(words)*12,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        textSurface = font.render(words, True, (19,104,229), (200,205,208))
        screen.blit(textSurface, textRect)
   
def terminate(): # close down the program
    print ("Closing down please wait")
    for plug in range(0,16): # Turn all plugs off - delete if required
       if plugState[plug] == True : 
          setPlug(plug,False)
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global visited, duplicate
    event = pygame.event.poll()
    if event.type == pygame.MOUSEBUTTONDOWN:
       point = pygame.mouse.get_pos()
       togglePlug(point)
       #print point # print out position of click for development
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_h : # hunt the Snark
          huntSet()
          
# Main program logic:
if __name__ == '__main__':    
    main()

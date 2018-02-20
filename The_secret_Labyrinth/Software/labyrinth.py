#!/usr/bin/python3
# Secret Labyrinth two nunchucks
import sys, random
from smbus import SMBus
import RPi.GPIO as io
import pygame, os, time

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Secret Labyrinth")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])

gSpace = 70 # size of square
gSide = 9 # number of squares per side
nSquares = gSide*gSide
screenSize = gSpace * gSide
screen = pygame.display.set_mode([screenSize+2,screenSize+2],0,32)
random.seed() ; centre =  (nSquares-1) // 2
refresh = True ; joyLast = [-1,-1,-1,-1]
playPos = [0,0,0,0] # current and start position
maskFrom = [8,2,1,4]
dirInc = [-1,1,-gSide,gSide] # direction movement
wallColour = (0,255,255) # for revealed labyrinth

def main():
   global refresh, done
   done = False
   initIO()
   init() # load in sound and graphics
   mazeGen() # create maze
   while 1:
      while not(done):
         checkForEvent()
         if refresh :
           drawScreen(False) # change to True for hidden view
           refresh = False
      time.sleep(3.5) # see the walls
      mazeGen()
      done = False

def drawScreen(laby):
    rSize = gSpace
    pygame.draw.rect(screen,(0,0,0),(0,0,screenSize,screenSize),0)
    #draw Tiles
    for s in range(0,nSquares):
      xp = findX(s)
      yp = findY(s)
      screen.blit(tiles[tilePlan[s]],(xp,yp))  
    #draw grid
    if not(laby) :  
       for y in range(0,gSide+1):
          pygame.draw.line(screen,(255,255,0),(gSpace*y,0),(gSpace*y,screenSize+2),2)
       for x in range(0,gSide+1):
          pygame.draw.line(screen,(255,255,0),(0,gSpace*x),(screenSize+2,gSpace*x),2)
       
    #draw players & prize
    xp = findX(centre)
    yp = findY(centre)
    screen.blit(prize,(xp,yp))
    xp = findX(playPos[0])
    yp = findY(playPos[0])
    screen.blit(tux1,(xp,yp))
    xp = findX(playPos[1]) 
    yp = findY(playPos[1]) 
    screen.blit(tux2,(xp,yp))
    
    # draw labyrinth
    if laby :
       for s in range (0,nSquares):
         xp = findX(s)
         yp = findY(s)
         for side in range(0,4):
            if not(maze[s] & 1) :   
               pygame.draw.line(screen,wallColour,(xp,yp),(xp+rSize,yp),2)
            if not(maze[s] & 2) :   
               pygame.draw.line(screen,wallColour,(xp+rSize,yp+rSize),(xp+rSize,yp),2)
            if not(maze[s] & 4) :
               pygame.draw.line(screen,wallColour,(xp+rSize,yp+rSize),(xp,yp+rSize),2)            
            if not(maze[s] & 8) :
               pygame.draw.line(screen,wallColour,(xp,yp),(xp,yp+rSize),2)         
    pygame.display.update()      

def findX(square):
   return (square % gSide)*gSpace

def findY(square):
   return (square//gSide)*gSpace

def initIO():
    global bus
    io.setmode(io.BCM)
    io.setwarnings(False)
    select = [4,17]
    io.setup(select,io.OUT)
    io.output(select,0) # select nunchuck 0
    print("Initialise I2C")
    if io.RPI_REVISION == 1:
      i2c_bus = 0
    else :
      i2c_bus = 1 
    bus = SMBus(i2c_bus)
    for nun in range(0,2):     
       bus.write_byte_data(0x52,0x40,0x00)
       io.output(4,1) # select nunchuck 1
       time.sleep(0.01)

def init():
    global bus,sounds, maze, tux1, tux2, prize, tiles, tilePlan
    global finish, resetPlayer
    tux1 = pygame.image.load("images/Tux1.png").convert_alpha()
    tux2 = pygame.image.load("images/Tux2.png").convert_alpha()
    prize = pygame.image.load("images/present.png").convert_alpha()
    tiles = [pygame.image.load("images/Tile"+str(t)+".png").convert_alpha()        
               for t in range(0,15)]
    finish = pygame.mixer.Sound("sounds/finish.wav")
    resetPlayer = [pygame.mixer.Sound("sounds/Pop.wav"),
                   pygame.mixer.Sound("sounds/Rattle.wav")]
    maze = []
    tilePlan = []
    for sr in range(0,nSquares):
       maze.append(0) # create maze array
       tilePlan.append(0) # pattern of tiles
       
def readNck(nunNum): # the I2C drivers or something throws up an occasional error - this is the sticking plaster
    io.output(4,nunNum) # select the right nunchuck
    time.sleep(0.004)
    try:
       bus.write_byte(0x52,0)
    except:
       print("bus restart")
       time.sleep(0.1)
       initIO()
       bus.write_byte(0x52,0)
    time.sleep(0.002) #delay for Nunchuck to respond   
    nCk = [((bus.read_byte(0x52) ^ 0x17) +0x17) for i in range(0,6)]
    return nCk    

def mazeGen():
   global maze, current, last, tilePlan, playPos, refresh
   refresh = True
   maskTo = [2,8,4,1]
   thisTile = random.randint(0,14)
   thisMethod = random.randint(0,3)
   for s in range(0,nSquares):
     maze[s] = 0 # clear the maze
     if thisMethod == 0:
        tilePlan[s] = random.randint(0,14) # random tile
     if thisMethod == 1:   
        tilePlan[s] = s % 10 # diagonal lines
     if thisMethod == 2:   
        tilePlan[s] = thisTile # all the same but different for each maze
     if thisMethod == 3:   
        tilePlan[s] = s % 12 # offset lines 
   maze[centre] = 15  
   current = centre ; last = centre
   while not(current == 0 or current == 8):
      blocked = True
      while blocked:
         move = random.randint(0,3)
         direction = dirInc[move] # initial direction of move
         test = direction + current
         if test >= 0 and test <= (nSquares/2 +gSide/2) and test != last: # within the board
            if not(direction ==1 and current % gSide == gSide-1) and not(direction ==-1 and current % gSide == 0):
              blocked = False
              maze[last] = maze[last] | maskFrom[move] # clear exit square
              maze[nSquares-last-1] = swap(maze[last]) 
              current = test
              last = current
              maze[current] = maze[current] | maskTo[move] # clear entrance square
              maze[nSquares-current-1] = swap(maze[current]) #need to swap bits
   playPos[0] = current # player start positions
   playPos[1] = nSquares - 1 - current
   playPos[2] = playPos[0] ; playPos[3] = playPos[1] # start positions

def movePlayer(pn, inc):
   global refresh, playPos, done
   refresh = True
   fromSq = playPos[pn]
   playPos[pn] += dirInc[inc]
   if not(maze[fromSq] & maskFrom[inc]) :  # a wall in the way 
      playPos[pn] = playPos[pn+2] # back to start
      resetPlayer[pn].play() # reset noise             
   if playPos[pn] == centre : # winner
      finish.play()
      refresh = False
      drawScreen(True)
      done = True

def getMove():
   global joyLast
   joyNow = [-1,-1,-1,-1] # no move
   for nun in range(0,2): # read both nunchucks
      x = nun
      y = 2+nun
      bank = readNck(nun)
      if bank[0] > 190:
         joyNow[x] = 1 # move right
      if bank[0] < 60:
         joyNow[x] = 0 # move left
      if bank[1] > 190:
         joyNow[y] = 2 # move up
      if bank[1] < 60:
         joyNow[y] = 3 # move down
      if joyNow[x] != joyLast[x] and joyNow[x] > -1:
         movePlayer(nun,joyNow[x]) # make move left or right
      if joyNow[y] != joyLast[y] and joyNow[y] > 1:
         movePlayer(nun,joyNow[y]) # make move up or down
      joyLast[x] = joyNow[x]          
      joyLast[y] = joyNow[y]
   
def swap(value):
  result = (value & 1) << 2 | (value & 4) >>2 | (value & 2) << 2 | (value & 8) >> 2
  return result
    
def terminate(): # close down the program
    print ("Closing down please wait")
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global refresh
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    getMove()    
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       getMove()   
       if event.key == pygame.K_g : #glimpse maze walls
          drawScreen(True)
          time.sleep(2.0) # time to display
          refresh = True # draw over it
          
# Main program logic:
if __name__ == '__main__':    
    main()


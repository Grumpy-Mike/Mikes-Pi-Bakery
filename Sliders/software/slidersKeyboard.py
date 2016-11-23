# Pi Christmas Slider Game - keyboard interface
# By Mike Cook - October 2016

import pygame, time, os, random

pygame.init()                   # initialise graphics interface
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)   

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
pygame.display.set_caption("Slider - The Pi Christmas Game")
pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.KEYDOWN,pygame.QUIT])
screenSize = 560
screen = pygame.display.set_mode([screenSize,screenSize],0,32)
textHeight = 36 ; sq = 112 # square size
font = pygame.font.Font(None, textHeight)
random.seed()

move = 0; moveInc = 0; moveIncX = 0; moveIncY = 0
squareC = [ (175,175,175),(255,255,255)]
board = [ 2,0,5,0,0, 3,0,0,0,0,  0,0,1,0,0,  0,0,4,0,0,  0,0,2,0,3]
moveList = [0,0, 0,0, 0,0, 0,0, 0,0, 0,0]
gameOver = True ; newLevel = True ; sameGame = False
currentGame = 0 ; gameLevel = 0 

def main():
   global move, gameOver, newLevel
   loadResorces()
   print"The Pi Christmas Game"
   while True:
      #checkForEvent()
      if gameOver:
         if newLevel:
            selectGameLevel()
            newLevel = False   
         makeNewGame()
         #print "table level"
         time.sleep(1.0)
         gameOver = False
         lastMove = 0
         move = 0
      while (move == lastMove or move == 0) and (not gameOver): # wait for a move
         checkForEvent()
      lastMove = move
      if move!= 0 and not gameOver:
         gameSound[0].play()
      while move != 0 and not gameOver: # move all to the side of the tilt
         makeMoveList()        
         s=0
         while s <= 1.0: # move free pieces one square
           showMove(s)
           s+= 0.05
         updateBoard()
         showBoard()
        
def selectGameLevel():
   global gameLevel, move
   drawSelectScreen()
   move = 0  
   while move == 0:
      checkForEvent()
   gameLevel = move
   print"game level ",gameLevel, " selected"
         
def drawSelectScreen():
   cp = screenSize/2
   pygame.draw.rect(screen,squareC[0],(0,0,screenSize,screenSize),0)
   drawWords("Tilt to select Game Level",cp-140,cp-100)
   drawWords("Ultra Hard",20,cp)
   drawWords("Hard",screenSize-100,cp)
   drawWords("Easy",cp-40,20)
   drawWords("Medium",cp-50,screenSize- 60)
   screen.blit(piece[2],(10,cp+40))
   screen.blit(piece[3],(screenSize-140,cp+40))
   screen.blit(piece[4],(cp-60,60))
   screen.blit(piece[5],(cp-60,screenSize-180))
   pygame.display.update()

def makeNewGame():
   global board, gameOver, setup,sameGame, currentGame
   for s in range(0,25): # Wipe out board
      board[s]=0
   if not sameGame :
      temp = currentGame
      while temp == currentGame:
         currentGame = random.randint(gameRange[gameLevel-1]+1,gameRange[gameLevel])
   game = setup[currentGame]
   elements = len(game)
   print"playing game ",currentGame
   for s in range(0,elements,2):
      board[game[s+1]] = game[s]
   board[12] = 1 # always the chimney
   gameOver = False
   sameGame = False
   showBoard()
   
def updateBoard():
   global board, gameOver, sameGame
   for c in range(0,12,2):
      if moveList[c+1] > 2: # not chimney or reindeer
         board[moveList[c]] = 0 # remove piece
         board[moveList[c]+ moveInc] = moveList[c+1] # new piece position
   if board[12] == 3:
      gameOver = True # lose
      gameSound[1].play() # elf scream
      sameGame = True
      screen.blit(loseImage,(0,60))
      pygame.display.update()
      time.sleep(3.0)
      board[12] = 1
   if board[12] == 4 or board[12] == 5 :
      gameSound[2].play() # present delivery sound
      board[12] = 1
      finished = True
      for s in range(0,25):
         if board[s] == 4 or board[s] == 5: # see if anything left to deliver
            finished = False
      if finished :      
         gameOver = True # win
         screen.blit(winImage,(0,60))
         pygame.display.update()
         time.sleep(2.0)
         gameSound[3].play() # finish
         time.sleep(2.0)
   
def makeMoveList(): # add to move list if not wrap round & space to move into 
   global moveList,move
   c = 0
   for i in range(0,12):
      moveList[i] = 0 # remove all moves
   for square in range(0,25):
      if board[square] > 2:
        if not findWrap(square):
          if board[moveInc + square] < 2:
            moveList[c] = square # place piece is
            moveList[c+1] = board[square] # piece type
            c += 2
   if c == 0:
      move = 0 # finished moving
      
def findWrap(square):
   wrap = False
   y = int(square / 5)
   x = (square - (y * 5))
   xw = x + moveIncX
   yw = y + moveIncY
   if xw>4 or xw <0 or yw > 4 or yw < 0:
     wrap = True
   return wrap

def showMove(movePart): # move all on the move list one square
   for c in range(0,12,2):
      if moveList[c+1] !=0:
         y = int(moveList[c] / 5)
         x = (moveList[c] - (y * 5))
         if moveList[c+1] > 2 :
           drawMove(moveList[c+1],x*sq+(sq*moveIncX*movePart),y*sq+(sq*moveIncY*movePart),moveList[c],x*sq,y*sq) 
   pygame.display.update()

def drawMove(character,x,y,square,sx,sy):
   pygame.draw.rect(screen,squareC[square & 1],(sx,sy,sq,sq),0) # from square
   pygame.draw.rect(screen,squareC[(square & 1)^1],(sx+(sq*moveIncX),sy+(sq*moveIncY),sq,sq),0) # to square
   screen.blit(piece[character],(x,y))
   
def showBoard():
   c = 1
   for x in range(0,5):
      xp = x * 112
      for y in range(0,5):
         yp = y *112
         c = c ^ 1
         pygame.draw.rect(screen,squareC[c],(xp,yp,112,112),0)
   for square in range(0,25):
     y = int(square / 5)
     x = (square - (y * 5))
     if board[square] != 0 :
       screen.blit(piece[board[square]],(x*sq,y*sq))     
   pygame.display.update()

def drawWords(words,x,y) :
        textSurface = pygame.Surface((14,textHeight))
        textRect = textSurface.get_rect()
        textRect.left = x
        textRect.top = y
        textSurface = font.render(words, True, (0,0,0), squareC[0])
        screen.blit(textSurface, textRect)
         
def loadResorces():
   global gameSound,piece,winImage,loseImage,santa,santaFlip,setup,gameRange
   chimney = pygame.image.load("images/chim.png").convert_alpha()
   elf = pygame.image.load("images/elf.png").convert_alpha()
   rainD = pygame.image.load("images/rain1.png").convert_alpha()
   santa = pygame.image.load("images/santa.png").convert_alpha()
   santaFlip = pygame.image.load("images/santaFlip.png").convert_alpha()
   present = pygame.image.load("images/present.png").convert_alpha()
   piece = [chimney,chimney,rainD,elf,santa,present]
   winImage = pygame.image.load("images/win.png").convert_alpha()
   loseImage = pygame.image.load("images/lose.png").convert_alpha()
   soundEffects = ["bells","elfScream","HoHoHo","finish"]
   gameSound = [ pygame.mixer.Sound("sounds/"+soundEffects[sound]+".wav")
                  for sound in range(0,4)]
   # Easy
   g1 = [4,0, 2,1, 2,22]
   g2 = [2,0,4,1, 3,2]
   g3 = [3,0,4,1, 2,2, 3,20, 5,21]
   g4 = [2,0, 4,4, 5,24,3,20]
   g5 = [3,0, 3,5, 3,2, 4,1, 5,7, 2,6]
   g6 = [2,1, 2,6, 2,11, 2,10, 3,2, 4,4, 5,24]
   g7 = [2,0, 2,2, 2,3, 4,15, 3,20]
   g8 = [4,0, 5,5, 3,10, 3,15, 3,20, 2,6, 2,11, 2,2, 2,7]
   g9 = [4,20, 3,21, 3,4, 3,3, 2,2]
   g10 = [4,24,3,23, 3,14, 3,13, 2,17, 2,18, 2,19]    
   # Medium
   g11 = [3,0, 2,1, 4,5, 5,6, 2,7, 2,9]
   g12 = [2,1, 4,6, 2,7, 5,8, 2,13, 2,21]
   g13 = [2,0,2,1,2,2, 2,6, 2,7, 4,20,5,21,3,24]
   g14 = [2,17,2,18,3,22, 4,23, 2,24]
   g15 = [2,0,3,1, 3,4, 4,9, 2,14]
   g16 = [2,0, 2,3, 4,5,2,7, 3,10]
   g17 = [2,11, 2,20, 4,21, 3,22]
   g18 = [3,0, 2,1, 3,5, 2,8, 2,10, 2,11, 2,13, 4,15]
   g19 = [2,2, 4,3, 5,4, 3,7,3,8,3,9, 2,16]
   g20 = [2,0, 3,1, 4,5, 2,7, 3,10, 2,17, 2,22]
   # Hard
   g21 = [2,0, 2,2, 2,4, 2,11, 2,17, 2,22, 4,19, 3,24]
   g22 = [2,2,4,3, 3,4, 2,6, 5,9, 3,24]
   g23 = [2,2, 4,5, 2,10, 2,20, 3,21, 2,24]
   g24 = [2,0, 2,7, 4,8, 5,9, 2,13, 2,14, 3,18, 3,19]
   g25 = [2,0, 2,9, 2,13, 4,14, 5,19, 3,18, 2,17, 3,24, 3,23]
   g26 = [2,0, 2,2, 3,17,3,18,3,19, 2,22,4,23, 3,24]
   g27 = [2,0,2,1, 2,7,3,10, 2,15, 2,16, 3,20, 4,21]
   g28 = [2,1, 2,6, 3,2, 3,4, 3,7, 4,9, 2,13, 3,14,2,16, 2,17, 2,18]
   g29 = [2,0, 3,1,4,2, 3,3, 2,4, 2,6, 2,7, 3,21, 2,22]
   g30 = [2,1,2,2, 2,11, 2,15, 2,17, 3,16, 3,20, 4,21, 3,22, 2,24]
   # Ultra hard
   g31 = [2,1,2,2, 2,17,2,21, 4,16,5,23, 3,22, 3,18]
   g32 = [2,0,2,1, 2,4, 4,5, 5,6, 3,10, 2,22]
   g33 = [2,20, 2,22,2,23, 2,17, 2,13, 4,18, 5,24,3,19]
   g34 = [2,1, 2,3, 2,11, 2,18, 2,23, 3,17,3,22, 4,16, 5,21]
   g35 = [2,2,2,7,2,10, 4,1, 5,5, 3,6,3,3, 3,15]
   g36 = [2,1,2,6, 2,13,2,23, 3,3,3,9,3,14, 4,4, 5,8]
   g37 = [2,2, 2,6,2,11,2,17, 3,3,3,8, 4,4, 5,9]
   g38 = [2,0,2,2, 2,14, 2,19, 2,22, 3,1, 5,5, 4,10]
   g39 = [2,0, 2,2,2,9,2,13,2,17, 5,3,4,4,3,8]
   g40 = [2,0,2,7,2,13,2,17,2,21, 4,4, 5,5,3,9, 3,10]
   setup = [g1,g1,g2,g3,g4,g5,g6,g7,g8,g9,g10,g11,g12,g13,g14,g15,g16,g17,g18,g19,g20,
    g21,g22,g23,g24,g25,g26,g27,g28,g29,g30,g31,g32,g33,g34,g35,g36,g37,g38,g39,g40]
   gameRange = [0,10,20,30,40]
   
def terminate(): # close down the program
    print "Closing down please wait"
    pygame.mixer.quit()
    pygame.quit() # close pygame
    os._exit(1)
 
def checkForEvent(): # see if we need to quit
    global move, moveInc,moveIncX,moveIncY,gameOver,piece,newLevel,sameGame
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
       if event.key == pygame.K_r :
          gameOver = True # abandon game
          sameGame = True # don't set new level
          move = 0
       if event.key == pygame.K_RETURN :
          gameOver = True # abandon game
          newLevel = True # set new level
          move = 0
       if event.key == pygame.K_SPACE :
          gameOver = True # start game again
          move = 0
       if event.key == pygame.K_UP :
          move = 1
          moveInc = -5
          moveIncX = 0 
          moveIncY = -1
       if event.key == pygame.K_DOWN :
          move = 2
          moveInc = 5
          moveIncX = 0 
          moveIncY = 1          
       if event.key == pygame.K_RIGHT :
          move = 3
          moveInc = 1
          moveIncX = 1 
          moveIncY = 0
          piece[4] = santaFlip
       if event.key == pygame.K_LEFT :
          move = 4
          moveInc = -1
          moveIncX = -1 
          moveIncY = 0
          piece[4] = santa
          
          
# Main program logic:
if __name__ == '__main__':    
    main()

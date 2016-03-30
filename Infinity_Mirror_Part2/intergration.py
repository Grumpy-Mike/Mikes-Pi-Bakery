def checkForDistance():
   global pattern, patternStep
   if io.digitalRead(sensorPins[0]) == 1 :
      if pattern != 0: # if something showing
         wipe()
         pixels.show()
         pattern = 0 # stop any display
         patternStep = 0 # put to start of a pattern
         display.clear_display() # wipe time display
         display.display()
   else :
      close = 0
      for n in range(1,4):
         if io.digitalRead(sensorPins[n]) == 0 :
            close = n
      if pattern != close+1 : # has pattern changed      
         pattern = close+1
         patternStep = 0 # stage in pattern
         timeText = time.strftime("%X")
         printHardTime(int(timeText[0:2]),int(timeText[3:5]) )
         #print"now showing pattern ",pattern

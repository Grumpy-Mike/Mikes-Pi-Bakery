# Hard time stand alone - Magic mirror
# By Mike Cook - Febuary 2016

import time, os, random
import gaugette.ssd1306

random.seed()
numberText = ["zero","one","two", "three", "four", "five", "six", "seven","eight",
                    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen","fifteen",
                     "sixteen", "seventeen", "eighteen","nineteen"]
upperNumberText = ["teen","twenty","thirty","forty","fifty"]
pastText = [" ","Five","Ten","1/4","20", "25", "Half"]
pastTextFull = ["nothing","five","ten","quarter","twenty", "twenty five", "half"]
toText = [" "," Five","  Ten","Quarter","Twenty", "   25", " Half"]

RESET_PIN = 15
DC_PIN    = 16
ROWS      = 64

display = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN, rows = ROWS)
display.begin()
display.clear_display()


def main():
   print"Time test"      
   while True:
     timeText = time.strftime("%X")
     print timeText
     printHardTime(int(timeText[0:2]),int(timeText[3:5]) )     
     print
     time.sleep(5.0)
     
def printHardTime(hardH, minsR):
    display.clear_display()    
    offset = 0
    past = True
    if(random.randint(0,10) > 5) :
       past = False
    if(past) :
       offset = random.randint(1, 6)
    else :
       offset = random.randint(1, 5)
    if(past) :
      display.draw_text2(0,0,pastText[offset]+" past",2)
      hardM = minsR - (offset * 5)
      if hardM < 0 :
        hardM +=60
        hardH -= 1
        if(hardH < 1) :
          hardH = 23     
      printTimeW(hardH,hardM); 
    else :
      display.draw_text2(0,0,toText[offset]+" to",2)
      hardM = minsR + (offset * 5)
      if(hardM >= 60) :
        hardM -=60
        hardH += 1
        if(hardH > 23) :
           hardH = 1     
      printTimeW(hardH,hardM)    
    display.display();

def printWords(number,y,s):
  if(number < 20):
    display.draw_text2(0,y,numberText[number],s)
    return
  else :
    display.draw_text2(0,y,upperNumberText[(number-10) / 10]+" ",s)
    if number % 10 != 0 :
       n = len(upperNumberText[(number-10) / 10]+" ")*6
       display.draw_text2(n,y,numberText[number% 10],s)

def printTimeW(h, mins):
  past = True
  if(h > 12) :
     h -= 12
  if(mins > 30):
        mins = 60 - mins; # test for seconds being mins
        h += 1
        if(h > 12) :
           h = 1
        past = False   
  if((mins % 5) == 0) :
     if(mins != 0):  # time is on a 5 min interval  
        #print(pastTextFull[mins / 5])
        display.draw_text2(0,24,pastTextFull[mins / 5],1)
        if( past ) :
           display.draw_text2(0,32,"      past ",1)
        else :
           display.draw_text2(0,32,"      to ",1)
        printWords(h,48,2)
     else : # time is on the hour
        printWords(h,48,2)
  else :
    printWords(mins,24,1) #minutes
    if( past ):
      if(mins == 1):
         display.draw_text2(0,32,"minute past ",1)
      else :
         display.draw_text2(0,32,"minutes past ",1)
    else :
      if(mins == 1) :
         display.draw_text2(0,32,"minute to ",1)
      else :
        display.draw_text2(0,32,"minutes to ",1)
  printWords(h,48,2)

# Main program logic:
if __name__ == '__main__':    
    main()

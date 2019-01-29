'' ===========================================================================
''
''  File: WMF_Terminal_Services_010.spin
'' 
'' This file contains general "terminal services" for the VGA driver VGA_HiRes_Text_***.
'' This is a work in progress and over time as the version iterates more functionality
'' will be added. However, for now, the object contains the following general sets
'' of functionality:
'' 
'' 1. General VGA terminal / console functionality
'' 2. Direct screen rendering for printing characters, text, etc.
'' 3. Text parsing functionality to help with string processing.
'' 4. Numeric functions that print binary, hex, decimal numbers as we well as conversion functions
''   from and to.
'' 
'' Of course, one could seperate all these into multiple objects, but in the quest for simplicity
'' I am going to keep all these functions within the same module since they are so tightly coupled,
'' need access to each other, and this is simply easier to deal with. You may want to seperate things
'' out later into multiple modules/objects and you are free to do so.
'' 
'' Much of the functionality in this object is very specific to the VGA driver it supports. This is
'' a necessary evil of graphics drivers. Each one has its various features, memory layout, functionality,
'' etc. and we must code for it specifically. Additioanally, a lot of the functions are generic and process
'' strings, characters, and convert numbers.
''
''  Modification History
''
''  Author:     Andre' LaMothe 
''  Copyright (c) Andre' LaMothe / Parallax Inc.
''  See end of file for terms of use
''  Version:    1.0
''  Date:       2/15/2011
''
''  Comments:
''
'' ===========================================================================

CON
' -----------------------------------------------------------------------------
' CONSTANTS, DEFINES, MACROS, ETC.   
' -----------------------------------------------------------------------------
  CLOCKS_PER_MICROSECOND = 5*16     ' simple xin*pll / 1_000_000                     
  CLOCKS_PER_MILLISECOND = 5000*16  ' simple xin*pll / 1_000


  ' import some constants from the VGA driver
  VGACOLS = vga#cols
  VGAROWS = vga#rows

  ' ASCII codes for ease of parser development
  ASCII_A      = 65
  ASCII_B      = 66
  ASCII_C      = 67
  ASCII_D      = 68
  ASCII_E      = 69
  ASCII_F      = 70
  ASCII_G      = 71
  ASCII_H      = 72
  ASCII_O      = 79  
  ASCII_P      = 80
  ASCII_Z      = 90
  ASCII_0      = 48
  ASCII_9      = 57
  ASCII_LEFT   = $C0
  ASCII_RIGHT  = $C1
  ASCII_UP     = $C2
  ASCII_DOWN   = $C3 
  ASCII_BS     = $C8 ' backspace
  ASCII_DEL    = $C9 ' delete
  ASCII_LF     = $0A ' line feed 
  ASCII_CR     = $0D ' carriage return
  ASCII_ESC    = $CB ' escape
  ASCII_HEX    = $24 ' $ for hex
  ASCII_BIN    = $25 ' % for binary
  ASCII_LB     = $5B ' [ 
  ASCII_SEMI   = $3A ' ; 
  ASCII_EQUALS = $3D ' = 
  ASCII_PERIOD = $2E ' .
  ASCII_COMMA  = $2C ' ,
  ASCII_SHARP  = $23 ' #
  ASCII_NULL   = $00 ' null character
  ASCII_SPACE  = $20 ' space
  ASCII_TAB    = $09 ' horizontal tab


  ' box drawing characters
  ASCII_HLINE = 14 ' horizontal line character
  ASCII_VLINE = 15 ' vertical line character

  ASCII_TOPLT = 10 ' top left corner character
  ASCII_TOPRT = 11 ' top right corner character

  ASCII_TOPT  = 16 ' top "t" character
  ASCII_BOTT  = 17 ' bottom "t" character

  ASCII_LTT   = 18 ' left "t" character
  ASCII_RTT   = 19 ' right "t" character

  ASCII_BOTLT = 12 ' bottom left character
  ASCII_BOTRT = 13 ' bottom right character

  ASCII_DITHER = 24 ' dithered pattern for shadows

  NULL         = 0 ' NULL pointer

  ' these are general mutually exclusive flags for assigning certain properties
  ' to objects to alter their visual or functional behavior
  ATTR_NULL        = $00

  ' general graphical rendering attributes for controls and windows
  ATTR_DRAW_SHADOW    = $01
  ATTR_DRAW_SOLID     = $02
  ATTR_DRAW_DASH      = $04
  ATTR_DRAW_BORDER    = $08
  ATTR_DRAW_INVERSE   = $10
  ATTR_DRAW_NORMAL    = $00  

  ' basic white on black theme, looks like a DOS/CMD console terminal, white text on black background
  CTHEME_WHITENBLACK_FG      = %%333
  CTHEME_WHITENBLACK_BG      = %%000
  
  CTHEME_WHITENBLACK_INFO_FG = %%000
  CTHEME_WHITENBLACK_INFO_BG = %%333

  ' basic black on white theme, looks like a modern Windows/Linux/Mac OS window with black text on white background
  CTHEME_BLACKNWHITE_FG      = %%000
  CTHEME_BLACKNWHITE_BG      = %%333
  
  CTHEME_BLACKNWHITE_INFO_FG = %%333
  CTHEME_BLACKNWHITE_INFO_BG = %%000

  ' Atari/C64 theme -- this is white on dark blue like the old 8-bit systems
  CTHEME_ATARI_C64_FG      = %%333
  CTHEME_ATARI_C64_BG      = %%002
  
  CTHEME_ATARI_C64_INFO_FG = %%002
  CTHEME_ATARI_C64_INFO_BG = %%333
  
  ' Apple ][ / Terminal theme - this theme is green text on a black background, reminiscient of old terminals and the Apple ][.
  CTHEME_APPLE2_FG      = %%030
  CTHEME_APPLE2_BG      = %%000
  
  CTHEME_APPLE2_INFO_FG = %%000
  CTHEME_APPLE2_INFO_BG = %%030

  ' wasp/yellow jacket theme - black on yellow background, 
  CTHEME_WASP_FG      = %%000
  CTHEME_WASP_BG      = %%220
  
  CTHEME_WASP_INFO_FG = %%220
  CTHEME_WASP_INFO_BG = %%000

  ' autumn theme  - black on orange background 
  CTHEME_AUTUMN_FG      = %%000
  CTHEME_AUTUMN_BG      = %%310
  
  CTHEME_AUTUMN_INFO_FG = %%310
  CTHEME_AUTUMN_INFO_BG = %%000

  ' creamsicle theme  - white on orange background 
  CTHEME_CREAMSICLE_FG      = %%333
  CTHEME_CREAMSICLE_BG      = %%310
  
  CTHEME_CREAMSICLE_INFO_FG = %%310
  CTHEME_CREAMSICLE_INFO_BG = %%333

  ' purple orchid theme  - white on purple background 
  CTHEME_ORCHID_FG      = %%333
  CTHEME_ORCHID_BG      = %%112
  
  CTHEME_ORCHID_INFO_FG = %%112
  CTHEME_ORCHID_INFO_BG = %%333

  ' gremlin theme  - green on gray background 
  CTHEME_GREMLIN_FG      = %%030
  CTHEME_GREMLIN_BG      = %%111
  
  CTHEME_GREMLIN_INFO_FG = %%111
  CTHEME_GREMLIN_INFO_BG = %%030


  
OBJ
  '---------------------------------------------------------------------------
  ' OBJECTS IMPORTED BY FRAMEWORK 
  '---------------------------------------------------------------------------
  ' there are many VGA text drivers, but this is the simplest and cleanest, plus
  ' its developed by Parallax and is somewhat of a standard.
  
  vga           : "VGA_HiRes_Text_010"


VAR
  long  gVideoBuffer[VGACOLS * VGAROWS / 4]     ' video buffer - could be bytes, but longs allow more efficient scrolling
  long  gVideoBufferPtr                         ' pointer to video buffer
  long  gBackBufferPtr                          ' user can send a "back buffer" to hold screen space overwritten by menuing system
                                                ' this way application doensn't need to refresh screen when menu events occur
                                                ' however, in a really tight application, the user might not be able to spare
                                                ' even a small amount of memory, but, in most cases, menu items are approx 20 characters
                                                ' wide and there are 5-10 menu items, thus the buffer will cost 100-200 bytes
                                                                                                            
  word  gColors[VGAROWS]                        ' row colors
  long  gVsync                                  ' sync long - written to -1 by VGA driver after each screen refresh

  byte  gStrBuffer[64]                          ' generic string buffer

  ' console terminal variables
  long  gTermCol, gTermRow, gTermNumCols, gTermNumRows, gTermAttr, gTermColor, gTermFlag, gTermLasRow


CON
' -----------------------------------------------------------------------------
' INITIALIZATION ENTRY POINT FOR TERMINAL SERVICES DRIVER   
' -----------------------------------------------------------------------------
PUB Init( pVGABasePin, pTextCursXPtr ) | retVal
{{
DESCRIPTION: Initializes the VGA and Keyboard Drivers as well as basic terminal parameters  

PARMS:

   pVGABasePin    - start of 8 consecutive pins where the VGA port is
   pTextCursXPtr  - pointer to start of 6 byte data structure that VGA driver interogates for "text" cursor
                    and "mouse" cursor. The selection of which is text and which is mouse is arbitrary since
                    the driver doesn't know the difference, but we will use the convention that the cursors
                    are text, mouse in that order.

RETURNS:  Returns the screen geometry in high WORD of 32-bit return value
          low byte  = number of character columns
          high byte = number of character rows
}}

  ' initialize any variables here...
  gVideoBufferPtr := @gVideoBuffer

  ' initial terminal settings
  gTermCol       := 0
  gTermRow       := 0
  gTermNumCols   := VGACOLS
  gTermNumRows   := VGAROWS
  gTermFlag      := 0
  
  ' start the VGA driver, send VGA base pins, video buffer, color buffer, pointer to cursors, and vsync global   
  vga.start(pVGABasePin, @gVideoBuffer, @gColors, pTextCursXPtr, @gVsync) 

  ' if you wanted the mouse as well, you would start it here, and then add "pass thru" functions
  ' so you could call it from the upper level object
  
  ' clear the VGA screen to Atari theme
  ClearScreen( CTHEME_ATARI_C64_FG, CTHEME_ATARI_C64_BG )           

  ' finally return the screen geometry in the format [video_buffer:16 | vga_colums:8 | vga_rows]
  retVal :=   (@gVideoBuffer << 16 ) | ( VGAROWS << 8 ) | VGACOLS
  
  return ( retVal )

' end PUB ----------------------------------------------------------------------


CON
' -----------------------------------------------------------------------------
' DIRECT FRAMEBUFFER FUNCTIONS FOR GENERAL RENDERING FOR CONSOLE AND CONTROLS  
' -----------------------------------------------------------------------------

PUB PrintString( pStrPtr, pCol, pRow, pInvFlag ) | strLen, vgaIndex, index
{{
DESCRIPTION: This method draws a string directly to the frame buffer avoiding the
terminal system.  

PARMS:  pStrPtr  - Pointer to string to print, null terminated.
        pCol     - Column(x) position to print (0,0) upper left.
        pRow     - Row(y) position to print.
        pInvFlag - Renders character with inverse video colors; background swapped with foreground color.

RETURNS: Nothing.
}}

  if ( pRow < VGAROWS ) AND ( pCol < VGACOLS )
    strLen := strsize( pStrPtr )
    vgaIndex := pRow * VGACOLS + pCol
    bytemove( gVideoBufferPtr + vgaIndex, pStrPtr, strLen )

  if ( pInvFlag )
    repeat index from 1 to strLen
      byte[gVideoBufferPtr][vgaIndex] += 128
      vgaIndex++

' end PUB ----------------------------------------------------------------------

PUB PrintChar( pChar, pCol, pRow, pInvFlag )
{{
DESCRIPTION: Draws a character directly the the frame buffer avoiding the terminal system.  

PARMS:  pChar    - Character to print.
        pCol     - Column(x) position to print (0,0) upper left.
        pRow     - Row(y) position to print.
        pInvFlag - Renders character with inverse video colors; background swampped with foreground color.

RETURNS: Nothing.
}}

' prints a single character to the screen in "direct mode"
  if ( pRow < VGAROWS ) AND ( pCol < VGACOLS )
    ' check inverse video flag, if so, add 128 for inverse character set
    if (pInvFlag)
      pChar += 128
      
    byte[ gVideoBufferPtr ][pCol + (pRow * gTermNumCols)] := pChar  

' end PUB ----------------------------------------------------------------------


PUB ClearScreen( pFGroundColor, pBGroundColor ) | colorWord
{{
DESCRIPTION: Clear the screen at the memory buffer level, very fast. However, doesn't
effect the terminal sub-system or cursor position, they are independant.   

PARMS:  pFGroundColor - foreground color in RGB[2:2:2] format.
        pBGroundColor - background color in RGB[2:2:2] format.

RETURNS: Nothing.
}}

  ' build color word in proper format
  colorWord := pBGroundColor << 10 + pFGroundColor << 2

  ' clear the screen (long at a time, this is why video buffer needs to be on
  ' long boundary  
  longfill( gVideoBufferPtr, $20202020, VGACOLS*VGAROWS/4 )

  ' clear color control buffer   
  wordfill( @gColors, colorWord, VGAROWS )

' end PUB ----------------------------------------------------------------------

PUB SetLineColor( pRow, pFGroundColor, pBGroundColor ) | colorWord
{{
DESCRIPTION: Sets the sent row to the given foreground and background color. The VGA
driver this framework is connected to VGA_HiRes_Text_*** has only 2 colors per row, but
we can control those colors. We give color up for high resoloution.  

PARMS:  pRow - the row to change the foreground and backgroundf color of.
        pFGroundColor - the foreground color in RGB[2:2:2] format.
        pBGroundColor - the background color in RGB[2:2:2] format.         

RETURNS: Nothing.
}}



  if ( pRow < VGAROWS )
    colorWord := pBGroundColor << 10 + pFGroundColor << 2 
    gColors[ pRow ] := colorWord

' end PUB ----------------------------------------------------------------------

PUB DrawFrame( pCol, pRow, pWidth, pHeight, pTitlePtr, pAttr, pVgaPtr, pVgaWidth ) | index, index2, vgaIndex, rowCount, vgaStartIndex , pWidth_2
{{
DESCRIPTION: This method draws a rectangular "frame" at pCol, pRow directly to the graphics buffer
with size pWidth x pHeight. Also, if pTitlePtr is not null then a title is drawn above the frame in a
smaller frame, so it looks nice and clean.
  
PARMS:

  pCol       - The column to draw the frame at. 
  pRow       - The row to draw the frame at. 
  pWidth     - The overall width of frame.
  pHeight    - The height of the frame.
  pTitlePtr  - ASCIIZ String to print as title or null for no title. 
  pAttr      - Rendering attributes such as shadow, etc. see CON section at top of program for all ATTR_* flags.
               Currently only ATTR_DRAW_SHADOW and ATTR_DRAW_INVERSE are implemented. 
  pVgaPtr    - Pointer to VGA character graphics buffer. 
  pVgaWidth  - Width of VGA screen in bytes, same as number of columns in screen; 40, 64, 80, 100, etc.
  

RETURNS: Nothing.
}}

  vgaStartIndex := pRow * pVgaWidth + pCol

  ' pre-compute this value since its used so much
  pWidth_2 := pWidth-2                           

  ' starting rendering index  
  vgaIndex := vgaStartIndex                      

  ' clear the target rectangle
  repeat pHeight
    bytefill(@byte[pVgaPtr][vgaIndex],32,pWidth)
    vgaIndex += pVgaWidth

  ' reset to top left of box
  vgaIndex := vgaStartIndex                              

  ' draw top left corner, then horizontal line followed by rop right character  
  byte[pVgaPtr][vgaIndex++] := ASCII_TOPLT               
  bytefill(@byte[pVgaPtr][vgaIndex],ASCII_HLINE,pWidth_2) 
  vgaIndex += pWidth_2
  byte[pVgaPtr][vgaIndex++] := ASCII_TOPRT               

  ' move to next row (potentially title will go here)    
  vgaIndex := vgaStartIndex + pVgaWidth              

  ' test if there is a title, if so draw it
  if (pTitlePtr <> NULL AND strsize( pTitlePtr ) > 0)

    ' left vertical line, then title, then right vertical line    
    byte[pVgaPtr][vgaIndex++] := ASCII_VLINE             
    index := strsize( pTitlePtr )

    ' test if caller wants inverted title
    if ( pAttr & ATTR_DRAW_INVERSE )
      repeat index2 from 0 to index-1
        byte[pVgaPtr][vgaIndex+index2] := byte[pTitlePtr][index2]+128   
    else
      bytemove( @byte[pVgaPtr][vgaIndex], pTitlePtr, index )         

    vgaIndex += pWidth_2
    byte[pVgaPtr][vgaIndex++] := ASCII_VLINE              

    ' move down to next row (optimize this *2 later)
    vgaIndex := vgaStartIndex + 2 * pVgaWidth             

    ' if a title was inserted, then we need to draw the "tee" characters
    ' on the left and right to finish this off

    ' draw left "tee" horizontal line, then right "tee"
    byte[pVgaPtr][vgaIndex++] := ASCII_LTT             
    bytefill(@byte[pVgaPtr][vgaIndex],ASCII_HLINE,pWidth_2) 
    vgaIndex += pWidth_2
    byte[pVgaPtr][vgaIndex++] := ASCII_RTT               

    ' adjust the row counter since we had this added title section    
    rowCount := 3                                         

    ' draw shadow on box?
    if (pAttr & ATTR_DRAW_SHADOW)                          
      byte[pVgaPtr][vgaIndex] := ASCII_DITHER               
    
  else ' don't adjust row counter, draw the box as usual
    rowCount := 1                                       

  ' taking row counter into consideration, move to next row and finish drawing
  ' left and right sides of box
  vgaIndex := vgaStartIndex + pVgaWidth * rowCount           

  ' draw the sides and vertical characters
  repeat pHeight - rowCount - 1
    byte[pVgaPtr][vgaIndex++] := ASCII_VLINE              'vertical line char
    vgaIndex += pWidth_2
    byte[pVgaPtr][vgaIndex++] := ASCII_VLINE              'vertical line char

    ' draw shadw on box?
    if (pAttr & ATTR_DRAW_SHADOW)                          
      byte[pVgaPtr][vgaIndex] := ASCII_DITHER                 

    ' adjust current position for rendering, back to left side of next and final row
    vgaIndex -= pWidth
    vgaIndex += pVgaWidth

  'the above left vgaIndex pointing to the start of the last line

  ' draw the last line on the bottom of box which consists
  ' of the bottom left corner char, then the horizontal line char
  ' and finally the bottom right corner char 
    
  byte[pVgaPtr][vgaIndex++] := ASCII_BOTLT                
  bytefill(@byte[pVgaPtr][vgaIndex],ASCII_HLINE,pWidth_2) 
  vgaIndex += pWidth_2
  byte[pVgaPtr][vgaIndex++] := ASCII_BOTRT                

  ' finally shadow?
  if (pAttr & ATTR_DRAW_SHADOW)                        
    byte[pVgaPtr][vgaIndex]  := ASCII_DITHER               
    vgaIndex += (pVgaWidth - pWidth + 2)
    bytefill(@byte[pVgaPtr][vgaIndex],ASCII_DITHER,pWidth-1)

' end PUB ----------------------------------------------------------------------


CON
' -----------------------------------------------------------------------------
' TEXT CONSOLE/TERMINAL FUNCTIONS - THESE FUNCTIONS CAN BE CALLED MUCH LIKE THE  
' OTHER TERMINAL DRIVERS FOR HIGH LEVEL PRINTING WITH "CONSOLE" EMULATION
' -----------------------------------------------------------------------------

PUB StringTermLn( pStringPtr )
{{
DESCRIPTION: Prints a string to the terminal and appends a newline.  

PARMS: pStrPtr - Pointer to null terminated string to print.

RETURNS: Nothing.
}}

  ' Print a zero-terminated string to terminal and newline
  StringTerm( pStringPtr )
  NewlineTerm

' end PUB ----------------------------------------------------------------------

PUB StringTerm( pStringPtr )
{{
DESCRIPTION: Prints a string to the terminal.  

PARMS: pStrPtr - Pointer to null terminated string to print.

RETURNS: Nothing.
}}

  ' Print a zero-terminated string to terminal
  repeat strsize( pStringPtr)
    OutTerm(byte[ pStringPtr++])

' end PUB ----------------------------------------------------------------------

PUB DecTerm( pValue, pDigits) | divisor, dividend, zFlag, digit
{{
DESCRIPTION: Prints a decimal number to the screen.  

PARMS:  pValue - the number to print.
        pDigits - the maximum number of digits to print.

RETURNS: Nothing.
}}

  ' check for 0
  if (pValue == 0)
    PrintTerm("0")
    return

  ' check for negative
  if (pValue < 0)
    pValue := -pValue
    PrintTerm("-")    

  ' generate divisor
  divisor := 1
    
  repeat (pDigits-1)
    divisor *= 10 
   
  ' pBase 10, only mode where leading 0's are not copied to string
  zFlag := 1
   
  repeat digit from 0 to (pDigits-1)
    ' print with pBase 10
   
    dividend := (pValue / divisor)
   
    if (dividend => 1)
      zFlag := 0
   
    if (zFlag == 0)
      PrintTerm( dividend + "0")
   
    pValue := pValue // divisor
    divisor /= 10
   
  
' end PUB ----------------------------------------------------------------------

PUB HexTerm(pValue, pDigits)
{{
DESCRIPTION: Prints the sent number in hex format.  

PARMS:  pValue  - the number to print in hex format.
        pDigits - the number of hex digits to print.

RETURNS: Nothing.
}}

  ' shift the value into place
  pValue <<= (8 - pDigits) << 2

  repeat pDigits
    PrintTerm(lookupz((pValue <-= 4) & $F : "0".."9", "A".."F"))

' end PUB ----------------------------------------------------------------------

PUB BinTerm(pValue, pDigits)
{{
DESCRIPTION: Prints the sent value in binary format with 0's and 1's.  

PARMS:  pValue - the number to print in binary format.
        pDigits - the number binary digits to print.

RETURNS: Nothing.
}}

  ' shift the value into place
  pValue <<= 32 - pDigits

  repeat pDigits
    PrintTerm((pValue <-= 1) & 1 + "0")

' end PUB ----------------------------------------------------------------------

PUB NewlineTerm
{{
DESCRIPTION: Moves the terminal cursor home and outputs a carriage return.  

PARMS: None.
 
RETURNS: Nothing.
}}

  ' reset terminal column
  gTermCol := 0

  if (++gTermRow => gTermNumRows)
    gTermRow--

    'scroll lines
    bytemove(gVideoBufferPtr, gVideoBufferPtr + gTermNumCols, ( (gTermNumRows-1) * gTermNumCols )  )

   'clear new line                             
    bytefill(gVideoBufferPtr + ((gTermNumRows-1) * gTermNumCols), ASCII_SPACE, gTermNumCols)

' end PUB ----------------------------------------------------------------------
       
PUB PrintTerm( pChar )
{{
DESCRIPTION: Prints the sent character to the terminal console with scrolling.  

PARMS: pChar - character to print.

RETURNS: Nothing.
}}

  ' print a character at current cursor position
  byte[ gVideoBufferPtr ][ gTermCol + (gTermRow * gTermNumCols)] := pChar

  ' check for scroll  
  if (++gTermCol == gTermNumCols)
    NewlineTerm

' end PUB ----------------------------------------------------------------------

PUB OutTerm( pChar )
{{
DESCRIPTION: Output a character to terminal, this is the primary interface from the client to the driver in "terminal mode"
direct mode access uses the register model and controls the engine from the low level

PARMS: pChar - character to print with the following extra controls:


     $00 = Null - can't be represented by a string
     $01 = clear screen
     $02 = home
     $08 = backspace
     $09 = tab (8 spaces per)
     $0A = set X position (X + 14 follows)
     $0B = set Y position (Y + 14 follows)
     $0C = set color (color follows)
     $0D = return - but can't be passed in a string from serial
     $0E = return
     others = prints to the screen

     +128 to any other printable character, draw in inverse video

RETURNS: Nothing.
}}

  case gTermFlag
    $00: case pChar
           $00..$01: bytefill( gVideoBufferPtr, ASCII_SPACE, gTermNumCols * gTermNumRows)
                    gTermCol := gTermRow := 0

           $02: gTermCol := gTermRow := 0
           

           $08: if gTermCol
                  gTermCol--

           $09: repeat
                  PrintTerm(" ")
                while gTermCol & 7

           $0A..$0C: gTermFlag := pChar
                     return

           '$0D: NewlineTerm
           
           $0E: NewlineTerm

           other: PrintTerm( pChar )
           
    $0A: gTermCol := (pChar-14) // gTermNumCols
    $0B: gTermRow := (pChar-14)// gTermNumRows
    $0C: gTermFlag := pChar & 7

  gTermFlag := 0

' end PUB ----------------------------------------------------------------------


PUB SetColTerm( pCol )
{{
DESCRIPTION: Set terminal x column cursor position.   

PARMS: pRow - row to set the cursor to.

RETURNS: Nothing.
}}

  gTermCol := pCol // gTermNumCols 

' end PUB ----------------------------------------------------------------------

PUB SetRowTerm( pRow )
{{
DESCRIPTION: Set terminal y row cursor position  

PARMS: pRow - row to set the cursor to.

RETURNS: Nothing.
}}

  gTermRow := pRow// gTermNumRows 

' end PUB ----------------------------------------------------------------------

PUB GotoXYTerm( pCol, pRow )
{{
DESCRIPTION: Sets the x column and y row position of terminal cursor.  

PARMS: none.

RETURNS: Nothing.
}}


' set terminal x/column cursor position
  gTermCol := pCol // gTermNumCols 

' set terminal y/row cursor position
  gTermRow := pRow// gTermNumRows 

' end PUB ----------------------------------------------------------------------

PUB GetColTerm
' retrieve x column cursor position 
{{
DESCRIPTION: Retrieve x terminal cursor position  

PARMS: none.

RETURNS: x terminal cursor position.
}}
  return( gTermCol )

' end PUB ----------------------------------------------------------------------

PUB GetRowTerm
{{ 
DESCRIPTION: Retrieve y row terminal cursor position  

PARMS: none.

RETURNS: y terminal cursor position.
}}

  return( gTermRow ) 

' end PUB ----------------------------------------------------------------------


CON
' -----------------------------------------------------------------------------
' STRING AND NUMERIC CONVERSION FUNCTIONS   
' -----------------------------------------------------------------------------

PUB StrCpy( pDestStrPtr, pSourceStrPtr ) | strIndex
{{
DESCRIPTION: Copies the NULL terminated source string to the destination string
and null terminates the copy. 

PARMS:  pDestStrPtr - destination string storage for string copy.
        pSrcStrPtr  - source string to copy, must be null terminated.

RETURNS: Number of bytes copied.
}}

' test if there is storage
if ( pDestStrPtr == NULL)
  return (NULL)

strIndex := 0

repeat while (byte [ pSourceStrPtr ][ strIndex ] <> NULL)
  ' copy next byte
   byte [ pDestStrPtr ][ strIndex ] := byte [ pSourceStrPtr ][ strIndex ]    
   strIndex++

' null terminate
byte [ pDestStrPtr ][ strIndex ] := NULL

' return number of bytes copied
return ( strIndex )

' end PUB ----------------------------------------------------------------------

PUB StrUpper( pStringPtr )
{{
DESCRIPTION: Converts the sent string to all uppercase. 

PARMS: pStringPtr - NULL terminated ASCII string to convert.  

RETURNS: pStringPtr converted to uppercase.
}}

  if ( pStringPtr <> NULL)
    repeat while (byte[ pStringPtr ] <> NULL)
      byte[ pStringPtr ] :=  ToUpper( byte[ pStringPtr ] )
      pStringPtr++  

  ' return string
  return ( pStringPtr )

' end PUB ----------------------------------------------------------------------

PUB ToUpper( pChar )
{{
DESCRIPTION: Returns the uppercase of the sent character.

PARMS:  pChar - character to convert to uppercase.

RETURNS: The uppercase version of the character.
}}

if ( pChar => $61 and pChar =< $7A)
  return( pChar - 32 )
else
  return( pChar )

' end PUB ----------------------------------------------------------------------

PUB IsInSet(pChar, pSetStringPtr)
{{
DESCRIPTION: Tests if sent character is in sent string.

PARMS:  pChar         - character to test for set inclusion.
        pSetStringPtr - string to test for character.
        
RETURNS: pChar if its in the string set, -1 otherwise. Note to self, maybe
later make this return the position of the 1st occurance, more useful?
}}

repeat while (byte[ pSetStringPtr ] <> NULL)
  if ( pChar == byte[ pSetStringPtr++ ])
    return( pChar )

' not found
return( -1 )    

' end PUB ----------------------------------------------------------------------

PUB IsSpace( pChar )
{{
DESCRIPTION: Tests if sent character is white space, cr, lf, space, or tab.

PARMS: pChar - character to test for white space.

RETURNS: pChar if its a white space character, -1 otherwise.
}}

if ( (pChar == ASCII_SPACE) OR (pChar == ASCII_LF) OR (pChar == ASCII_CR) or (pChar == ASCII_TAB))
  return ( pChar )
else
  return( -1 )  

' end PUB ----------------------------------------------------------------------

PUB IsNull( pChar )
{{
DESCRIPTION: Tests if sent character is NULL, 0.

PARMS: pChar - character to test.

RETURNS: 1 if pChar is NULL, -1 otherwise.
}}

if ( ( pChar == NULL))
  return ( 1 )
else
  return( -1 )  

' end PUB ----------------------------------------------------------------------

PUB IsDigit( pChar )
{{
DESCRIPTION: Tests if sent character is an ASCII number digit [0..9], returns integer [0..9]

PARMS: pChar - character to test.

RETURNS: pChar if its in the ASCII set [0..9], -1 otherwise.
}}

if ( (pChar => ASCII_0) AND (pChar =< ASCII_9) )
  return ( pChar-ASCII_0 )
else
  return(-1)  

' end PUB ----------------------------------------------------------------------

PUB IsAlpha( pChar )
{{
DESCRIPTION: Tests if sent character is in the set [a...zA...Z].
Useful for text processing and parsing.

PARMS: pChar - character to test.

RETURNS: pChar if the sent character is in the set [a...zA....Z] or -1 otherwise.
}}

' first convert to uppercase to simplify testing
pChar := ToUpper( pChar )

if ( (pChar => ASCII_A) AND (pChar =< ASCII_Z))
  return ( pChar )
else
  return( -1 )  

' end PUB ----------------------------------------------------------------------

PUB IsPunc( pChar )
{{
DESCRIPTION: Tests if sent character is a punctuation symbol !@#$%^&*()--+={}[]|\;:'",<.>/?.
Helpful for parser and string processing in general.

PARMS: pChar - ASCII character to test if its in the set of punctuation characters.

RETURNS: pChar itself if its in the set, -1 if its not in the set.
}}

pChar := ToUpper( pChar )

if ( ((pChar => 33) AND (pChar =< 47)) OR ((pChar => 58) AND (pChar =< 64)) OR ((pChar => 91) AND (pChar =< 96)) OR ((pChar =>123) AND (pChar =< 126))  ) 
  return ( pChar )
else
  return( -1 )  

' end PUB ----------------------------------------------------------------------


PUB HexToDec( pChar )
{{
DESCRIPTION: Converts ASCII hex digit to decimal.

PARMS: ASCII hex digit ["0"..."9", "A..."F"|"a"..."f"]

RETURNS:
}} 
  if ( (pChar => "0") and (pChar =< "9") )
    return (pChar - ASCII_0)
  elseif ( (pChar => "A") and (pChar =< "F") )
    return (pChar - "A" + 10)
  elseif ( (pChar => "a") and (pChar =< "f") )
    return (pChar - "a" + 10)
  else
    return ( 0 )  

' end PUB ----------------------------------------------------------------------

PUB HexToASCII( pValue )
{{
DESCRIPTION: ' converts a number 0..15 to ASCII 0...9, A, B, C, D, E, F. There
should be a better way to do this with lookupz etc., note to self check that out.

PARMS:  pValue - The hex digit value to convert to ASCII digit.

RETURNS: The converted ASCII digit. 

}}
{
  if (pValue > 9)
    return ( pValue + "A" - 10 )
  else
    return( pValue + "0" )
}   
return ( lookupz( (pValue & $F) : "0".."9", "A".."F") )


' end PUB ----------------------------------------------------------------------

PUB itoa(pNumber, pBase, pDigits, pStringPtr) | divisor, digit, zflag, dividend
{{
DESCRIPTION: "C-like" method that converts pNumber to string; decimal, hex, or binary formats. Caller
should make sure that conversion will fit in string, otherwise method will overwrite
data.        

PARMS:  pNumber - number to convert to ASCII string.
        pBase   - base for conversion; 2, 10, 16, for binary, decimal, and hex respectively.

RETURNS: Pointer back to the pStringPtr with the converted results.
}}

  ' clear result string
  bytefill( pStringPtr, " ", pDigits)

  ' check for negative
  if (pNumber < 0)
    pNumber := -pNumber
    byte [pStringPtr++] := "-"


  ' pBase 2 code --------------------------------------------------------------
  if (pBase == 2)
    ' print with pBase 2,  bit pNumber
    divisor := 1 << (pDigits-1) ' initialize bitmask
    
    repeat digit from 0 to (pDigits-1)
      ' print with pBase 2
      byte [pStringPtr++] := ((pNumber & divisor) >> ( (pDigits-1) - digit) + "0")
      divisor >>= 1

  ' pBase 10 code --------------------------------------------------------------
  elseif (pBase == 10)

    ' check for 0
    if (pNumber == 0)
      byte [pStringPtr++] := "0"
    else

      ' generate divisor
      divisor := 1
      repeat (pDigits-1)
        divisor *= 10 
       
      ' pBase 10, only mode where leading 0's are not copied to string
      zflag~~
       
      repeat digit from 0 to (pDigits-1)
        ' print with pBase 10
       
        dividend := (pNumber / divisor)
       
        if (dividend => 1)
          zflag~
       
        if (zflag == 0)
          byte [pStringPtr++] := (dividend + "0")
       
        pNumber := pNumber // divisor
        divisor /= 10

  ' pBase 16 code --------------------------------------------------------------       
  else  
    divisor := $F << (4*(pDigits-1))  

    repeat digit from 0 to (pDigits-1)
      ' print with pBase 16
      byte [pStringPtr++] := (HexToASCII ((pNumber & divisor) >> (( (pDigits-1) - digit)*4)))
      divisor >>= 4

   ' null terminate and return
   byte [pStringPtr] := 0
      
   return( pStringPtr )

  ' end PUB ----------------------------------------------------------------------  

PUB atoi(pStringPtr, pLength) | index, sum, ch, sign
{{
DESCRIPTION: "C-like" method that tries to convert the string to a number, supports binary %, hex $, decimal (default)
pStringPtr can be to a null terminated string, or the pLength can be overridden by sending the pLength shorter
than the null terminator, ignores white space

Eg. %001010110, $EF, 25

PARMS:  pStringPtr - NULL terminated string to attempt numerical conversion.
        pLength    - Maximum length to process of string, if less than length of pStringPtr processing stops early.

RETURNS: The value of the converted number or 0 if conversion couldn't be completed. Of course, the converted
number could be 0, so this is misleading. A better idea might be to use a very large integer, such as +-2 billion
however, if the user assigns this method to a byte then that would be lost as well. Thus, be smart when using
this method!
}}

' initialize vars
index := 0
sum   := 0
sign  := 1
 
' consume white space
repeat while (IsSpace( byte[ pStringPtr ][index] ) <> -1)
  index++
 
' is there a +/- sign?
if (byte [pStringPtr][index] == "+")
  ' consume it
  index++
elseif (byte [pStringPtr][index] == "-")
  ' consume it
  index++
  sign := -1    
     
' try to determine number base
if (byte [pStringPtr][index] == ASCII_HEX)
  index++
  repeat while ( ( IsDigit(ch := byte [pStringPtr][index]) <> -1) or ( IsAlpha(ch := byte [pStringPtr][index]) <> -1)  )
    index++
    sum := (sum << 4) + HexToDec( ToUpper(ch) )
    if (index => pLength)
      return (sum*sign)
 
  return(sum*sign)
' // end if hex number    
elseif (byte [pStringPtr][index] == ASCII_BIN)
  repeat while ( IsDigit(ch := byte [pStringPtr][++index]) <> -1)
    sum := (sum << 1) + (ch - ASCII_0)
    if (index => pLength)
      return (sum*sign)
 
  return(sum*sign)
' // end if binary number  
else
  ' must be in default base 10, assume that
  repeat while ( IsDigit(ch := byte [pStringPtr][index++]) <> -1)
    sum := (sum * 10) + (ch - ASCII_0)
    if (index => pLength)
      return (sum*sign)
 
  return(sum*sign)
 
' else, have no idea of number format!
return( 0 )
 
' end PUB ----------------------------------------------------------------------


PUB DelayMilliSec( pTime )
{{
DESCRIPTION: Delays "time" milliseconds and returns.

PARMS: pTime - number of millseconds to delay.

RETURNS: nothing.                                       
}}

  waitcnt (cnt + pTime*CLOCKS_PER_MILLISECOND)

' end PUB ----------------------------------------------------------------------

PUB DelayMicroSec( pTime )
{{
DESCRIPTION: Delays "time" microseconds and returns.

PARMS: pTime - number of microseconds to delay.

RETURNS: nothing.
}}

  waitcnt (cnt + pTime*CLOCKS_PER_MICROSECOND)

' end PUB ----------------------------------------------------------------------

{{
┌────────────────────────────────────────────────────────────────────────────┐
│                     TERMS OF USE: MIT License                              │                                                            
├────────────────────────────────────────────────────────────────────────────┤
│Permission is hereby granted, free of charge, to any person obtaining a copy│
│of this software and associated documentation files (the "Software"), to    │
│deal in the Software without restriction, including without limitation the  │
│rights to use, copy, modify, merge, publish, distribute, sublicense, and/or │
│sell copies of the Software, and to permit persons to whom the Software is  │
│furnished to do so, subject to the following conditions:                    │
│                                                                            │
│The above copyright notice and this permission notice shall be included in  │
│all copies or substantial portions of the Software.                         │
│                                                                            │
│THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  │
│IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    │
│FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE │
│AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      │
│LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     │
│FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS│
│IN THE SOFTWARE.                                                            │
└────────────────────────────────────────────────────────────────────────────┘
}}


    
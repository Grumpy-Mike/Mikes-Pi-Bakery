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

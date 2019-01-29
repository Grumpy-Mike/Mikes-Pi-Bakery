'' ===========================================================================
''  File: HelloPi.Spin
''  Mike Cook 
'' ===========================================================================
CON
' CONSTANTS, DEFINES, MACROS, ETC.   
  _clkmode = xtal1 + pll16x
  _xinfreq = 5_000_000
  RxPin = 31     'default boot loader RX
  TxPin = 30     'default boot loader TX
  BaudRate = 115200 'this is a good baud rate for 80MHz

  ' import some constants from the Propeller Window Manager
  VGACOLS = WMF#VGACOLS
  VGAROWS = WMF#VGAROWS

  ' set these constants based on the Propeller device you are using
  VGA_BASE_PIN      = 16        'VGA pins 16-23

OBJ
  ' Propeller Windows GUI object(s) 
  SerIO : "FullDuplexSerialPlus" 'object that implements serial I/O for the Propeller.
  WMF   : "WMF_Terminal_Services_010" ' include the terminal services driver which includes the VGA driver itself 

VAR
' DECLARED VARIABLES, ARRAYS

  byte  gVgaRows, gVgaCols ' convenient globals to store number of columns and rows
  byte  gStrBuff1[64]      ' a string buffers  
  byte  gTextCursX, gTextCursY, gTextCursMode        ' text cursor 0 [x0,y0,mode0]  
  long  gVideoBufferPtr                              ' holds the address of the video buffer passed back from the VGA driver 

CON
' MAIN ENTRY POINT   
PUB Start | S1, N1, CF, CB

  ' create the GUI itself
  CreateAppGUI
  SerIO.Start(RxPin, TxPin, %0000, BaudRate) ' initialise SerIO object 

  ' MAIN EVENT LOOP
  WMF.StringTerm(string("Hello World! from the Propeller ")) 
  repeat
      S1 := SerIO.getstr(gStrBuff1)
      N1 := byte[gStrBuff1][0] 
      if N1 == $0C
        CF := byte[gStrBuff1][1] & $3F
        CB := byte[gStrBuff1][2] & $3F
        WMF.SetLineColor(WMF.GetRowTerm , CF, CB )
      else    
        WMF.StringTerm(S1)
      SerIO.tx (2) ' send an ACK to say that has beed processed 
 
' end PUB ---------------------------------------------------------------------

PUB CreateAppGUI | retVal 
' This functions creates the entire user interface for the application 
  ' start the VGA driver and terminal services 
  retVal := WMF.Init(VGA_BASE_PIN, @gTextCursX )

  ' VGA buffer encoded in upper 16-bits of return value
  gVideoBufferPtr := retVal >> 16 

  'setup screen colors - see Terminal Services themes
  WMF.ClearScreen( WMF#CTHEME_ATARI_C64_FG, WMF#CTHEME_ATARI_C64_BG )
  'WMF.ClearScreen( WMF#CTHEME_AUTUMN_FG, WMF#CTHEME_AUTUMN_BG )
  return
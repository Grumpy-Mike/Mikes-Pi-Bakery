#ifndef __SS_OLED_H__
#define __SS_OLED_H__

#include "BitBang_I2C.h"

typedef struct ssoleds
{
uint8_t oled_addr; // requested address or 0xff for automatic detection
uint8_t oled_wrap, oled_flip, oled_type;
uint8_t *ucScreen;
uint8_t iCursorX, iCursorY;
uint8_t oled_x, oled_y;
int iScreenOffset;
BBI2C bbi2c;
} SSOLED;
// Make the Linux library interface C instead of C++
#if defined(__cplusplus)
extern "C" {
#endif

// 4 possible font sizes: 8x8, 16x32, 6x8, 16x16 (stretched from 8x8)
enum {
   FONT_6x8 = 0,
   FONT_8x8,
   FONT_12x16,
   FONT_16x16,
   FONT_16x32
};
#define FONT_NORMAL FONT_8x8
#define FONT_SMALL FONT_6x8
#define FONT_LARGE FONT_16x32
#define FONT_STRETCHED FONT_16x16

// OLED type for init function
enum {
  OLED_128x128 = 1,
  OLED_128x32,
  OLED_128x64,
  OLED_132x64,
  OLED_64x32,
  OLED_96x16,
  OLED_72x40
};

// Rotation and flip angles to draw tiles
enum {
  ANGLE_0=0,
  ANGLE_90,
  ANGLE_180,
  ANGLE_270,
  ANGLE_FLIPX,
  ANGLE_FLIPY
};

// Return value from oledInit()
enum {
  OLED_NOT_FOUND = -1, // no display found
  OLED_SSD1306_3C,  // SSD1306 found at 0x3C
  OLED_SSD1306_3D,  // SSD1306 found at 0x3D
  OLED_SH1106_3C,   // SH1106 found at 0x3C
  OLED_SH1106_3D,   // SH1106 found at 0x3D
  OLED_SH1107_3C,  // SH1107
  OLED_SH1107_3D
};
//
// Initializes the OLED controller into "page mode" on I2C
// If SDAPin and SCLPin are not -1, then bit bang I2C on those pins
// Otherwise use the Wire library.
// If you don't need to use a separate reset pin, set it to -1
//
int oledInit(SSOLED *pOLED, int iType, int iAddr, int bFlip, int bInvert, int bWire, int sda, int scl, int reset, int32_t iSpeed);

//
// Provide or revoke a back buffer for your OLED graphics
// This allows you to manage the RAM used by ss_oled on tiny
// embedded platforms like the ATmega series
// Pass NULL to revoke the buffer. Make sure you provide a buffer
// large enough for your display (e.g. 128x64 needs 1K - 1024 bytes)
//
void oledSetBackBuffer(SSOLED *pOLED, uint8_t *pBuffer);

//
// Sets the brightness (0=off, 255=brightest)
//
void oledSetContrast(SSOLED *pOLED, unsigned char ucContrast);

//
// Load a 128x64 1-bpp Windows bitmap
// Pass the pointer to the beginning of the BMP file
// First pass version assumes a full screen bitmap
//
int oledLoadBMP(SSOLED *pOLED, uint8_t *pBMP, int bInvert, int bRender);

//
// Power up/down the display
// useful for low power situations
//
void oledPower(SSOLED *pOLED, uint8_t bOn);

//
// Set the current cursor position
// The column represents the pixel column (0-127)
// The row represents the text row (0-7)
//
void oledSetCursor(SSOLED *pOLED, int x, int y);

//
// Turn text wrap on or off for the oldWriteString() function
//
void oledSetTextWrap(SSOLED *pOLED, int bWrap);

//
// Draw a string of normal (8x8), small (6x8) or large (16x32) characters
// At the given col+row with the given scroll offset. The scroll offset allows you to
// horizontally scroll text which does not fit on the width of the display. The offset
// represents the pixels to skip when drawing the text. An offset of 0 starts at the beginning
// of the text.
// The system remembers where the last text was written (the cursor position)
// To continue writing from the last position, set the x,y values to -1
// The text can optionally wrap around to the next line by calling oledSetTextWrap(true);
// otherwise text which would go off the right edge will not be drawn and the cursor will
// be left "off screen" until set to a new position explicitly
//
//  Returns 0 for success, -1 for invalid parameter
//
int oledWriteString(SSOLED *pOLED, int iScrollX, int x, int y, char *szMsg, int iSize, int bInvert, int bRender);

//
// Fill the frame buffer with a byte pattern
// e.g. all off (0x00) or all on (0xff)
//
void oledFill(SSOLED *pOLED, unsigned char ucData, int bRender);

//
// Set (or clear) an individual pixel
// The local copy of the frame buffer is used to avoid
// reading data from the display controller
// (which isn't possible in most configurations)
// This function needs the USE_BACKBUFFER macro to be defined
// otherwise, new pixels will erase old pixels within the same byte
//
int oledSetPixel(SSOLED *pOLED, int x, int y, unsigned char ucColor, int bRender);

//
// Dump an entire custom buffer to the display
// useful for custom animation effects
//
void oledDumpBuffer(SSOLED *pOLED, uint8_t *pBuffer);

//
// Render a window of pixels from a provided buffer or the library's internal buffer
// to the display. The row values refer to byte rows, not pixel rows due to the memory
// layout of OLEDs. Pass a src pointer of NULL to use the internal backing buffer
// returns 0 for success, -1 for invalid parameter
//
int oledDrawGFX(SSOLED *pOLED, uint8_t *pSrc, int iSrcCol, int iSrcRow, int iDestCol, int iDestRow, int iWidth, int iHeight, int iSrcPitch);

//
// Draw a line between 2 points
//
void oledDrawLine(SSOLED *pOLED, int x1, int y1, int x2, int y2, int bRender);

//
// Play a frame of animation data
// The animation data is assumed to be encoded for a full frame of the display
// Given the pointer to the start of the compressed data,
// it returns the pointer to the start of the next frame
// Frame rate control is up to the calling program to manage
// When it finishes the last frame, it will start again from the beginning
//
uint8_t * oledPlayAnimFrame(SSOLED *pOLED, uint8_t *pAnimation, uint8_t *pCurrent, int iLen);

//
// Scroll the internal buffer by 1 scanline (up/down)
// width is in pixels, lines is group of 8 rows
// Returns 0 for success, -1 for invalid parameter
//
int oledScrollBuffer(SSOLED *pOLED, int iStartCol, int iEndCol, int iStartRow, int iEndRow, int bUp);

//
// Draw a sprite of any size in any position
// If it goes beyond the left/right or top/bottom edges
// it's trimmed to show the valid parts
// This function requires a back buffer to be defined
// The priority color (0 or 1) determines which color is painted 
// when a 1 is encountered in the source image.
// e.g. when 0, the input bitmap acts like a mask to clear
// the destination where bits are set.
//
void oledDrawSprite(SSOLED *pOLED, uint8_t *pSprite, int cx, int cy, int iPitch, int x, int y, uint8_t iPriority);

//
// Draw a 16x16 tile in any of 4 rotated positions
// Assumes input image is laid out like "normal" graphics with
// the MSB on the left and 2 bytes per line
// On AVR, the source image is assumed to be in FLASH memory
// The function can draw the tile on byte boundaries, so the x value
// can be from 0 to 112 and y can be from 0 to 6
//
void oledDrawTile(SSOLED *pOLED, const uint8_t *pTile, int x, int y, int iRotation, int bInvert, int bRender);

//
// Draw an outline or filled ellipse
//
void oledEllipse(SSOLED *pOLED, int iCenterX, int iCenterY, int32_t iRadiusX, int32_t iRadiusY, uint8_t ucColor, uint8_t bFilled);

//
// Draw an outline or filled rectangle
//
void oledRectangle(SSOLED *pOLED, int x1, int y1, int x2, int y2, uint8_t ucColor, uint8_t bFilled);

#if defined(__cplusplus)
}
#endif

#endif // __SS_OLED_H__


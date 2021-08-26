# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython

import time
import board
import busio
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

'''
try:
    i2c = busio.I2C (scl=board.GP15, sda=board.GP14) # This RPi Pico way to call I2C
except:
    print("this means pins in use")


except:
    board.GP15.destroy()
    board.GP14.destroy()
'''    
#board.GP15.destroy()
#board.GP14.destroy() 
    
i2c = busio.I2C (scl=board.GP15, sda=board.GP14) # This RPi Pico way to call I2C


display_bus = displayio.I2CDisplay (i2c, device_address = 0x3C) # The address of my Board


display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
splash = displayio.Group(max_size=10)
display.show(splash)

#time.sleep(3.0)
color_bitmap = displayio.Bitmap(128, 64, 1) # Full screen white
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White
 
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)
 
# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(118, 54, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
splash.append(inner_sprite)
time.sleep(3.0)
 
# Draw a label
text = "Mike"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=20)
splash.append(text_area)

time.sleep(3.0)
text = "Cook"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=30)
splash.append(text_area)
time.sleep(5.0)
text_area = label.Label(terminalio.FONT, text="is", color=0xFFFF00, x=38, y=30)

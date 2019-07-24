#!/usr/bin/env python3
# Needs to run in supervisor mode
import time , board, neopixel

pixel_pin = board.D18
num_pixels = 184 # make this 11 for track section test
# RGB or GRB. Some NeoPixels have red and green reversed
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.15,
                         auto_write=False, pixel_order=ORDER)
print("Neopixel LED test")
while True:
    for i in range(num_pixels):
       pixels[i] = (128,128,128)
       pixels.show()
       time.sleep(0.1)
       pixels.fill((0, 0, 0))


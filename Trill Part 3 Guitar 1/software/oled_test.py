'''
Tests display-ssd1306-test.py
see the tutorial at:- 
  DroneBot Workshop 2021
  https://dronebotworkshop.com
Or in Thonny go to menu Tools -> Manage plug-ins
put in ssd1360 and click search on PyPi
Click on the micropython-ssd1327
Finally click on "Install"
''' 
import machine
import utime
from ssd1306 import SSD1306_I2C

sda=machine.Pin(16)
scl=machine.Pin(17) 
i2c = machine.I2C(0, sda=sda, scl=scl, freq=100000) 
oled = SSD1306_I2C(128, 64, i2c) # define size of display
  
print("found address", i2c.scan()) # see if it attached to the I2C bus
oled.fill(1)
oled.show()
utime.sleep(2)
count = 0 
while True:
    count = (count + 1) & 0xFF # count up to 255
    oled.text("Hello World   ", 0, 0)
    oled.text('Pi Pico', 0, 16)
    oled.text('Display test', 0, 25)
    oled.fill_rect(0, 35, 24, 11, 0)
    oled.text(str(count), 0, 35)
    oled.show()
    utime.sleep(0.01)
    oled.fill(0)

Using the TraxScript.py program.

Sounds:-
In a script each sound is defined by a number. These are derived from the soundNames list in the loadResources function.
The sound numbers / names are here as a handy reference:-
number sound name
0 - "owl", 
1 - "Breaking Glass",
2 - "ComputerBeeps1",
3 - "CymbalCrash",
4 - "Fairydust", 
5 - "Dog1",
6 - "Zoop", 
7 - "Ya",
8 - "Pop", 
9 - "Duck", 
10 - "Gong",
11 - "Laser1",
12 - "Laser2", 
13 - "running", 
14 - "Screech",
15 - "SpaceRipple", 
16 - "Zoop",
17 - "Dog2",
18 - "DirtyWhir", 
19 - "ComputerBeeps2",
20 - "AlienCreak2", 
21 - "AlienCreak1"
To add your own .wav sounds place them in the sounds directory, and add the name to the end of the the soundNames list in quotes and without the .wav file extension. Then they will appear as sound numbers greater than 21.

FL3731 LED modules:-
When the FL3731_Thread file is first activated the I2C bus is scanned to see what devices are connected to the Raspberry Pi. A message is printed out saying at what I2C addresses nothing is found. Each device found is allocated a "device number" from the actual I2C address. It is this device address that is used in the FL3731_Thread functions.
I2C Address  Device number
0x74		0
0x75		1 - the only address an LED shim can have
0x76		2
0x77		3

The startFL3731Thread function calls up an animation routine according to the number passed to it. When a thread calls an animation routine the first parameter passed to it is the device number. For example:-
if number == 0:
        matrix_thread0 = threading.Thread(target =
                   spinC, args = (2, 0.008, 0.1, 0.01))
Calls up the function spinC and passes to it four numbers. The device number in this case is 2, to change this to work on any other device number simply change the 2 to a number between 0 and 3. If you call a thread that uses a device number that does not exist then the TraxScript.py program will crash with an error message in the Python console.

It is simple to add more threads by repeating the pattern of code in the startFL3731Thread function and more functions to do different animations. Oddly enough I found that you can pass no values to a thread or many, but for some reason passing only one results in an error.

WS2812 or Neopixel LED module:-
The startWs2812Thread function calls up an animation routine according to the number passed to it. Similar to the FL3731Thread a device number 0 to 7, is passed to an animation routine. However, unlike the FL3731Thread if there is nothing attached to that output there is no error cause, just nothing happens. There is a maximum number of 20 LEDs for each animation, this can be changed but for some reason all threads must have the same number of LEDs associated with them. There is no point adding extra threads here because the hardware can only cope with eight different device numbers.  
 
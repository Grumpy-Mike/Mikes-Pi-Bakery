// look up table for note mapping - change these how you like
// map harp in thirds ascending
byte noteLookUp0[] = { 0, 2, 4, 6 }; // for notes C E G B  major - minor - major
byte noteLookUp1[] = { 1, 3, 5, 7 }; // for notes D F A C  minor - major - minor
byte noteLookUp2[] = { 2, 4, 6, 8 }; // for notes E G B D  minor - major - minor 
byte noteLookUp3[] = { 3, 5, 7, 9 }; // for notes F A C E  major - minor - major
// map marimba in thirds ascending 
byte noteLookUp4[] = { 10, 12, 14, 16 }; // for notes C E G B  major - minor - major
byte noteLookUp5[] = { 11, 13, 15, 17 }; // for notes D F A C  minor - major - minor
byte noteLookUp6[] = { 12, 14, 16, 18 }; // for notes E G B D  minor - major - minor 
byte noteLookUp7[] = { 13, 15, 17, 19 }; // for notes F A C E  major - minor - major
byte noteLookUp8[] = { 20, 21, 22, 23 }; // for percussion
byte noteLookUp9[] = { 24, 25, 26, 27 }; // for percussion

byte noteLookUp[][] = { noteLookUp0, noteLookUp1, noteLookUp2, noteLookUp3, noteLookUp4, noteLookUp5,
                       noteLookUp6, noteLookUp7, noteLookUp8, noteLookUp9 };
byte sample[] = { 60,62,64,65,67,69,71,72,74,76 };

// look up table for coordinate conversion
// Polar to LED number

// Display ledNumber to display grid
 byte [] displayX= {
  5, 7, 9, 11, 13,  // leds 0 to 4 
  4, 6, 8, 10, 12, 14, // leds 5 to 10
  3, 5, 7, 9, 11, 13, 15, // leds 11 to 17
  2, 4, 6, 8, 10, 12, 14, 16, // leds 18 to 25
  1, 3, 5, 7, 9, 11, 13, 15, 17, // led 26 to 34
  2, 4, 6, 8, 10, 12, 14, 16, // leds 35 to 42
  3, 5, 7, 9, 11, 13, 15, // leds 43 to 49
  4, 6, 8, 10, 12, 14, // leds 50 to 55
  5, 7, 9, 11, 13,  // leds 56 to 60
  40, 40, 40, 40  // unused LEDs
    };

  byte [] displayY= {
  0, 0, 0, 0, 0,  // leds 0 to 4 
  1, 1, 1, 1, 1, 1, // leds 5 to 10
  2, 2, 2, 2, 2, 2, 2, // leds 11 to 17
  3, 3, 3, 3, 3, 3, 3, 3, // leds 18 to 25
  4, 4, 4, 4, 4, 4, 4, 4, 4, // led 26 to 34
  5, 5, 5, 5, 5, 5, 5, 5, // leds 35 to 42
  6, 6, 6, 6, 6, 6, 6, // leds 43 to 49
  7, 7, 7, 7, 7, 7, // leds 50 to 55
  8, 8, 8, 8, 8,  // leds 56 to 60
  40, 40, 40, 40 // unused LEDs
   };

// LED number for each angle, lesser angles wrap round
  byte []  ringR0 = { 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30 };
  byte []  ringR1 = { 31, 39, 38, 29, 21, 22, 31, 39, 38, 29, 21, 22, 31, 39, 38, 29, 21, 22, 31, 39, 38, 29, 21, 22 };
  byte []  ringR2 = { 32, 40, 47, 46, 45, 37, 28, 20, 13, 14, 15, 23, 32, 40, 47, 46, 45, 37, 28, 20, 13, 14, 15, 23 };
  byte []  ringR3 = { 33, 41, 48, 54, 53, 52, 51, 44, 36, 27, 19, 12,  6,  7,  8,  9, 16, 24, 33, 41, 48, 54, 53, 52 };
  byte []  ringR4 = { 34, 42, 49, 55, 60, 59, 58, 57, 56, 50, 43, 35, 26, 18, 11,  5,  0,  1,  2,  3,  4, 10, 17, 25 };
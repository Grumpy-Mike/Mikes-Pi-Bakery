
// look up table for note mapping - change these how you like
// map in thirds ascending
byte noteLookUp0[] = { 48, 52, 55, 59, 62, 67 }; // MIDI for notes C E G B D  major - minor - major
byte noteLookUp1[] = { 52, 55, 59, 62, 67, 71 }; // MIDI for notes D F A C  minor - major - minor
byte noteLookUp2[] = { 53, 57, 60, 64, 67, 71 }; // MIDI for notes E G B D  minor - major - minor 
byte noteLookUp3[] = { 55, 59, 62, 65, 69, 72 }; // MIDI for notes F A C E  major - minor - major
byte noteLookUp4[] = { 59, 62, 65, 69, 72, 76 }; 

byte noteLookUp5[] = { 49, 51, 54, 56, 58, 61 }; // MIDI for notes pentatonic scale
byte noteLookUp6[] = { 51, 54, 56, 58, 61, 63 }; // MIDI for notes pentatonic scale
byte noteLookUp7[] = { 54, 56, 58, 61, 63, 66 }; // MIDI for notes pentatonic scale  
byte noteLookUp8[] = { 56, 58, 61, 63, 66, 68 }; // MIDI for notes pentatonic scale
byte noteLookUp9[] = { 58, 61, 63, 66, 68, 70 }; // MIDI for notes pentatonic scale

byte noteLookUp10[] = { 48, 50, 52, 54, 56, 60 }; // MIDI for notes 
byte noteLookUp11[] = { 50, 52, 54, 56, 60, 62 }; // MIDI for notes 
byte noteLookUp12[] = { 52, 54, 56, 60, 62, 64 }; // MIDI for notes  
byte noteLookUp13[] = { 54, 56, 60, 62, 64, 66 }; // MIDI for notes 
byte noteLookUp14[] = { 56, 60, 62, 64, 66, 68 }; 
byte noteLookUp15[] = { 52, 54, 56, 60, 62, 64 }; // MIDI for notes  
byte noteLookUp16[] = { 54, 56, 60, 62, 64, 66 }; // MIDI for notes 

byte noteLookUp[][] = { noteLookUp0, noteLookUp1, noteLookUp2, noteLookUp3, noteLookUp4, noteLookUp5,
                       noteLookUp6, noteLookUp7, noteLookUp8, noteLookUp9, noteLookUp10, noteLookUp11,
                       noteLookUp12, noteLookUp13, noteLookUp14, noteLookUp15, noteLookUp16 };

// sequence length maps
int seqLength[] = { 6, 12, 18, 24, 30, 0}; // default start up length
int triSeq[]    = { 3, 6, 9, 12, 15, 18 }; // length of Tri sequence
int quadSeq[]   = { 4, 8, 12, 16, 20, 24};
int pentSeq[]   = { 5, 10, 15, 20, 25, 30 };
int hexSeq[]    = { 6, 12, 18, 24, 30, 0 };
int octSeq[]    = { 8, 16, 24, 32,  0, 0 };
int prime1Seq[]  = { 2, 3, 5, 7, 11, 13, 17 };
int prime2Seq[]  = { 3, 5, 7, 11, 13, 17, 23 };

int presetSeq[][] ={ triSeq, quadSeq, pentSeq, hexSeq, octSeq, prime1Seq, prime2Seq };

int buttonSize[] = { 35, 40, 45, 45, 45, 45, 50};

int ringC[] = {1, 2, 3, 4, 5, 6 }; // channel for ring
int instC[] = {0, 0, 0, 0, 0, 0}; // instrument for ring
int cVel[]  = {100, 100, 100, 100, 100, 100} ; // velocity for ring
/*
 * MIDIUSB_play - by Mike Cook September 2017
 * recieves MIDI through the USB port and routes it out to the
 * VS1053 0n the Bare conductive touch board
 * note the two "MIDI" links of the board must be made with a solder blob
 */ 

#include "MIDIUSB.h"
#include <SoftwareSerial.h>
// compiler error handling
#include "Compiler_Errors.h"

SoftwareSerial midiSerial(12, 10); // Soft TX on 10, we don't use RX in this code

// VS1053 setup
byte note = 0; // The MIDI note value to be played
byte resetMIDI = 8; // Tied to VS1053 Reset line pin 3
byte ledPin = 13; // MIDI traffic inidicator
int  instrument = 113; // initial instrument

void setup() {
  pinMode(ledPin,OUTPUT);
  // Setup soft serial for MIDI control
  midiSerial.begin(31250);
  Serial.begin(57600);
   // Reset the VS1053
  pinMode(resetMIDI, OUTPUT);
  digitalWrite(resetMIDI, LOW);
  delay(100);
  digitalWrite(resetMIDI, HIGH);
  delay(100);
  setupMidi(); // set up bank and instrument
}
// midiEventPacket_t format:-
// First parameter byte0 is the event type (0x0B = control change).
// Second parameter byte1 is the event type, combined with the channel.
// Third parameter byte2 is the control number number (0-119).
// Fourth parameter byte3 is the control value (0-127).

void loop() {
  midiEventPacket_t rx;
    rx = MidiUSB.read();
    if (rx.header != 0) {
      digitalWrite(ledPin, HIGH);
      sendToVS1053(rx.byte1, rx.byte2, rx.byte3);
      digitalWrite(ledPin, LOW);
    }
}

void sendToVS1053(byte cmd, byte data1, byte data2) {
  midiSerial.write(cmd);
  if( (cmd & 0xF0) == 0xF0) return; // single paramater call
  midiSerial.write(data1);
  if( (cmd & 0xF0) > 0xB0) return; // two pramater call
  midiSerial.write(data2);
}

void setupMidi(){  
   sendToVS1053(0xB0, 0x07, 127); // 0xB0 is channel message, set channel volume to max (127)
   sendToVS1053(0xB0, 0, 0x00); // Bank select - Default bank GM1  
   sendToVS1053(0xC0, instrument, 0); // "instrument" sets the intiial switch on voice  
}

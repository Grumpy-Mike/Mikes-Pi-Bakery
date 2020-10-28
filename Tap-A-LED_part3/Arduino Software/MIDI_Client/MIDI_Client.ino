/*
 * MIDI_Client
 *
 * Created: August 2020
 * Author: Mike Cook
 */ 

#include "MIDIUSB.h"

byte com[4];
byte pin [] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16};
midiEventPacket_t rx;

void noteOff(byte command, byte pitch, byte velocity) {
  midiEventPacket_t noteOff = {0x08, command, pitch, velocity};
  MidiUSB.sendMIDI(noteOff);
}

void noteOn(byte command, byte pitch, byte velocity) {
  midiEventPacket_t noteOn = {0x09, command, pitch, velocity};
  MidiUSB.sendMIDI(noteOn);
}

void afterTouchPoly(byte command, byte control, byte value) {
  midiEventPacket_t event = {0x0A, command, control, value};
  MidiUSB.sendMIDI(event);
}

void controlChange(byte command, byte control, byte value) {
  midiEventPacket_t event = {0x0B, command, control, value};
  MidiUSB.sendMIDI(event);
}

void programChange(byte command, byte control) {
  midiEventPacket_t event = {0x0C, command, control};
  MidiUSB.sendMIDI(event);
}

void afterTouch(byte command, byte control) {
  midiEventPacket_t event = {0x0D, command, control};
  MidiUSB.sendMIDI(event);
}

void pitchBend(byte command, byte control, byte value) {
  midiEventPacket_t event = {0x0E, command, control, value};
  MidiUSB.sendMIDI(event);
}

void requestPeripheral(byte what, byte val){ // read or write from Arduino GPIO
  int result1 = 0, result2 = 0xFF;
  byte type = what & 0xC0;
  byte pinNumber = what & 0x1F;
  if(type == 0) { // Digital read
      if((pinNumber <= 21) && (pinNumber > 1) && 
      (not(pinNumber == 11 || pinNumber == 12  || pinNumber == 13))) {
         pinMode(pinNumber, INPUT_PULLUP) ; // all inputs pull up
         result1 = digitalRead(pinNumber) ;
         sendToPi(0xF9, what, result1, 0x00);  
     }
     else sendToPi(0xF9, what, 0, 0xFF); // indicate an error
  }
  else if(type == 0x80) { // Digital write
    if((pinNumber <= 21) && (pinNumber > 1) && 
      (not(pinNumber == 11 || pinNumber == 12  || pinNumber == 13))) {
        //pinMode(pinNumber, INPUT) ; // remove any pull up
        pinMode(pinNumber, OUTPUT);
        digitalWrite(pinNumber, val & 0x01);
        sendToPi(0xF9, what, result1, 0x00);
      }
    else  sendToPi(0xF9, what, 0, 0xFF); // indicate an error 
  }
  else if(type == 0x40) { // Analogue read
    if(pinNumber < 0xB && not(pinNumber == 0x4 || pinNumber == 0x5)) {
      pinMode(pinNumber, INPUT); // remove any pull up
      result1 = analogRead(pinNumber);
      sendToPi(0xF9, what, result1 >> 3, result1 & 0x07);  
    }
    else sendToPi(0xF9, what, 0, 0xFF); // indicate an error
  }
  else if(type == 0xC0) { // analogue write (PWM)
       if( pinNumber == 3 || pinNumber == 5 || pinNumber == 6 || 
           pinNumber == 9 || pinNumber == 10) {
           analogWrite(pinNumber, val);
           sendToPi(0xF9, what, val, 0); // indicate OK 
           }
       else sendToPi(0xF9, what, 0, 0xFF); // indicate an error
  }
}

void sendToPi(byte header, byte what, byte result1, byte result2){
      Serial1.print(header); Serial1.print(" ");
      Serial1.print(what);  Serial1.print(" ");
      Serial1.print(result1);  Serial1.print(" ");
      Serial1.print(result2);  Serial1.println(" ");
}
  
void setup() {
  Serial.begin(250000);
  delay(3000);
  Serial1.begin(250000);
  while(Serial1.available() != 0) Serial1.read(); // empty the buffer
  for( int i = 0; i < 12; i++){ // default digital pins
    pinMode(pin[i], INPUT_PULLUP);
  }
}

void loop() {
  // read four byte commands from the Pi
    if(Serial1.available() >= 4) {
      for(byte i = 0 ; i < 4; i++){  
        com[i] = Serial1.read();
      } 
      switch (com[0]) {
        case 0x8 :
        noteOff(com[1], com[2], com[3]);
        break;
        case 0x9 :
        noteOff(com[1], com[2], com[3]);
        break;
        case 0xA :
        afterTouchPoly(com[1], com[2], com[3]);
        break;
        case 0xB :
        controlChange(com[1], com[2], com[3]);
        break;
        case 0xC :
        programChange(com[1], com[2]);
        break;
        case 0xD:
        afterTouch(com[1], com[2]);
        break;
        case 0xE :
        pitchBend(com[1], com[2], com[3]);
        break;
        case 0xF9 :
        requestPeripheral(com[1], com[2]);
        break;       
      }
       MidiUSB.flush();
   }
  
  do {
    rx = MidiUSB.read(); // Read command from MIDI host
    if (rx.header != 0) {
      sendToPi(rx.header, rx.byte1, rx.byte2, rx.byte3);
    }
  } while (rx.header != 0);
 }

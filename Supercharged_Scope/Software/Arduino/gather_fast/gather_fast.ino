// Arduino - Pi - Scope By Mike Cook June 2020
// using fast 8 bit A/D AD7822BNZ
// Trigger stratigy :- read in 1K buffer 
// then see if you have a trigger point in the first 512 bytes
// If you do then send the next 512 bytes

byte buffer [1028]; // 1028 byte input buffer
int pot1, triggerVoltage;
// int triggerTimeout = 1000; // time until auto trigger
// unsigned long triggerStart;
char triggerType = '2';
char readSpeed = '0'; // '0' as fast as possible
int firstSample = 0 ; // sample to start sending from buffer

void setup(){
  Serial.begin(250000);
  digitalWrite(4, HIGH);
  pinMode(4, OUTPUT);        //CONVIST pin
  pinMode(2, INPUT_PULLUP);  // EOC pin
  for(int i = 5; i<13; i++){
    pinMode(i, INPUT_PULLUP);
    //while(1) readA_Dd('1');
  }

  // set up fast sampling mode for internal A/D
  ADCSRA = (ADCSRA & 0xf8) | 0x04; // set 16 times division
}

void loop(){ 
  pot1 = analogRead(5); // switch channel to time cursor pot
  if( triggerType != '2') {
    trigger(); // get a trigger and send out to Pi 
  }
  else {
     if(readSpeed == '0') readA_D(516); else readA_Dd(516); // read fast or slow
     printBuffer(4); // send to the pi
  }
  // send back pot values for cursors
  pot1 = analogRead(5); 
  analogRead(6); // set up voltage cursor pot
  Serial.write(pot1>>8); // send Time cursor
  Serial.write(pot1 & 0xff);
   //Serial.println(pot1);
  pot1 = analogRead(6); // read voltage cursor
  triggerVoltage = analogRead(7); // set up trigger voltage cursor
  Serial.write(pot1>>8); // send voltage cursor
  Serial.write(pot1 & 0xff);
  //Serial.println(pot1);
  triggerVoltage = analogRead(7); // read trigger voltage cursor
  Serial.write(triggerVoltage>>8); // send trigger voltage cursor
  Serial.write(triggerVoltage & 0xff);
  //Serial.println(triggerVoltage);
  triggerVoltage = triggerVoltage >> 2; // 8 bit trigger voltage 
  // data sent now wait for next request  
  while(Serial.available() < 2) { } // wait for next request
  triggerType = Serial.read(); // see what trigger to use
  readSpeed = Serial.read(); // speed to read the buffer at
  while (Serial.available() != 0) { // remove any other bytes in buffer
     Serial.read();
  }
}

void trigger(){ // trigger at falling edge
     firstSample = 0;
     if(readSpeed == '0') readA_D(1028); else readA_Dd(1028); // read fast or slow   
     //triggerVoltage = analogRead(7)>>2; // update trigger voltage
  int i=4;
  while(firstSample == 0 && i < 516){ // search through buffer looking for a trigger event
    i++;
    if(buffer[i] < triggerVoltage && buffer[i-1] >= triggerVoltage) firstSample = i; 
  }
    if(firstSample != 0) {
      printBuffer(firstSample); // send to Pi
    }
    else {
    printBuffer(4);
    }
}

void readA_D(int len){ // read in buffer 943.4 KHz sample rate
  noInterrupts();
 for( int i = 0; i<len; i++){
  PORTD = 0xEF; // sets 4 LOW pulse the CONVIST pin 
  PORTD = 0x10; // sets 4,HIGH
  while((PIND & 4) == 0); 
  buffer[i] = PIND & 0xE0 | PINB & 0x1F;
 }
  interrupts();
}

void readA_Dd(int len){ // read in buffer xxx KHz sample rate
  byte readDel = 10;
  if(readSpeed == '2') readDel = 100;
  noInterrupts();
 for( int i = 0; i<len; i++){
  PORTD = 0xEF; // sets 4 LOW pulse the CONVIST pin 
  PORTD = 0x10; // sets 4,HIGH
  while((PIND & 4) == 0); 
  buffer[i] = PIND & 0xE0 | PINB & 0x1F;
  delayMicroseconds(readDel);
 }
  interrupts();
}

void printBuffer(int startR){
  for( int i = startR; i< startR + 512; i++){
    Serial.write(buffer[i]);
  }
}

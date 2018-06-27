// Arduino - Pi - Scope By Mike Cook
int buffer [512]; // 1K input buffer
int sample, lastSample;
int pot1, triggerVoltage;
int triggerTimeout = 1000; // time until auto trigger
unsigned long triggerStart;
char triggerType = '2';

void setup(){
  Serial.begin(115200);
  pinMode(13,OUTPUT);
  // set up fast sampling mode
  ADCSRA = (ADCSRA & 0xf8) | 0x04; // set 16 times division
}

void loop(){ 
  if( triggerType != '2') trigger(); // get a trigger 
  digitalWrite(13,HIGH);// timing marker
  for(int i=0; i<512 ; i++){
    buffer[i] = analogRead(0);
  }
  digitalWrite(13,LOW); // timing marker
  pot1 = analogRead(2); // switch channel to cursor pot
  for(int i=0; i<512 ; i++){
    Serial.write(buffer[i]>>8);
    Serial.write(buffer[i] & 0xff);
  }
  // send back pot values for cursors
  pot1 = analogRead(2);
  analogRead(3); // next cursor pot
  Serial.write(pot1>>8);
  Serial.write(pot1 & 0xff);
  pot1 = analogRead(3);
  triggerVoltage = analogRead(4);
  Serial.write(pot1>>8);
  Serial.write(pot1 & 0xff);
  triggerVoltage = analogRead(4);
  pot1 = analogRead(0); // prepair for next sample run 
  Serial.write(triggerVoltage>>8);
  Serial.write(triggerVoltage & 0xff);  
    
  while(Serial.available() == 0) { } // wait for next request
  triggerType = Serial.read(); // see what trigger to use
  while (Serial.available() != 0) { // remove any other bytes in buffer
     Serial.read();
  }
}

void trigger(){
  // trigger at rising zero crossing
  triggerStart = millis();
  sample = analogRead(0);
  do {
  lastSample = sample;
  sample = analogRead(0);
  }
  while(!(lastSample < triggerVoltage && sample > triggerVoltage) && (millis() - triggerStart < triggerTimeout));
}

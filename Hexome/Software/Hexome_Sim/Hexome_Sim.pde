/**
 * TouchOSC Hexome seq 1
 * 
 * The " TouchOSC hexome simulator "
 *
 * Each circle scans green at the same speed
 * Pushed buttons turn blue
 * When green scan meets a blue 
 *     - button turns orange and generates a note
 * repeats every 72 steps
 * By Mike Cook
 */

import oscP5.*;
import netP5.*;
import ddf.minim.*;
import ddf.minim.ugens.*;

Minim minim;
AudioOutput out;
Gain       gain;
Sampler [] notes = new Sampler[28];
int bank = 0;

OscP5 oscP5;
NetAddress myRemoteLocation;

String iPadIP = "192.168.1.68"; // change this to the address of your iPad / iPhone
int buttonNumber = -1;
int countR1=0, countR2=0, countR3=0, countR4=0;
boolean [] button = new boolean[64];
int ins=112;
int currentR, currentG, currentB;
int activeToggle = 0;
int frameCounter=0,frameLimit=9; // controls the speed of the step sequence
color cFill = color(204, 153, 0);
int ledColour = 0; // default red
String colours [] = {
     "red", "green", "blue", "yellow", "purple", "orange", "grey"
};
//     0       1       2       3          4          5        6

String page = "/1"; // TouchOSC page to send messages to

void setup() {
  size(580, 470);
  frameRate(30);
  setupSound();
  // array of button states
  for(int i=0; i<63; i++) button[i]=false;
  noStroke();
  colorMode(RGB, 255);
  ellipseMode(CORNER); 
  println("press f or s to change speed");
  println("press 1 to 0 change sound");

  /* start oscP5, listening for incoming messages at port 7000 */
  oscP5 = new OscP5(this,7000);
  // set the local IP address and port number to what is on the iPod
  myRemoteLocation = new NetAddress(iPadIP,7001); // local IP on the iPod  // select the correct page of the TouchOSC layout
  OscMessage myMessage = new OscMessage("/1"); // switch to layout page
  oscP5.send(myMessage, myRemoteLocation);
  setLEDcolour(6); // grey
  for(int i=0; i<61; i++) {  // put the lights on the keys
    setLED(i, true, 0.2);
    bufDelay(2); // make sure we don't do thing too fast
    } 
  setLEDcolour(0); // set clear button to red
  setLED(30, true, 0.8);
  toggleClear(); // clear the toggle
  toggleSet(0, 1.0); // set toggle 0
  messageFader(1,float(frameLimit));  // speed
  messageFader(2,-6.0); // volume
}

void draw() {
  frameCounter++;
  if((frameCounter > frameLimit)) { // only update every frameLimit frames
    frameCounter=0; 
    animate();
  }
}

void setupSound(){
   gain = new Gain(0.f);
  minim = new Minim(this);
  out   = minim.getLineOut();
  String soundDir = "harp/";
  for(int b=0; b<2; b++){
    for(int i=0;i<10;i++){ 
    notes[i+b*10] = new Sampler( soundDir + str(sample[i])+".wav", 4, minim );
    println("Loading",soundDir,str(sample[i])+".wav");
    notes[i+b*10].patch( out );
    }
    soundDir = "marimba/";
  }
  soundDir = "percussion/";
  for(int i=0;i<8;i++){ 
    notes[i+20] = new Sampler( soundDir + str(i)+".wav", 4, minim );
    println("Loading",soundDir,i);
    notes[i+20].patch( out );
  }
    out.setGain(-6.0);
}

void oscEvent(OscMessage theOscMessage) {   // respond to incoming messages
  String addr = theOscMessage.addrPattern();
  //println(addr);  // uncomment for debug print of all received messages
  if(addr.indexOf("/ping") != -1) return; // got a ping
  if(addr.length() < 3) return; // page change from the iPad
  float  val  = theOscMessage.get(0).floatValue();
  int startOfNumber; 
  //println(addr +" "+ val); // uncomment for debug print of relevant received messages and values
  // look at the push buttons
  startOfNumber = addr.indexOf(page+"/push");
  if(startOfNumber != -1) {
    buttonNumber = getNumber(addr, startOfNumber + 7);
    if(val != 0.0) {  // for button push
      doLEDclick(buttonNumber);
    } 
    else {  // for button release
      if(buttonNumber == 30) {
        OscMessage myMessage = new OscMessage(page+"/led30");
        myMessage.add(0.3);    // turn it down
        oscP5.send(myMessage, myRemoteLocation);
      }
    }
  }
  // look at the faders
  startOfNumber = addr.indexOf(page+"/fade");
  if(startOfNumber != -1) {
    int faderNumber = getNumber(addr, startOfNumber + 7);
    // println("in fader" + faderNumber + " with value of "+val);
    if(faderNumber == 1) frameLimit = int(val);
    if(faderNumber == 2) out.setGain(val);
  }

  // look at the toggle switches
  startOfNumber = addr.indexOf(page+"/toggle");
  if(startOfNumber != -1) {
    int toggleNumber = getNumber(addr, startOfNumber + 9);
    //println("in toggel" + toggleNumber + " with value of "+val); // remove comment for debug
    toggleSet(activeToggle, 0.0); // turn off previous toggle
    if ( ((int(toggleNumber) < 5 && activeToggle < 5)) || (int(toggleNumber) > 4 && activeToggle > 4)) {
    }    
    activeToggle = int(toggleNumber);
    bank = activeToggle;
    toggleSet(activeToggle, 1.0); // turn on new toggle
  }
}

void messageFader(int n,float val ){
  OscMessage myMessage = new OscMessage(page+"/fader"+n);
  myMessage.add(val);
  oscP5.send(myMessage, myRemoteLocation);
}

void clearSetButtons() {
  for(int i = 0; i<61; i++) {
    if(button[i]) {
      setLED(i, false, 1.0);  // turn off LED
      button[i] = false ;  // remove from the list
    }
  }
}

int getNumber(String s, int look) {
  int number = -1, i = 0;
  char p = '0';
  if(s.length() > look) {
    number = 0;
    for(int k = look; k< s.length(); k++) {
      p = s.charAt(look+i);
      i++;
      if(p >= '0' && p <= '9') number = (number * 10) + (int(p) & 0x0f);
    }
  }
  return(number);
}

void drawScreen() {
  // draw all screen LEDs
  for(byte n=0 ; n < 61 ; n++) {
    if(n != 30){
      if(button[n]) setLEDcolour(2); else setLEDcolour(6);
      fill(cFill);
    ellipse(displayX[n]*30, 10+ displayY[n]*50, 55, 55);
    }
  }
}

void animate() { // each ring progresses in turn preserving any set led by button push
  drawScreen();
  setLEDcolour(1); // green
  checkSetLED(ringR4[countR4],0,4);
  checkSetLED(ringR3[countR3],0,3);
  checkSetLED(ringR2[countR2],0,2);
  checkSetLED(ringR1[countR1],0,1);
  // increment counters and wrap round
  countR4++; 
   if(countR4>23) countR4=0;
  countR3++; 
   if(countR3>17) countR3=0;
  countR2++; 
   if(countR2>11) countR2=0;
  countR1++; 
   if(countR1>5) countR1=0;
  // turn on next LEDs in the sequence
  checkSetLED(ringR4[countR4],1,4);
  checkSetLED(ringR3[countR3],1,3);
  checkSetLED(ringR2[countR2],1,2);
  checkSetLED(ringR1[countR1],1,1);
}

void checkSetLED(byte num, int state, int ring) { // check to see if that LED is set if so change colour
  if(button[num]) { // if this is a special case LED a collision between sweep and set key has occurred
    int oldColour = ledColour;
    int g = currentG;
    int b = currentB;
    if(state == 0) setLEDcolour(2); // restore blue marker
    else {
      // collision has occurred generate a note
      notes[noteLookUp[bank][ring-1]].trigger();
      setLEDcolour(5); // orange
    }
    setLED(int(num),true, 1.0);
    setLEDcolour(oldColour); // restore colour
  } 
  else {
    setLED(num,boolean(state), 1.0);
  }
}

void setLEDcolour(int colour) {  // make sure the displayed colour matches the iPad (sort of)
  switch(colour) {
  case 0:
    ledColour = 0; // red
    cFill = color(196, 0, 0);
    break;
  case 1:
    ledColour = 1;  // green
    cFill = color(0, 196, 0);
    break;
  case 2:
    ledColour = 2;  // blue
    cFill = color(0, 128, 196);
    break;
  case 3:
    ledColour = 3;  // yellow
    cFill = color(196, 196, 0);
    break;
  case 4:
    ledColour = 4; // purple
    cFill = color(255, 0, 255);
    break;
  case 5:
    ledColour = 5;  // orange
    cFill = color(196, 128, 0);
    break;
  case 6:
    ledColour = 6;
    cFill = color(160, 160, 160);
    break;
  }
}

void setLED(int n, boolean s, float intensity) {
  color oldFill = cFill;
  // println("setting LED " +n);  // uncomment for debug
  if(s) {   // if we are setting the switch colour
    fill(cFill);
    OscMessage myMessage = new OscMessage(page+"/led"+n+"/color");
    myMessage.add(colours[ledColour]);
    oscP5.send(myMessage, myRemoteLocation);
    myMessage = new OscMessage(page+"/led"+n);
    myMessage.add(intensity);    // light it up
    oscP5.send(myMessage, myRemoteLocation);
  } 
  else {  // or we are turning it off
    fill(160); // change color to grey
    OscMessage myMessage = new OscMessage(page+"/led"+n+"/color");
    myMessage.add("gray");
    oscP5.send(myMessage, myRemoteLocation);
    myMessage = new OscMessage(page+"/led"+n);
    myMessage.add(0.2);    // turn it off
    oscP5.send(myMessage, myRemoteLocation); 
  }
  ellipse(displayX[n]*30, 10+ displayY[n]*50, 55, 55);
  cFill = oldFill;  // restore colour for screen
  bufDelay(4); // make sure we don't do thing too fast
}

 void bufDelay(long pause){
   pause = pause + millis();
   while(pause > millis()) { } // do nothing
 }
 
void toggleClear() {
  for(int i=0; i<10; i++) {
    toggleSet(i, 0.0);
  }
}

void toggleSet(int n, float val) {
  OscMessage myMessage = new OscMessage(page+"/toggle"+n);
  myMessage.add(val);    // set value
  oscP5.send(myMessage, myRemoteLocation);
}

void keyPressed() {
  if(key >= '0' && key <='9'){
  int press = 0xf & key;
  if(press == 0) press = 10;
  toggleClear();
  bank = press-1;
  toggleSet(bank, 1.0); // turn on new toggle  
  }  
  if(key == 's') { // slow down
    frameLimit++;
    messageFader(1,float(frameLimit));
    println("Speed " + frameLimit + " frames delay");
  }  
  if(key == 'f') { // speed up
    frameLimit--; 
    if(frameLimit <= 0) frameLimit = 0; // speed up limit
    println("Speed " + frameLimit + " frames delay");
  }   
  messageFader(1,float(frameLimit));
}

int findLED(int x,int y) { //find the led closest to click
  for(byte n=0 ; n < 61 ; n++) {
   if( (55+displayX[n]*30)-x < 55 && (55+displayX[n]*30)-x > 0 &&
    (10+displayY[n]*50)-y+50 < 50 && (10+displayY[n]*50)-y+50 > 0) {
      // println("LED click at",n);
      return (n);
  }
 }
 return(-99);
}

void doLEDclick(int buttonNumber){
      if(buttonNumber != 30) {    
        if(button[buttonNumber] == true) {
          button[buttonNumber] = false;
          setLED(buttonNumber, false, 1.0);
        } 
        else {
          button[buttonNumber] = true;
          setLEDcolour(2); // set to blue
          setLED(buttonNumber, true, 1.0);
        } 
      }
   else {
     clearSetButtons();
   }
}

void mousePressed() {
  int click = findLED(mouseX,mouseY);
  if(click != -99){
    doLEDclick(click);
  }
}
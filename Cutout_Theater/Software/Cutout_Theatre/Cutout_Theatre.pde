// Cutout Theatre - by Mike Cook March 2017
import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;
String iPadIP = "192.168.1.68"; // change this to the address of your mobile device
PImage openCurtian, closedCurtian; 
PImage rhhFront,rhhBack,woodMan,wolf,wSheep,wHead,gHead;
PImage door, room, plant, tree, wood;

String page = "/1";
int buttonNumber = -1 ;
boolean [] button = new boolean[13];
boolean displayUpdate = true;
int rrhPos = 899;
int cPos = 0;
int wPos = 899;

void setup() {
  size(899, 590);
  frameRate(30);
  /* start oscP5, listening for incoming messages at port 7000 */
  oscP5 = new OscP5(this,7000);
  // set the port number to what is on the mobile device
  myRemoteLocation = new NetAddress(iPadIP,7001); // send messages to this port
  // Load the image into the program
  openCurtian = loadImage("curtain_open.png"); 
  closedCurtian = loadImage("curtain.png");
  rhhFront = loadImage("rrh_front.png");
  rhhBack = loadImage("rrh_back.png");
  woodMan = loadImage("woodMan.png");  
  wolf = loadImage("wolf.png");
  wSheep = loadImage("wolf_sheep.png");
  wHead = loadImage("wolf_head.png");
  gHead = loadImage("grandma_head.png");
  door = loadImage("door.png");
  room = loadImage("room.png");
  plant = loadImage("plant.png");
  tree = loadImage("tree.png");
  wood = loadImage("wood.png");
  setFaders();
}

void draw() {
  if(displayUpdate){
    rect(0.0,0.0,width,height); // clear screen
    if(button[12])image(wood,0,110); // wood backdrop
    if(button[10])image(door,0,160);
    if(button[11])image(room,0,110); // room
    if(button[9])image(plant,450,300); // house plant
    if(button[1])image(wolf,wPos,320);
    if(button[2])image(wSheep,wPos,320);
    if(button[3])image(wHead,308,323+(wPos/300.0));
    if(button[6])image(gHead,306,360+(rrhPos/300.0));
    if(button[8])image(tree,530,140); // tree
    if(button[4])image(rhhFront,rrhPos,320);
    if(button[5])image(rhhBack,rrhPos,380);
    if(button[7])image(woodMan,rrhPos,260);
    image(closedCurtian, 0, cPos);
    image(openCurtian, 0, 0);
    displayUpdate = false;
  }
}

void oscEvent(OscMessage theOscMessage) {   // respond to incoming messages
  String addr = theOscMessage.addrPattern();
  //println(addr);  // uncomment for debug print of all received messages
  if(addr.indexOf("/ping") != -1) return; // got a ping
  if(addr.length() < 3) return; // page change from the iPad
  float  val  = theOscMessage.get(0).floatValue();
  int startOfNumber; 
   // println(addr +" "+ val); // uncomment for debug print of relevant received messages and values
  // look at the push buttons  
  startOfNumber = addr.indexOf(page+"/push");
  if(startOfNumber != -1) {
    buttonNumber = getNumber(addr, startOfNumber + 7);
    //println("in push" + buttonNumber + " with value of "+val);
    if(val == 0.0) {  // for button release 
          setPush(buttonNumber, !button[buttonNumber]); // toggle
          // do radio buttons
    if(buttonNumber == 1 || buttonNumber == 2 || buttonNumber == 3){
       setPush(1,false);
       setPush(2,false);
       setPush(3,false);
       setPush(buttonNumber,!button[buttonNumber]);
        } 
         if(buttonNumber == 4 || buttonNumber == 5 || buttonNumber == 6|| buttonNumber == 7){
            setPush(4,false);
            setPush(5,false);
            setPush(6,false);
            setPush(7,false);
            setPush(buttonNumber,!button[buttonNumber]);
        } 
      }
      displayUpdate = true;
     }
  // look at the faders
  startOfNumber = addr.indexOf(page+"/fader");
  if(startOfNumber != -1) {
    int faderNumber = getNumber(addr, startOfNumber + 7);
    //println("in fader" + faderNumber + " with value of "+val);    
    if(faderNumber == 1) cPos = int(val);
    if(faderNumber == 2) wPos = int(val);    
    if(faderNumber == 3) rrhPos = int(val);    
    displayUpdate = true;
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

void setFaders(){
  messageFader(1,0.0);
  messageFader(2,899.0);
  messageFader(3,899.0);
  for(int i=1;i<13;i++) setPush(i,false);
  setPush(1,true);
  setPush(4,true);
}

void messageFader(int n,float val ){
  OscMessage myMessage = new OscMessage(page+"/fader"+n);
  myMessage.add(val);
  oscP5.send(myMessage, myRemoteLocation);
}

void setPush(int n, boolean s) {
  // println("setting push button " +n);  // uncomment for debug
    OscMessage myMessage = new OscMessage(page+"/push"+n);
    if(s) myMessage.add(1.0); else myMessage.add(0.0);
    button[n] = s; 
    oscP5.send(myMessage, myRemoteLocation);
    bufDelay(4); // make sure we don't do thing too fast
}

 void bufDelay(long pause){
   pause = pause + millis();
   while(pause > millis()) { } // do nothing
 }

void toggleSet(int n, float val) {
  OscMessage myMessage = new OscMessage(page+"/toggle"+n);
  myMessage.add(val);    // set value
  oscP5.send(myMessage, myRemoteLocation);
}
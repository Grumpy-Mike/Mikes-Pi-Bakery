/*   Poly1 - a poly rythmic sequencer
*    File to handel the user interface
*
*/
Numberbox n0,n1,n2,n3,n4,n5,n6,n7,n8,n9;
Numberbox c0,c1,c2,c3,c4,c5; // channel
Numberbox v0,v1,v2,v3,v4,v5; // velocity
Numberbox in0,in1,in2,in3,in4,in5; // instrument
void addControls() {
int yoff = 22, yinc = 40;
  lengthControl = new ControlP5(this);
  lengthControl.setColorCaptionLabel(0);
// NAME, START value, X, Y, length of number box, hight of box
  n0 = lengthControl.addNumberbox("length_1",6,10, yoff,30,15);
  n0.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  n1 = lengthControl.addNumberbox("length_2",12,10, yoff + yinc*1,30,15);
  n1.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  n2 = lengthControl.addNumberbox("length_3",18,10, yoff + yinc*2,30,15);
  n2.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  n3 = lengthControl.addNumberbox("length_4",24,10, yoff + yinc*3,30,15);
  n3.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  n4 = lengthControl.addNumberbox("length_5",30,10, yoff + yinc*4,30,15);
  n4.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  n5 = lengthControl.addNumberbox("length_6",0,10, yoff + yinc*5,30,15);
  n5.setMax(32).setMin(0).setDirection(Controller.HORIZONTAL);
  //n7 = lengthControl.addNumberbox("instrument",112,800, 620,30,15);
  //n7.setMax(127).setMin(0);
  n8 = lengthControl.addNumberbox("sequence_length",32,200, yoff,50,15);
  n9 = lengthControl.addNumberbox("step_delay",8,800, yoff,30,15);
  n9.setMax(32).setMin(1).setDirection(Controller.HORIZONTAL);
  
  // Check boxes for mute
 // controlP5 = new ControlP5(this);
  checkbox = lengthControl.addCheckBox("checkBox",74,22);  
  // make adjustments to the layout of a checkbox.
  checkbox.setColorForeground(color(120));
  checkbox.setColorActive(color(255, 0, 0));
  checkbox.setColorLabel(color(0)).setSize(20,20);
  checkbox.setItemsPerRow(1);
  checkbox.setSpacingColumn(70);
  checkbox.setSpacingRow(20);
  // add items to a checkbox.
  checkbox.addItem("m1",0);
  checkbox.addItem("m2",0);
  checkbox.addItem("m3",0);
  checkbox.addItem("m4",0);
  checkbox.addItem("m5",0);
  checkbox.addItem("m6",0);
  
  muteLabel = lengthControl.addTextlabel("label1","Mute",70,8);
  muteLabel.setColorValue(0x0);
  map1Label = lengthControl.addTextlabel("label2","Note Mapping",906,8);
  map1Label.setColorValue(0x0);
  map2Label = lengthControl.addTextlabel("label3","Ring",14,8);
  map2Label.setColorValue(0x0);
  cont1Label = lengthControl.addTextlabel("label4","Controls",56,265);
  cont1Label.setColorValue(0x0);
  cont2Label = lengthControl.addTextlabel("label5","Stop",26,296);
  cont2Label.setColorValue(0x0);
  cont3Label = lengthControl.addTextlabel("label6","Reset",24,342);
  cont3Label.setColorValue(0x0);
  cont4Label = lengthControl.addTextlabel("label7","Clear",26,385);
  cont4Label.setColorValue(0x0);
 
  config = lengthControl.addTextlabel("label8","Configurations",56,400);
  config.setColorValue(0x0);
  config0 = lengthControl.addTextlabel("label9","Tri",28,432);
  config0.setColorValue(0x0);
  config1 = lengthControl.addTextlabel("label10","Quad",24,477);
  config1.setColorValue(0x0);
  config2 = lengthControl.addTextlabel("label11","Pent",26,522);
  config2.setColorValue(0x0);
  config3 = lengthControl.addTextlabel("label12","Hex",26,567);
  config3.setColorValue(0x0);
  config4 = lengthControl.addTextlabel("label13","Oct",26,612);
  config4.setColorValue(0x0);
  config5 = lengthControl.addTextlabel("label14","Prime1",22,657);
  config5.setColorValue(0x0);
  config6 = lengthControl.addTextlabel("label15","Prime2",22,702);
  config6.setColorValue(0x0);
  config7 = lengthControl.addTextlabel("label16","Instrument",80,454);
  config7.setColorValue(0x0);
  config8 = lengthControl.addTextlabel("label17","Channels",825,454);
  config8.setColorValue(0x0);

  
  // Ring channeles
  channelSelect = new ControlP5(this);
  channelSelect.setColorCaptionLabel(0);
  c0 = lengthControl.addNumberbox("ring_1",1,832, 472,30,15);
  c0.setRange(1,16).setDirection(Controller.HORIZONTAL);
  c1 = lengthControl.addNumberbox("ring_2",2,832, 472+yinc*1,30,15);
  c1.setRange(1,16).setDirection(Controller.HORIZONTAL);
  c2 = lengthControl.addNumberbox("ring_3",3,832, 472+yinc*2,30,15);
  c2.setRange(1,16).setDirection(Controller.HORIZONTAL);
  c3 = lengthControl.addNumberbox("ring_4",4,832, 472+yinc*3,30,15);
  c3.setRange(1,16).setDirection(Controller.HORIZONTAL);
  c4 = lengthControl.addNumberbox("ring_5",5,832, 472+yinc*4,30,15);
  c4.setRange(1,16).setDirection(Controller.HORIZONTAL);
  c5 = lengthControl.addNumberbox("ring_6",6,832, 472+yinc*5,30,15);
  c5.setRange(1,16).setDirection(Controller.HORIZONTAL);
// velocity select
  velocitySelect = new ControlP5(this);
  velocitySelect.setColorCaptionLabel(0);
  v0 = lengthControl.addNumberbox("vel_1",100,872, 472,30,15);
  v0.setRange(0,127).setDirection(Controller.HORIZONTAL);
  v1 = lengthControl.addNumberbox("vel_2",100,872, 472+yinc*1,30,15);
  v1.setRange(0,127).setDirection(Controller.HORIZONTAL);
  v1 = lengthControl.addNumberbox("vel_3",100,872, 472+yinc*2,30,15);
  v1.setRange(0,127).setDirection(Controller.HORIZONTAL);
  v1 = lengthControl.addNumberbox("vel_4",100,872, 472+yinc*3,30,15);
  v1.setRange(0,127).setDirection(Controller.HORIZONTAL);
  v1 = lengthControl.addNumberbox("vel_5",100,872, 472+yinc*4,30,15);
  v1.setRange(0,127).setDirection(Controller.HORIZONTAL);
  v1 = lengthControl.addNumberbox("vel_6",100,872, 472+yinc*5,30,15);
  v1.setRange(0,127).setDirection(Controller.HORIZONTAL);
// instrument select
  voiceSelect = new ControlP5(this);
  voiceSelect.setColorCaptionLabel(0);
  in0 = lengthControl.addNumberbox("inst_1",0,88, 472,30,15);
  in0.setRange(0,127).setDirection(Controller.HORIZONTAL);
  in1 = lengthControl.addNumberbox("inst_2",0,88, 472+yinc*1,30,15);
  in1.setRange(0,127).setDirection(Controller.HORIZONTAL);
  in2 = lengthControl.addNumberbox("inst_3",0,88, 472+yinc*2,30,15);
  in2.setRange(0,127).setDirection(Controller.HORIZONTAL);
  in3 = lengthControl.addNumberbox("inst_4",0,88, 472+yinc*3,30,15);
  in3.setRange(0,127).setDirection(Controller.HORIZONTAL);
  in4 = lengthControl.addNumberbox("inst_5",0,88, 472+yinc*4,30,15);
  in4.setRange(0,127).setDirection(Controller.HORIZONTAL);
  in5 = lengthControl.addNumberbox("inst_6",0,88, 472+yinc*5,30,15);
  in5.setRange(0,127).setDirection(Controller.HORIZONTAL);
 }
 

 void length_1(int theLength) {
  seqLength[0] = theLength;
  if(seqLength[0] < 11) buttonSize[0] = 10 + (32 - seqLength[0]); else buttonSize[0] = 10 + ((32 - seqLength[0])/2);
  seeSeqLength();
  resetSeq();
}

 void length_2(int theLength) {
  seqLength[1] = theLength;  
  buttonSize[1] = 20 + (32 - seqLength[1]) ;
  seeSeqLength();
  resetSeq();
}

 void length_3(int theLength) {
  seqLength[2] = theLength;
  buttonSize[2] = 30 + (32 - seqLength[2]) ;
  seeSeqLength();
  resetSeq();
}
 void length_4(int theLength) {
  seqLength[3] = theLength;
  seeSeqLength();
  resetSeq();
}
 void length_5(int theLength) {
  seqLength[4] = theLength;
  seeSeqLength();
  resetSeq();
}
 void length_6(int theLength) {
  seqLength[5] = theLength;
  seeSeqLength();
  resetSeq();
}

  void step_delay(int speed){
    frameLimit = speed;
  }
  
void sequence_length(int seq){
  // do nothing
}
void resetSeq(){
  for(int n=0 ; n < numberOfLines ; n++) {
       sequence[n]=0;
  }
  if(seeLength){
  seeSeqLength();
  seeLength = false;
  }
}
// ring channel adjustment
 void ring_1(int chan) {
  ringC[0] = chan;
}
 void ring_2(int chan) {
  ringC[1] = chan;
}
 void ring_3(int chan) {
  ringC[2] = chan;
}
 void ring_4(int chan) {
  ringC[3] = chan;
}
 void ring_5(int chan) {
  ringC[4] = chan;
}
 void ring_6(int chan) {
  ringC[5] = chan;
}
// Ring velocity ajustment
 void vel_1(int velocity) {
  cVel[0] = velocity;
}
 void vel_2(int velocity) {
  cVel[1] = velocity;
}
 void vel_3(int velocity) {
  cVel[2] = velocity;
}
 void vel_4(int velocity) {
  cVel[3] = velocity;
}
 void vel_5(int velocity) {
  cVel[4] = velocity;
}
 void vel_6(int velocity) {
  cVel[5] = velocity;
}

void inst_1(int ins){
    myBus.sendMessage(0xC0,ringC[0],ins,0);
    instC[0] = ins;
  }
void inst_2(int ins){
    myBus.sendMessage(0xC0,ringC[1],ins,0);
    instC[1] = ins;
  }
void inst_3(int ins){
    myBus.sendMessage(0xC0,ringC[2],ins,0);
    instC[2] = ins;
  }
void inst_4(int ins){
    myBus.sendMessage(0xC0,ringC[3],ins,0);
    instC[3] = ins;
  }
void inst_5(int ins){
    myBus.sendMessage(0xC0,ringC[4],ins,0);
    instC[4] = ins;
  }
void inst_6(int ins){
    myBus.sendMessage(0xC0,ringC[5],ins,0);
    instC[5] = ins;
  }

void controlEvent(ControlEvent theEvent) {
  if(theEvent.isGroup()) {
    //print("got an event from "+theEvent.getGroup().getName()+"\t");
    for(int i=0;i<checkbox.getArrayValue().length;i++) {
      mute[i] = (int)checkbox.getArrayValue()[i];
    }
  }
}
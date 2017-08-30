  /**
   * Poly - a poly rhythmic sequencer
   * For the Raspberry Pi version of processing 3.3.5
   * 
   * Each line scans at the same speed
   * Click buttons turn blue
   * When green meets blue - button turns orange and generates a MIDI note on
   *
   * Buttons on the right control the ring to note mapping
   * Buttons on the left control the number of steps in a ring, with presets for connected space.
   * 
   * By Mike Cook April - June 2012 & August 2017
   * Creative Commons Licence
   */
   
  import themidibus.*; //Import the library
  import controlP5.*;
  
  MidiBus myBus; // The MidiBus
  ControlP5 lengthControl, channelSelect, velocitySelect, voiceSelect;
  CheckBox checkbox;
  Textlabel muteLabel, map1Label,  map2Label, cont1Label, cont2Label, cont3Label, cont4Label;
  Textlabel config, config0, config1, config2, config3, config4, config5, config6, config7,config8;
  
  byte x, y;
  int frameCounter=0,frameLimit=8; // sets start up speed
  boolean stop = true, seeLength = true;
  int xOffset = 50, yOffset = 20, numberOfLines = 6;
  boolean [][] button = new boolean[numberOfLines][32];
  boolean [] notePlaying = new boolean[numberOfLines];
  int [] sequence = new int[numberOfLines];
  int mapping = 0; // note mapping
  int [] mute= new int[numberOfLines]; // mute mask bit set = track mute
  color cFill = color(204, 153, 0);
  color [] ringsColour = new color [7];
  boolean needMappingRedraw= true, changeMapping = false;

/* ************** setup ********************* */  
  void setup() {
    size(980, 720);
    frameRate(30);
    MidiBus.list(); // List all available Midi devices
//                   Parent In Out
//                     |    |  |
  myBus = new MidiBus(this, 0, 1); // Create a new MidiBus using the device index to select the Midi input and output devices respectively.

    clearButtons();
    addControls();
    colorMode(HSB, 360, 100, 100);
    // define ring colours
    for(int i = 0; i<7; i++){
      ringsColour[i] = color(25+50*i, 40, 70);
    }
    colorMode(RGB, 255);
    // Draw grid of LEDs
    noStroke();
    colorMode(RGB, 255);
    ellipseMode(CENTER);
    fill(180); 
    clearScreenLEDs(); 
    println("press +/- to change speed");  
      drawMappingPads();
  }
  

  /* ************** Draw ***************** */
  boolean test = true;
  void draw() {
    frameCounter++;
    if((frameCounter > frameLimit) && test){
    frameCounter=0; 
    drawMappingPads();  // the place to click and find the notes
    anamate();
    } 
  } // end of draw
  
     void anamate(){ // each ring progresses in turn preserving any set led by button push
     // draw the ring tracks
      noStroke();
              fill(204, 204, 204);
        //rect(xOffset+26, yOffset, width-112-xOffset, height);
        rect(xOffset+26, 0, width-112-xOffset, height);
     for(int n=numberOfLines-1; n > -1; n--){
       if(seqLength[n] !=0) {  // only draw rings with LEDs on them
        fill(ringsColour[n]);
       ellipse((width+xOffset-60)/2, height/2, 10+((1+n)*108)+ buttonSize[n], 10+((1+n)*108) + buttonSize[n]);
       }
       fill(204,204,204);
       ellipse((width+xOffset-60)/2, height/2, 10+((1+n)*108) - buttonSize[n], 10+((1+n)*108) - buttonSize[n]); 
     }
       noFill();
      // next turn off LEDs
     showSelectedLEDs();
     setLEDcolour(0,255,0);
  
    for(int n=0 ; n < numberOfLines ; n++) {
       if(!stop)sequence[n]++; // increment if not stoped
       if(sequence[n] >= seqLength[n] ) sequence[n] = 0;      
       checkSetLED(n, sequence[n]);      
     }      
  }
  
  void checkSetLED(int row, int num){ // check to see if that LED is set if so change colour
  // println("checking row " + row + " number " + num);
  if(seqLength[row] == 0) return;
    if(button[row][num]) { // if this is a selected LED
       // collision has occoured generate a  note
      if(mute[row] == 0 && !stop) {  playNote(row); notePlaying[row] = true; }
       setLEDcolour(255,128, 0);  // orange
       setLED(row, num, true); // make it orange
       setLEDcolour(0,255,0); // restore green for the rest of the scan
     }
    else {
       if(notePlaying[row]) { noteOff(row); notePlaying[row] = false; }
       setLED(row, num, true);
    }
  }
  
  void clearScreenLEDs(){ // draw all screen LEDs as off
      fill(0);
      for(byte n=0 ; n < numberOfLines ; n++) {
        for( int l=0; l<seqLength[n]; l++){ // draw each LED for the number of times in the sequence
       }
      }
   }
   
  void showSelectedLEDs(){ // display selected LED as blue or un selected as black  
        
      for(int row=0 ; row < numberOfLines ; row++) {
        if(seqLength[row] != 0){
          setLEDcolour(0,0,255); // selected colour  
          for( int l=0; l<seqLength[row]; l++){ // draw each LED for the number of times in the sequence
          if(button[row][l]){
           setLEDcolour(0,0,255); // selected colour
            setLED(row,l, true); 
          } else {
             
            setLEDcolour(int(red(ringsColour[row]))-10, int(green(ringsColour[row]))-10, int(blue(ringsColour[row]))-10);
            setLED(row,l, true);
          }
        }
      }
     }
   }

   void setLEDcolour(int r, int g, int b){
     cFill = color(r, g, b);
   }
   
  void setLED(int seq, int n, boolean s) { // sets the LED of sequence number, led number, set or clear
   if(s) { fill(cFill); } else {fill (0,0,0);}  // change colour 
  //    println(cFill);   
  
    // ellipse(xOffset + x + seq*40, yOffset + y, 30, 30);
    pushMatrix(); 
    translate((width+xOffset-60)/2, height/2);
      rotate((n*(PI/(seqLength[seq]/2.0))));
      ellipse(60 + seq*54, 0, buttonSize[seq], buttonSize[seq]);
    popMatrix();   
  }
  
  void playNote(int i){ 
    //println("play Note",noteLookUp[mapping][i]);      
     myBus.sendNoteOn(ringC[i],noteLookUp[mapping][i],cVel[i]);
  }
  
    void noteOff(int i){
     //println("stop Note",noteLookUp[mapping][i]);  
     myBus.sendNoteOff(ringC[i],noteLookUp[mapping][i],cVel[i]);
  }
  
  void allOff(){ // turn off all notes on a control stop
      for(int i =0 ; i<numberOfLines; i++){
        noteOff(i);
       }
  }
    
 void drawMappingPads(){ // draw the bits that are mapped
  if(needMappingRedraw) {
    allOff(); // remove any hanging notes
    stroke(0);
    needMappingRedraw = false; // so we only do it when needed
    for(int i =0; i<17; i++){ 
      if(i<=4) fill(153, 130, 153);
      if(i>4 && i<10) fill(130, 153, 153);
      if(i>9) fill(153, 153, 130);
      if(i == mapping) { // draw the selected square
      if(i<=4) fill(200, 0, 200);
      if(i>4 && i<10) fill(0, 200, 200); 
      if(i>9) fill(200, 200, 0);
      }
      //rect(920 , 20 + i*50, 30,30);
      rect(920 , 20 + i*41, 30,30);
    } 
      // draw control buttons
      fill(153, 153, 0);
      for(int i =0; i<10; i++){
       if(i == 3)  fill(0, 140, 140);
       //rect(20, 346 + i*50, 30,30);
       rect(24, 266 + i*45, 25,25);
      }
    noStroke();
   }
  }
  
  void clearButtons(){  // reset all the buttons to unpressed
  for(int i=0; i<numberOfLines; i++){
    for(int l=0; l<seqLength[i]; l++){  
      button[i][l]=false;
     }
    }
  }
  
  void setSeq(int n){
    for(int i = 0; i<numberOfLines; i++){
      seqLength[i] = presetSeq[n][i];
    }
    n0.setValue(seqLength[0]);
    n1.setValue(seqLength[1]);
    n2.setValue(seqLength[2]);
    n3.setValue(seqLength[3]);
    n4.setValue(seqLength[4]);
    n5.setValue(seqLength[5]);
  }
  
  void seeSeqLength(){
    long count = 1;
    boolean test= false;
    while(test == false){
      count++;
      test = true;
    for(int i = 0; i<numberOfLines; i++){
      if(seqLength[i] !=0){
        if( (count % seqLength[i]) != 0 )  test = false;
    //  println("Length "+ seqLength[i] + " " + count % seqLength[i]);
      }
     }
    }
    // println("Sequence length is " + count);
    n8.setValueLabel(str(int(count)));
  }
  
 void mouseReleased() {
   needMappingRedraw = true; // draw it
   seeLength=true;
 }
 
 void mousePressed() {
  int x, y, hit, hitY=0, hitX, hitCont=-1, hitR;
  x = mouseX; 
  y = mouseY;
  //println(x,y);
  hit = mapping;
   // println(x+" "+y);
   
   // ******* Look to see if we have hit an LED ********
   int xc = (width+xOffset-60)/2; // the center of the display
   int yc = height/2;
   int px = x - xc; // shift mouse relitave to the center
   int py = yc - y;
  // println("shifted " + px + " " + py);
   int r = int( sqrt((px*px) + (py*py) ));
     hitX=-1;
   for(int n=0; n<numberOfLines; n++){
     hitR = 60 + n*54;
     // println("hitR " + hitR + " at n= " + n + " Lower " + (hitR-buttonSize[n]/2) + " Upper " + (hitR+buttonSize[n]/2));
     if(r > hitR-(buttonSize[n]/2) && r < hitR+(buttonSize[n]/2) ) hitX=n;
    }
    if(hitX > -1 ){ 
      float th = atan2(py, px);
      th = 0.5+(seqLength[hitX]*(( - th)/TWO_PI));
      if(th < 0.0) th = th + seqLength[hitX];
     // println("polar " + r + " " + th);
   button[hitX][int(th)] = !button[hitX][int(th)];
   }

   // ***** look at note mapping buttons  ********

   if(x >= 920 && x <= 957){ // in the zone for x
   // println("in x zone");
       for(int i =0; i<17; i++){ // see if we hit a square
       if((y >= (22 + i*41)) && (y <= ((30 + i*50) + 22) ) ) hit = i; // println("Y hit at "+ i); }
       }
       if(hit != mapping) { // we have clicked a square
         // allOff(); // remove any hanging notes
         mapping = hit;
         needMappingRedraw = true; // draw it
       }
   }
 // look at control buttons  
   if(x >= 26 && x <= 54 && y > 266){ // in the zone for x
     for(int i =0; i<10; i++){ // see if we hit a square
       if((y >= (268 + i*45)) && (y <= ((268 + i*45) + 25) ) ) hitCont = i;
       }
       if(hitCont != -1) { // we have clicked a square
       stroke(0);
       if(hitCont > 2) fill(180, 240, 0); else fill(240, 180, 0); // hit colour
       rect(24, 266 + hitCont*45, 25, 25);
       noStroke();
       // println("Control " + hitCont);
       switch (hitCont) {
         case 0:  // stop go
         if(!stop) allOff(); // shut down sound
         fill(200, 200, 200);
         rect(26,295, 24,12); // rub out the old label
         stop = !stop;
         if(stop) cont2Label.setValueLabel("Go "); 
           else   cont2Label.setValueLabel("Stop");
         break;
         case 1: // reset sequence & stop all notes
           resetSeq();
           for(int c=1;c<17;c++){
             for(int n=0; n<128;n++){
               myBus.sendNoteOff(c,n,0);
             }
           } 
         break;
         case 2: // clear buttons
         clearButtons();
         break;
         case 3:
         case 4:
         case 5:
         case 6:
         case 7:
         case 8:
         case 9:
         setSeq(hitCont - 3);
         break;
       }
       }
   }
}
   
   void keyPressed() {
    if(key == '=') { frameLimit--;  println("Speed " + frameLimit + " frames delay"); } // speed up
    if(key == '-') { frameLimit++;  println("Speed " + frameLimit + " frames delay"); } // slow down
    if(frameLimit < 0) frameLimit = 0; // slow down limit
   }
     
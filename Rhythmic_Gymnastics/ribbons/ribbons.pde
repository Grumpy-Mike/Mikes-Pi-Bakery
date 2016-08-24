// Ribbons by Mike Cook August 2016
// with credit to http://www.zenbullets.com
import processing.io.*;
MCP3004 adc;

int ribbonAmount = 2; // number of ribbon strands
int ribbonParticleAmount = 20;
float randomness = .2;
RibbonManager ribbonManager1;
RibbonManager ribbonManager2;
float xPad1 = 0.120, yPad1 = 0.120; 
float xPad2 = 0.120, yPad2 = 0.120;
boolean rightClick = false;
boolean leftClick = false;

void setup()
{  	
  fullScreen();
  //size(600, 450);
  frameRate(30);
  background(0);
  GPIO.pinMode(2, GPIO.INPUT);
  GPIO.pinMode(3, GPIO.INPUT);  
  ribbonManager1 = new RibbonManager(ribbonAmount, ribbonParticleAmount, randomness, "swatch_01.jpg");     
  ribbonManager2 = new RibbonManager(ribbonAmount, ribbonParticleAmount, randomness, "swatch_02.jpg");  
  adc = new MCP3004(SPI.list()[0]);
} 


void draw()
{
  fill(0, 255);
  rect(0, 0, width, height);
  doClick();
   xPad1 = 0.5 - (adc.getAnalog(0)/2.0);
   yPad1 = adc.getAnalog(1);
   xPad2 = 0.5 + (adc.getAnalog(2)/2.0);
   yPad2 = adc.getAnalog(3);
   stroke(255,255,255);
   ellipse(xPad1*width, yPad1*height, 15, 15);
   ellipse(xPad2*width, yPad2*height, 15, 15);
  ribbonManager1.update(int(xPad2*width), int(yPad2*height));
  ribbonManager2.update(int(xPad1*width), int(yPad1*height));
}

void doClick(){
  if (GPIO.digitalRead(2) == GPIO.LOW && !rightClick) {
    print("right press ");
    rightClick = true;
     ribbonManager2.setNewColour();
  }
  if (GPIO.digitalRead(2) == GPIO.HIGH && rightClick) {
    println("release ");
    rightClick = false;
  }
  if (GPIO.digitalRead(3) == GPIO.LOW && !leftClick) {
    print("left press ");
    leftClick = true;
    ribbonManager1.setNewColour();
  }
  if (GPIO.digitalRead(3) == GPIO.HIGH && leftClick) {
    println("release ");
    leftClick = false;
  }
}
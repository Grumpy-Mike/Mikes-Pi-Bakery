import processing.io.SPI;

// MCP3004 is a Analog-to-Digital converter using SPI
// this has 4 input channels
// datasheet: http://ww1.microchip.com/downloads/en/DeviceDoc/21295d.pdf
// code corrections by Mike Cook

class MCP3004 extends SPI {

  MCP3004(String dev) {
    super(dev);
    super.settings(500000, SPI.MSBFIRST, SPI.MODE0);
  }

  float getAnalog(int channel) {
    if (channel < 0 ||  channel > 3) {
      System.err.println("The channel needs to be from 0 to 3");
      throw new IllegalArgumentException("Unexpected channel");
    }
    byte[] out = { 0, 0, 0 };
    // encode the channel number in the first byte
    out[0] = (byte)(0x18 | channel);
    byte[] in = super.transfer(out);
    int val = ((in[1] & 0x3f)<< 4 ) | ((in[2] & 0xf0) >> 4);
    // val is between 0 and 1023
    return float(val)/1023.0;
  }
}
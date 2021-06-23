// Pico Voice - voice changing effects by Mike Cook June 2021

#include "pico-voice.h"

void (*jumpTable[])(void) = { // functions to do the effect
    delaySound, reverb, reverb, pitchShift, twoVoices,
     backwardsC, backwardsR, dalek, vibrato, concrete };

static inline void cs_select() {
    asm volatile("nop \n nop \n nop");
    gpio_put(PIN_CS, 0);  // Active low
    asm volatile("nop \n nop \n nop");
}

static inline void cs_deselect() {
    asm volatile("nop \n nop \n nop");
    gpio_put(PIN_CS, 1);
    asm volatile("nop \n nop \n nop");
}

static void alarm_irq(void) {
    alarm_fired = true;
    hw_clear_bits(&timer_hw->intr, 1u << ALARM_NUM0); // Clear the alarm IRQ
    // call again in 25 uS
    uint64_t target = timer_hw->timerawl + samplePeriod;
    timer_hw->alarm[ALARM_NUM0] = (uint32_t) target; // set the timer for another 25uS
}

static void debounce_irq(void) {
    bounce_over = true;
    hw_clear_bits(&timer_hw->intr, 1u << ALARM_NUM1); // Clear the alarm IRQ
}

static void alarm_in_us(uint32_t delay_us, bool sample) {
    if(sample){
       hw_set_bits(&timer_hw->inte, 1u << ALARM_NUM0);
       irq_set_exclusive_handler(ALARM_IRQ0, alarm_irq);
       irq_set_enabled(ALARM_IRQ0, true);
   }
    else {
       // Enable the interrupt for our alarm (the timer outputs 4 alarm IRQ) 
       hw_set_bits(&timer_hw->inte, 1u << ALARM_NUM1);
       // Set irq handler for alarm irq
       irq_set_exclusive_handler(ALARM_IRQ1, debounce_irq);
       // Enable the alarm irq
       irq_set_enabled(ALARM_IRQ1, true);
   }
    // Enable interrupt in block and at processor
    uint64_t target = timer_hw->timerawl + delay_us;

    // Write the lower 32 bits of the target time to the alarm which
    // will arm it
    if(sample){
    timer_hw->alarm[ALARM_NUM0] = (uint32_t) target;
    }
    else {
    timer_hw->alarm[ALARM_NUM1] = (uint32_t) target;
   }
}

void pramStringOLED(int number, int8_t line){ // prints a right justified line with number
   int8_t stringCount = 0; 
   sprintf(strOLED, "%d", number);
   while(strOLED[stringCount] != 0) stringCount ++; // find null
   oledWriteString(&oled,0, 0, line, (char *)blankOLED, FONT_8x8, 0, 1);
   oledWriteString(&oled,0, 127 - (stringCount *8), line, (char *)strOLED, FONT_8x8, 0, 1);  
}

void floatStringOLED( float number, int8_t line){ // right justified float to OLED line
    int8_t stringCount = 0;
    sprintf(strOLED, "%.3f", number);
    while(strOLED[stringCount] != 0) stringCount ++; // find null 
    oledWriteString(&oled,0, 0, line, (char *)blankOLED, FONT_8x8, 0, 1);   
    oledWriteString(&oled,0, 127 - (stringCount *8), line, (char *)strOLED, FONT_8x8, 0, 1);
}

void changePram(int8_t value, int8_t num){
    switch(effectNumber){
       case 0: // delay
            inputPointer = 20000 * rotCount[0] + 20000 * (float) rotCount[1] / 100.0 ;
            workingBuffer = inputPointer;
            outputPointer[0] = 0;
            //printf("input pointer %d \n", inputPointer );
            if(inputPointer >= BUFFER_LEN){
                 inputPointer = BUFFER_LEN -1;
                 workingBuffer = inputPointer;
                 rotCount[0] = (BUFFER_LEN -1) / 20000;
                 rotCount[1] = ((BUFFER_LEN -1) % 20000) / 200;
             }
            floatStringOLED((float)rotCount[0] + (float) rotCount[1] / 100.0, 4);
           break;
            
       case 1: // reverb
            if(num == 0) {
            inputPointer = 20000 * (float) rotCount[0] / 1000.0 ;
            workingBuffer = inputPointer;
            // exponential output taps in time
            outputPointer[4] = 0;
            outputPointer[3] = inputPointer >> 1;
            outputPointer[2] = inputPointer >> 2;
            outputPointer[1] = inputPointer >> 3;
            outputPointer[0] = inputPointer >> 4;
            floatStringOLED((float) rotCount[0] / 1000.0, 4);
            }
            else {
                pramStringOLED(rotCount[1], 6);
            }
           break;    

       case 2: // echo
            if(num == 0) {
            inputPointer = 20000 * (float) rotCount[0] / 10.0 ;
            workingBuffer = inputPointer +1;
            outputPointer[4] = 0;
            int32_t q = inputPointer / 5;
            // linear output taps in time
            outputPointer[3] = q;
            outputPointer[2] = q+q;
            outputPointer[1] = q+q+q;
            outputPointer[0] = q+q+q+q;
            floatStringOLED((float) rotCount[0] / 10.0, 4);
            }
            else {
                pramStringOLED(rotCount[1], 6);
            }
           break;
               
       case 3: // Pitch up
            if(num == 0) {
            inputPointer = 20000 * (float) rotCount[0] / 1000.0 ;
            workingBuffer = inputPointer +1;
            floatStringOLED((float) rotCount[0] / 1000.0, 4);
            }
            else {
                floatStringOLED((float) rotCount[1] / 10.0, 6);
                outputIncF[0] = (float)rotCount[1] / 10.0;
            }
           break; 
              
       case 4: // Two voices
            if(num == 0) {
                floatStringOLED((float) rotCount[0] / 10.0, 4);
                outputIncF[0] = (float)rotCount[0] / 10.0;            }
            else {
                floatStringOLED((float) rotCount[1] / 10.0, 7);
                outputIncF[1] = (float)rotCount[1] / 10.0;
            }
           break;    

       case 5: // Backwards continuous
            if(num == 0) { // buffer length
                if(rotCount[0] == 0) rotCount[0] = 1; // avoid zero
                workingBuffer = 20000 * (float) rotCount[0] / 10.0; 
                outputPointer[0] = 0;
                floatStringOLED((float) rotCount[0] / 10.0, 4);
            }
           break;    

       case 6: // Backwards record
            if(num == 0) { // buffer length
                if(rotCount[0] == 0) rotCount[0] = 1; // avoid zero
                workingBuffer = 20000 * (float) rotCount[0] / 10.0; 
                outputPointer[0] = 0;
                floatStringOLED((float) rotCount[0] / 10.0, 4);
            }
            else { // trigger level
                triggerThreshold = thresholdSteps[rotCount[1]];
                pramStringOLED(rotCount[1], 6);
            }
           break;
           
        case 7: // dalek 
            if(num == 0) {
                makeWave(value);
                oledWriteString(&oled,0,0,4,pramsDisplay1[rotCount[0]], FONT_8x8, 0, 1);
            }
            else {
                wavePointInc = (512.0 * (float)value) / 40000.0 ;
                pramStringOLED(rotCount[1], 6);
            }
            break;
                           
       case 8: // vibrato
           if(num == 0) { // vibrato depth
               if(value == 0) {
                   value = 1;
                   rotCount[0] = 1;
               }
                vibDepth = 20.0 - (float)value;
                pramStringOLED(rotCount[0], 4);
            }
            else {
                wavePointInc = (1024.0 * (float)value) / 40000.0 ;
                pramStringOLED(rotCount[1], 6);
            }
           break;
               
      case 9: // concrete
            if(num == 0) { // buffer length
                if(rotCount[0] == 0) rotCount[0] = 1; // avoid zero
                workingBuffer = 20000 * (float) rotCount[0] / 10.0; 
                outputPointer[0] = 0;
                int32_t q = workingBuffer / 5;
                // linear output taps in time
                outputPointer[4] = 5000; quarterLength[4] = outputPointer[4]  = q;
                outputPointer[3] = q; quarterLength[3] = outputPointer[3] + q;
                outputPointer[2] = q+q; quarterLength[2] = outputPointer[2] + q;
                outputPointer[1] = q+q+q; quarterLength[1] = workingBuffer;
                floatStringOLED((float) rotCount[0] / 10.0, 4);
            }
            else { // trigger level
                triggerThreshold = thresholdSteps[rotCount[1]];
                pramStringOLED(rotCount[1], 6);
            }
           break;    
     }
}

void displayEffect(){
    switch(effectNumber){
        case 0:
            //printf("Delay\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Delay", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            break;
        case 1:
            //printf("Reverb\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Reverb", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Feedback %", FONT_8x8, 0, 1);
            break;
         case 2:
            //printf("Echo Chamber\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Echo", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Feedback %", FONT_8x8, 0, 1);
            break;
         case 3:
            //printf("Pitch Shift\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Pitch Shift", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Buffer", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Pitch X", FONT_8x8, 0, 1);
            break;
         case 4:
            //printf("Two Voices\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Two Voices", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Voice 1 pitch X", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,6,(char *)"Voice 2 pitch X", FONT_8x8, 0, 1);
            break;
         case 5:
            //printf("Backwards continious\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Backwards", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,6,(char *)"Continuous", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,7,(char *)"Playback", FONT_8x8, 0, 1);
            break;            
         case 6:
            //printf("Backwards record\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"BackwardsR", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Trigger", FONT_8x8, 0, 1);
            break;            
         case 7:
            //printf("Dalek\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Dalek", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Waveform", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,4,pramsDisplay1[0], FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Speed Hz", FONT_8x8, 0, 1);
            pramStringOLED(30, 6);
            break;
         case 8:
            //printf("Vibrato\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Vibrato", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Depth", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Speed", FONT_8x8, 0, 1);
            break;
         case 9:
            //printf("Concrete\n");
            oledFill(&oled, 0,1);
            oledSetContrast(&oled, OLED_CONTRAST);
            oledWriteString(&oled,0,0,0,(char *)"Concrete", FONT_12x16, 0, 1);
            oledWriteString(&oled,0,0,3,(char *)"Seconds", FONT_8x8, 0, 1);
            oledWriteString(&oled,0,0,5,(char *)"Trigger", FONT_8x8, 0, 1);
            break;
          
        default: // incase BCD switch bounce gives you an invalid number
           //printf("Effect number %d out of range\n", effectNumber);
           oledFill(&oled, 0,1);
           oledSetContrast(&oled, OLED_CONTRAST);
           oledWriteString(&oled,0,0,0,(char *)"No effect", FONT_8x8, 0, 1);
           effectNumber = 0; // back to first effect
           break;       
        }
}

int8_t rot_look(uint gpio, uint32_t events, int8_t encoder ){     
    int8_t ck_level = 0;
    int8_t dt_level = 0;
    int8_t retVal = 0;
    static int8_t currentState[] = {3, 3};
    static int8_t lastState[] = {3, 3};
    static bool dir[] = {true, true};
    if(encoder){
        ck_level = gpio_get(rot_pin[2]); // get states as soon as possible
        dt_level = gpio_get(rot_pin[3]);
    }
    else {
        ck_level = gpio_get(rot_pin[0]); // get states as soon as possible
        dt_level = gpio_get(rot_pin[1]);
    }
    currentState[encoder] = (int8_t)((ck_level << 1) | dt_level);
    if(currentState[encoder] == 1 && lastState[encoder] == 3){ dir[encoder] = true; lastState[encoder] = currentState[encoder];}
    if(currentState[encoder] == 2 && lastState[encoder] == 3){ dir[encoder] = false; lastState[encoder] = currentState[encoder];}
    if(currentState[encoder] == 0 && lastState[encoder] == 1 && dir[encoder]) lastState[encoder] = currentState[encoder];
    if(currentState[encoder] == 2 && lastState[encoder] == 0 && dir[encoder]) lastState[encoder] = currentState[encoder];
    if(currentState[encoder] == 3 && lastState[encoder] == 0 && dir[encoder]) lastState[encoder] = 3;
    if(currentState[encoder] == 3 && lastState[encoder] == 1 && dir[encoder]) lastState[encoder] = 3;
    if(currentState[encoder] == 3 && lastState[encoder] == 2 && dir[encoder]) {lastState[encoder] = currentState[encoder]; retVal = 1;}
    if(currentState[encoder] == 0 && lastState[encoder] == 2 && !dir[encoder]) lastState[encoder] = currentState[encoder];
    if(currentState[encoder] == 1 && lastState[encoder] == 0 && !dir[encoder]) lastState[encoder] = currentState[encoder];
    if(currentState[encoder] == 3 && lastState[encoder] == 0 && !dir[encoder]) lastState[encoder] = 3;
    if(currentState[encoder] == 3 && lastState[encoder] == 2 && !dir[encoder]) lastState[encoder] = 3;
    if(currentState[encoder] == 3 && lastState[encoder] == 1 && !dir[encoder]) {lastState[encoder] = currentState[encoder]; retVal = -1;}
        
    return retVal;
 }
 
void gpio_callback(uint gpio, uint32_t events){ // encoder 0
    if(gpio == rot_pin[0] || gpio == rot_pin[1]){ 
       int16_t reading = rot_look(gpio, events, 0);
       rotCount[0] += reading;
       if(reading != 0) {
           if(rotCount[0] > pramLimit0[effectNumber] ) rotCount[0] = 0;
           if(rotCount[0] < 0) rotCount[0] = pramLimit0[effectNumber];           
           changePram(rotCount[0], 0);           
       }
       return;
       }
    if(gpio == rot_pin[2] || gpio == rot_pin[3]){ // encoder 1
       int16_t reading = rot_look(gpio, events, 1);
       rotCount[1] += reading;
       if(reading != 0) {
           if(rotCount[1] > pramLimit1[effectNumber] ) rotCount[1] = 0;
           if(rotCount[1] < 0) rotCount[1] = pramLimit1[effectNumber]-1;
           changePram(rotCount[1], 1);
       }
       return;  
    }    
    if(gpio >= SELECT_1 && gpio <= SELECT_8) {
        uint32_t newEffect = (((gpio_get_all() & selectMask) >> (SELECT_1)) & 0xF) ^ 0xF;
        if(newEffect != effectNumber){
           effectNumber = newEffect;
           displayEffect();
    }
   }
    else {
        //printf("Rotary encoder push event pin %d\n", gpio);
        if(gpio == ROT_SW2 && currentEffect == 9) finishedPlayback = true;
     }
}

void gpio_setup(){
// select pins init
    for(int8_t i = 0; i<6; i++){
        gpio_init(select_pin[i]);
        gpio_set_dir(select_pin[i], GPIO_IN);
        gpio_set_pulls(select_pin[i], true, false);
        gpio_set_irq_enabled_with_callback(select_pin[i], GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &gpio_callback);
    }
// unfortunately all interrupts from GPIO pins will go to the same place 
    for(int8_t i = 0; i<4; i++){
        gpio_init(rot_pin[i]);
        gpio_set_dir(rot_pin[i], GPIO_IN);
        gpio_set_irq_enabled_with_callback(rot_pin[i], GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &gpio_callback);
    }
} 

void i2c_setup(){
    char szTemp[32];
    for(int8_t i = 0; i < 16; i++) blankOLED[i] = 0x20;
    blankOLED[16] = 0;
    rc = oledInit(&oled, OLED_128x64, 0x3c, 1, 0, 1, SDA_PIN, SCL_PIN, RESET_PIN, 1000000L);
	  if (rc != OLED_NOT_FOUND)
  { 
    oledFill(&oled, 0,1);
    oledSetContrast(&oled, 127);
    oledWriteString(&oled,0,0,0,(char *)"Pico Voice", FONT_12x16, 0, 1);
    sleep_ms(3000);
    }
}

void spi_setup(){
    // SPI initialisation use SPI at 8MHz.
    spi_init(SPI_PORT, 8000*1000); // 8MHz
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS,   GPIO_FUNC_SIO);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    // SPI Chip select is active-low, initialise it to high
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
}
 
void makeWave(int8_t type){ // type 0 = sine, 1 = saw, 2 = triangle, 3 = square
    float increment = 0.0;
    float point = 0.0;
    if(type == 0){ // sine wave
        for (int16_t i = 0; i < WAVE_TABLE_LEN; i++) {
            wave_table[i] = cosf(i * 2 * (float)(M_PI / (float)(WAVE_TABLE_LEN)));
    }
   }
    if(type == 1){ // saw tooth
        point = 0.0;
        increment = 1.0 / (WAVE_TABLE_LEN / 2);
        for (int16_t i = 0; i < WAVE_TABLE_LEN; i++) {
            wave_table[i] = point;
            point += increment;
            if(i == 256) {point = -0.99;}
    }
   }
   if(type == 2){ // triangle
       point = 0.0;
       increment = 2.0 / (WAVE_TABLE_LEN / 2);
       for (int16_t i = 0; i < WAVE_TABLE_LEN; i++) {
           wave_table[i] = point;
           point += increment;
           if(i == 127) increment = - increment;
           if(i == 383) increment = - increment;            
    }
   }
   if(type == 3){ // square
       point = 0.9999;
       for (int16_t i = 0; i < WAVE_TABLE_LEN; i++) {
           wave_table[i] = point;
           if(i == 255) point = - 0.9999;
       }
   }

}

void sendSample(int16_t sample){
    buf[1] = sample & 0xff; // least significant byte
    buf[0] = ((sample >> 8) & 0x0f) | daConfig; // most significant nibble
    while (!alarm_fired); // Wait for alarm to fire
    // send out the data to the D/A through the spi
    cs_select();
    spi_write_blocking(SPI_PORT, buf, 2);
    cs_deselect();
    alarm_fired = false; // reset alarm fired flag
} 

void delaySound(){ // delay between input sound and output
    sampleBuf[inputPointer] = adc_read();
    d_a_out = sampleBuf[outputPointer[0]];
    inputPointer += 1;
    if(inputPointer >= workingBuffer) inputPointer = 0;
    outputPointer[0] += 1;
    if(outputPointer[0] >= workingBuffer) outputPointer[0] = 0; 
    sendSample(d_a_out);
}

void reverb(){ // for both reverb and echo
    sampleBuf[inputPointer] = (adc_read()) >> 1;
    int16_t echoComponent = sampleBuf[outputPointer[0]];
    for(int8_t i = 1; i< 5 ;i++){
      echoComponent += ((int)((float)sampleBuf[outputPointer[i]] * (float)rotCount[1] / 100.0) >> (i-1)); 
    }
    d_a_out = (sampleBuf[inputPointer] + echoComponent) >> 1; 
    inputPointer += 1;
    if(inputPointer >= workingBuffer){ inputPointer = 0; } // printf("volume %.3f\n",(float)rotCount[1] / 100.0);}
    for(int8_t i = 0; i<5; i++) {
    outputPointer[i] += 1;
    if(outputPointer[i] >= workingBuffer) { 
        outputPointer[i] = 0; 
        }
    }
    sendSample(d_a_out);
}

void pitchShift(){ 
    sampleBuf[inputPointer] = adc_read();
    d_a_out = sampleBuf[(int)outputPointF[0]];
    inputPointer += 1;
    outputPointF[0] += outputIncF[0];
    if(inputPointer >= workingBuffer) inputPointer = 0;
    if(outputPointF[0] >= workingBuffer) outputPointF[0] = 0.0;
    sendSample(d_a_out);
}

void twoVoices(){
    sampleBuf[inputPointer] = adc_read();
    d_a_out = (sampleBuf[(int)outputPointF[0]] + sampleBuf[(int)outputPointF[1]]) >> 1;
    inputPointer += 1;
    outputPointF[0] += outputIncF[0];
    outputPointF[1] += outputIncF[1];
    if(inputPointer >= workingBuffer) inputPointer = 0;
    if(outputPointF[0] >= workingBuffer) outputPointF[0] = 0.0;
    if(outputPointF[1] >= workingBuffer) outputPointF[1] = 0.0;
    sendSample(d_a_out);
}

void backwardsC(){
    sampleBuf[inputPointer] = adc_read();
    d_a_out = sampleBuf[outputPointer[0]];
    inputPointer += 1;
    outputPointer[0] -= 1;
    if(inputPointer >= workingBuffer) inputPointer = 0;
    if(outputPointer[0] < 0) outputPointer[0] = workingBuffer;
    sendSample(d_a_out);

}

void backwardsR(){
    if(record){
        sampleBuf[inputPointer] = adc_read();
        sendSample(2040); // send out DC level to get a sample delay
        if(sampleBuf[inputPointer] > triggerThreshold) triggered = true;
        inputPointer += 1;
        // half a second pre trigger record
        if(inputPointer >= 10000 && !triggered) inputPointer = 0;
        if(inputPointer >= workingBuffer){ // finished recording
             inputPointer = 0;
             record = false;
             triggered = false;
             oledWriteString(&oled,0,0,7,(char *)"Play  ", FONT_8x8, 0, 1);
         }
     }
    else {     
        d_a_out = sampleBuf[outputPointer[0]];
        sendSample(d_a_out); 
        outputPointer[0] -= 1;
        if(outputPointer[0] < 0 ){ // finished playback that pointer
            outputPointer[0] = workingBuffer;
            record = true;
            oledWriteString(&oled,0,0,7,(char *)"Record", FONT_8x8, 0, 1);
        } 
    }
  } 

void dalek(){ // ring modulation at around 30Hz    
    waveSample = wave_table[(int)wavePoint];
    wavePoint += wavePointInc;
    if (wavePoint >= (float)WAVE_TABLE_LEN) wavePoint -= (float)WAVE_TABLE_LEN;
    d_a_out = 2047 + ((float)(adc_read() - 2047.0) * waveSample);
    sendSample(d_a_out);
}

void vibrato(){ // changing pitch in response to a waveform
    sampleBuf[inputPointer] = adc_read();
    d_a_out = sampleBuf[(int)outputPointF[0]];
    waveSample = wave_table[(int)wavePoint];
    outputIncF[0] = 0.5 + ((waveSample) / vibDepth);
    wavePoint += wavePointInc;    
    if (wavePoint >= (float)WAVE_TABLE_LEN) wavePoint -= (float)WAVE_TABLE_LEN;
    outputPointF[0] += outputIncF[0];
    inputPointer += 1;
    outputPointF[0] += outputIncF[0];
    if(inputPointer >= workingBuffer) inputPointer = 0;
    if(outputPointF[0] >= workingBuffer) outputPointF[0] = 0.0;
    sendSample(d_a_out);
}

void concrete(){ // record & playback in random order
    static int8_t playbackCount = 1;
    if(record){
        sampleBuf[inputPointer] = adc_read();
        sendSample(2040); // send out DC level to get a sample delay
        if(sampleBuf[inputPointer] > triggerThreshold) triggered = true;
        inputPointer += 1;
        // half a second pre trigger record
        if(inputPointer >= 10000 && !triggered) inputPointer = 0;
        if(inputPointer >= workingBuffer){ // finished recording
             inputPointer = 0;
             record = false;
             triggered = false;
             finishedPlayback = false; // repeat incase of push button bounce
             outputPointer[0] = outputPointer[playbackCount];
             oledWriteString(&oled,0,0,7,(char *)"Play  ", FONT_8x8, 0, 1);
         }
     }
     else {     
         d_a_out = sampleBuf[outputPointer[0]];
         sendSample(d_a_out); 
         outputPointer[0] += 1;
         if(outputPointer[0] >= quarterLength[playbackCount] ){ // one sample
             playbackCount = 1+ rand() % 4;
             //printf("playing pointer %d \n", playbackCount); 
             outputPointer[0] = outputPointer[playbackCount] ;
        }
        if(finishedPlayback) {
            record = true;
            finishedPlayback = false;
            oledWriteString(&oled,0,0,7,(char *)"Record", FONT_8x8, 0, 1);
        } 
    }
 
}
 
void prepareEffect(int effect){ // prepare program for this effect
    switch(effect) {        
    case 0:
     // prepare for sound delay
    rotCount[0] = 1;
    rotCount[1] = 0;
    inputPointer = 20000; // 1 second delay input pointer 20K from output pointer
    outputPointer[0] = 0; // always start with zero delay
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    floatStringOLED((float)rotCount[0], 4);
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;
    
    case 1:
     // prepare for reverb
    rotCount[0] = 100; // 100mS
    rotCount[1] = 50; // Echo add 50%
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    workingBuffer = inputPointer;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break; 

    case 2:
     // prepare for echo chamber
    rotCount[0] = 20; // 2 seconds
    rotCount[1] = 50; // Echo add 50%
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    workingBuffer = inputPointer;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;
              
    case 3:
     // prepare for pitch up
    rotCount[0] = 20; // 100 mS 
    rotCount[1] = 17; // default pitch up 1.7
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    workingBuffer = inputPointer;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;
              
    case 4:
     // prepare for two voices
    rotCount[0] = 9; // voice 1 default pitch down 0.9 
    rotCount[1] = 17; // voice 2 default pitch up 1.7
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    inputPointer = 70; // 35 mS
    workingBuffer = inputPointer;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;          

    case 5:
    // Backwards continuous
    rotCount[0] = 40; // four seconds
    changePram(rotCount[0], 0); // setup display of parameters
    inputPointer = 0;
    outputPointer[0] = workingBuffer;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;

    case 6:
    // Backwards record
    rotCount[0] = 15; // Buffer one tenth seconds
    rotCount[1] = 3; // Trigger level
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    inputPointer = 0;
    outputPointer[0] = workingBuffer;
    oledWriteString(&oled,0,0,7,(char *)"Record", FONT_8x8, 0, 1);
    triggered = false; 
    record = true;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;
    
    case 7:
     // prepare for dalek
    makeWave(0); // make a wave type in parameter
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 25;    
    wavePointInc = (512.0 * 30.0) / 40000.0 ; // about 30Hz
    rotCount[1] = 30; // speed
    rotCount[0] = 0;  // waveform
    break;
    
    case 8:
     // prepare for Vibrato
    makeWave(0); // make a wave type in parameter
    wavePointInc = (512.0 * 50.0) / 40000.0 ; // about 30Hz
    wavePoint = 0;
    rotCount[1] = 5; // speed
    rotCount[0] = 10;  // vibrato depth
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    workingBuffer = 20000.0 / 10.0; 
    inputPointer = 0;
    outputPointF[0] = 0.0;
    outputIncF[0] = 0.5; 
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50;
    break;
    
    case 9:
     // prepare for concrete
    rotCount[0] = 15; // Buffer one tenth seconds
    rotCount[1] = 3; // Trigger level
    changePram(rotCount[0], 0); // setup display of parameters
    changePram(rotCount[1], 1);
    inputPointer = 0;
    outputPointer[0] = workingBuffer;
    oledWriteString(&oled,0,0,7,(char *)"Record", FONT_8x8, 0, 1);
    triggered = false; 
    record = true;
    alarm_in_us(10, true); // sample IRQ
    samplePeriod = 50; // 20KHz sample rate to get longer maximum delay
    break;            
    }    
}
    
int main()
{
    //stdio_init_all();
    adc_init();
    gpio_setup();
    i2c_setup(); // sets up the OLED driver
    // adc input zero initialisation
    gpio_init(26);
    adc_select_input(0);
    for(int16_t i = 0; i<< adc_read(); i++){ // seed random number by calling an noise based number of times
       inputPointer = rand();
    }
    spi_setup();
    // read the BCD switch
    effectNumber = (((gpio_get_all() & selectMask) >> (SELECT_1)) & 0xF) ^ 0xF;
    displayEffect();
          
    while(1) { // do forever
    prepareEffect(effectNumber);
    currentEffect = effectNumber;
     while(currentEffect == effectNumber){
        jumpTable[currentEffect](); // go to sound routine
        }
     }
    return 0;
}

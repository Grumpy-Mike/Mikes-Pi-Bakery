#ifndef __PICOVOICE_H__
#define __PICOVOICE_H__


#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "hardware/timer.h"
#include "hardware/adc.h"
#include "hardware/irq.h"
#include "hardware/i2c.h"
#include <math.h>
#include "ss_oled.h"

// Function prototypes
static inline void cs_select();
static inline void cs_deselect();
static void alarm_irq(void);
static void debounce_irq(void);
static void alarm_in_us(uint32_t delay_us, bool sample);
void displayEffect();
int8_t rot_look(uint gpio, uint32_t events, int8_t encoder);
void gpio_callback(uint gpio, uint32_t events);
void gpio_setup();
void i2c_setup();
void spi_setup();
void makeWave(int8_t type);
void sendSample(int16_t sample);
void dalek();
void delaySound();
void reverb();
void pitchShift();
void twoVoices();
void backwardsC();
void backwardsR();
void vibrato();
void concrete();
void pramStringOLED(int number, int8_t line);
void floatStringOLED( float number, int8_t line);
void prepareEffect(int effect);
void changePram(int8_t value, int8_t num);
// end of function prototypes

// Global variables
float wavePointInc = 0.16; // about 30Hz
float wavePoint = 0.0; 
float waveSample;

// RPI Pico I2C bus
#define SDA_PIN 14
#define SCL_PIN 15
#define RESET_PIN -1
#define PICO_I2C i2c1
#define I2C_SPEED 1000 * 1000
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define OLED_CONTRAST 127

// SPI Defines use SPI 0, and allocate it to the following GPIO pins
#define SPI_PORT spi0
#define PIN_MISO 4
#define PIN_CS   5
#define PIN_SCK  2
#define PIN_MOSI 3
// pins used for external switch inputs
#define SELECT_8 21
#define SELECT_4 20
#define SELECT_2 19
#define SELECT_1 18

#define ROT_CK1 6
#define ROT_DT1 7
#define ROT_SW1 8
#define ROT_CK2 9
#define ROT_DT2 10
#define ROT_SW2 11

// global variables for SPI out
uint8_t buf[] = {0x6b, 0x00};
uint8_t daConfig = 0x70;
int16_t d_a_out = 0;
uint16_t samplIn;
bool playing = false;
bool release = false;
uint8_t effectNumber = 1;
uint8_t currentEffect = 1;

// Use alarm 0
#define ALARM_NUM0 0
#define ALARM_NUM1 1
#define ALARM_IRQ0 TIMER_IRQ_0
#define ALARM_IRQ1 TIMER_IRQ_1
#define DEBOUNCE 30000

uint32_t samplePeriod = 25; // uS
// Alarm interrupt handler
static volatile bool alarm_fired = false;
static volatile bool bounce_over = true;

// sound buffer
#define BUFFER_LEN 100000
static uint16_t sampleBuf[BUFFER_LEN]; // enough for 5 seconds delay
int32_t inputPointer = 0;
int32_t outputPointer[] = {0, 0, 0, 0, 0};
int32_t quarterLength[] = {0, 0, 0, 0, 0};
int32_t workingBuffer = 0;
float outputIncF[] = {0.0, 0.0};
float outputPointF[] = {0.0, 0.0};
int16_t thresholdSteps[] = {0,  2456, 2864, 3272};
int16_t triggerThreshold = 2084; // in effect triggered by noise
bool triggered = false, record = true, finishedPlayback = false; // for record control

#define WAVE_TABLE_LEN 512
float wave_table[WAVE_TABLE_LEN];

// for rotary encoders & BCD switches
int32_t selectMask = (1 << SELECT_8) | (1 << SELECT_4) | (1 << SELECT_2) | (1 << SELECT_1) ;
int32_t lastMaskRead;
uint8_t rot_pin[] = {ROT_CK1, ROT_DT1, ROT_CK2, ROT_DT2};
uint8_t select_pin[] = {SELECT_1, SELECT_2, SELECT_4, SELECT_8, ROT_SW1, ROT_SW2};
char* pramsDisplay1[] = {(char *)"             Sin", (char *)"             Saw", (char *)"        Triangle", (char *)"          Square"};
int16_t pramLimit0[] = {5, 199, 49, 100, 40, 49, 49, 3, 19, 49};  // limit for rotCount[0]
int16_t pramLimit1[] = {99, 99, 99, 100, 40, 1, 4, 126, 126, 4}; // limit for rotCount[1]
static int16_t rotCount [] = {0, 0};
float vibDepth = 10.0;
int16_t workingDelay = 0;

// for OLED display
int rc;
SSOLED oled;
//static uint8_t ucBuffer[1024]; // no OLED buffer required here
//uint8_t uc[8];
char strOLED[30]; // buffer for numbers conversion on OLED display
char blankOLED[17]; // buffer for right hand justified OLED line

#endif // __PICOVOICE_H__

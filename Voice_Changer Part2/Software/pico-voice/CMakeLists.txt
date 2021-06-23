# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.12)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# initalize pico_sdk from installed location
# (note this can come from environment, CMake cache etc)
#set(PICO_SDK_PATH /home/pi/pico/pico-sdk)

# from OLED example



# Pull in pico libraries that we need

# Pull in Pico SDK (must be before project)
include(pico_sdk_import.cmake)
project(pico-voice C CXX ASM)

# Initialise the Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

add_executable(pico-voice 
	pico-voice.c 
	BitBang_I2C.c 
	ss_oled.c)

target_include_directories(pico-voice PRIVATE  ${CMAKE_CURRENT_LIST_DIR}/include)

pico_set_program_name(pico-voice "pico-voice")
pico_set_program_version(pico-voice "0.1")

pico_enable_stdio_uart(pico-voice 0)
pico_enable_stdio_usb(pico-voice 1)

# Add the libraries
target_link_libraries(pico-voice
        pico_stdlib
        hardware_spi
        hardware_pio
        hardware_adc
        hardware_i2c
        )

# create map/bin/hex files etc.
pico_add_extra_outputs(pico-voice)


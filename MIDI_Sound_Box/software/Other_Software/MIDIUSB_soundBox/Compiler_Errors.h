/*******************************************************************************

 Bare Conductive Compiler Error Handler
 --------------------------------------
 
 Compiler_Errors.h - avoids incorrect builds due to wrong environment
 
 Bare Conductive code written by Stefan Dzisiewski-Smith and Peter Krige.
 
 This work is licensed under a MIT license https://opensource.org/licenses/MIT
 
 Copyright (c) 2016, Bare Conductive
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

*******************************************************************************/

#ifndef COMPILER_ERRORS_H
#define COMPILER_ERRORS_H

	// we only support Arduino 1.6.6 or greater
	#if ARDUINO < 10606
	  #error Please upgrade your Arduino IDE to 1.6.6 or greater
	#else 
		// check that Bare Conductive Touch Board is selected in Tools -> Board
		#if !defined(ARDUINO_AVR_BARETOUCH) || defined(IPAD_COMPAT)
		 	#error Please select "Bare Conductive Touch Board" in the Tools -> Board menu.
		#endif
 	#endif

#endif // COMPILER_ERRORS_H

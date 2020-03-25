#!/usr/bin/env python
# Class to decode mechanical rotary encoder pulses.
# by Mike Cook

import pigpio

class Ky040 :
   sw_debounce = 25000 # switch debounce time
   rot_debounce = 1000 # rotary debounce
   def __init__(self, clk = None, dt = None, cbrot=None, sw = None, cbr = None, cbf = None):
      if not clk or not dt or not cbrot :
         raise BaseException("The clk & dt pins and the callback function must be specified")
      self.callback = cbrot
      self.swFit = False 
      if sw and cbr and cbf: # if the switch being used
          self.swFit = True
          sw_input = pigpio.pi()
          self.sw = sw_input
          sw_input.set_mode(sw, pigpio.INPUT)
          sw_input.set_pull_up_down(sw, pigpio.PUD_UP)
          sw_input.set_glitch_filter(sw, self.sw_debounce)            
          self.swR = sw_input.callback(sw, pigpio.RISING_EDGE, cbr)
          self.swF = sw_input.callback(sw, pigpio.FALLING_EDGE, cbf)   
      self.pi = pigpio.pi()
      self.clk = clk
      self.dt = dt     
      self.pi.set_mode(clk, pigpio.INPUT)
      self.pi.set_mode(dt, pigpio.INPUT)      
      self.pi.set_pull_up_down(clk, pigpio.PUD_UP)
      self.pi.set_pull_up_down(dt, pigpio.PUD_UP)      
      self.pi.set_glitch_filter(self.clk, self.rot_debounce)
      self.pi.set_glitch_filter(self.dt, self.rot_debounce)
      #self.pi.set_glitch_filter(self.clk, 0)
      #self.pi.set_glitch_filter(self.dt, 0)
      self.cb1 = self.pi.callback(clk, pigpio.EITHER_EDGE, self._clock)
      self.cb2 = self.pi.callback(dt, pigpio.EITHER_EDGE, self._clock) 
      self.clkLev = 0 # Level of ck pin
      self.dtLev = 0  # Level of dt pin
      self.pp = None  # Previous pin to report

   def _clock(self, ep, level, t):
      if ep == self.clk: self.clkLev = level
      else: self.dtLev = level
      if self.pp != ep : 
          self.pp = ep
          if ep == self.clk and level == 1:
              if self.dtLev == 1:
                  self.callback(1)
          elif ep == self.dt and level == 1:
               if self.clkLev == 1:
                   self.callback(-1)

   def cancel(self):
      if self.swFit :
          self.swR.cancel()
          self.swF.cancel() 
          self.sw.stop()
      self.cb1.cancel()
      self.cb2.cancel()
      self.pi.stop()



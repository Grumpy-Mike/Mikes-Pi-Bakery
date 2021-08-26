# SPDX-FileCopyrightText: 2021 Jeff Epler, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# This example is adapted in part from micropython:
# https://github.com/micropython/micropython/pull/6894/files

# Modified by Mike Cook June 2021
# added scalling:- use 2 to return one increment per click, use 0 for steps of 4 increments
# added function to set the value of the count to allow wrap round, or limits of the count

import adafruit_pioasm
import board
import rp2pio
import array
import digitalio


class IncrementalEncoder:
    _state_look_up_table = array.array(
        "b",
        [
            # Direction = 1
            0,  # 00 to 00
            -1,  # 00 to 01
            +1,  # 00 to 10
            +2,  # 00 to 11
            +1,  # 01 to 00
            0,  # 01 to 01
            +2,  # 01 to 10
            -1,  # 01 to 11
            -1,  # 10 to 00
            +2,  # 10 to 01
            0,  # 10 to 10
            +1,  # 10 to 11
            +2,  # 11 to 00
            +1,  # 11 to 01
            -1,  # 11 to 10
            0,  # 11 to 11
            # Direction = 0
            0,  # 00 to 00
            -1,  # 00 to 01
            +1,  # 00 to 10
            -2,  # 00 to 11
            +1,  # 01 to 00
            0,  # 01 to 01
            -2,  # 01 to 10
            -1,  # 01 to 11
            -1,  # 10 to 00
            -2,  # 10 to 01
            0,  # 10 to 10
            +1,  # 10 to 11
            -2,  # 11 to 00
            +1,  # 11 to 01
            -1,  # 11 to 10
            0,  # 11 to 11
        ],
    )

    _sm_code = adafruit_pioasm.assemble(
        """
    again:
        in pins, 2
        mov x, isr
        jmp x!=y, push_data
        mov isr, null
        jmp again
    push_data:
        push
        mov y, x
    """
    )

    _sm_init = adafruit_pioasm.assemble("set y 31")

    def __init__(self, pin_a, pin_b, scale):
        if not rp2pio.pins_are_sequential([pin_a, pin_b]):
            raise ValueError("Pins must be sequential")
        if scale < 0 : scale = 0
        
        self._sm = rp2pio.StateMachine(
            self._sm_code,
            160_000,
            init=self._sm_init,
            first_in_pin=pin_a,
            in_pin_count=2,
            pull_in_pin_up=0b11,
            in_shift_right=False,
        )

        self._counter = 0
        self._direction = 0
        self._lut_index = 0
        self._buffer = bytearray(1)
        self._scale = scale

    def _update_state_machine(self, state):
        lut_index = self._lut_index | (state & 3)
        lut = self._state_look_up_table[lut_index]
        self._counter += lut
        if lut:
            self._direction = 1 if (lut > 0) else 0
        self._lut_index = ((lut_index << 2) & 0b1100) | (self._direction << 4)

    def deinit(self):
        self._sm.deinit()
        
    def setCounter(self, newValue):
        self._counter = newValue << self._scale
        
    def setScale(self, newValue):
        self._scale = newValue        

    @property
    def value(self):
        while self._sm.in_waiting:
            self._sm.readinto(self._buffer)
            self._update_state_machine(self._buffer[0])
        return self._counter >> self._scale


rotaryEncoder = IncrementalEncoder(board.GP10, board.GP11, 2)

old_value = None
while True:
    # limit readings between 0 to 127
    value = rotaryEncoder.value
    if old_value != value:
        if value < 0 : rotaryEncoder.setCounter(0)
        if value > 127 : rotaryEncoder.setCounter(127)
        print("Encoder:", rotaryEncoder.value)
        old_value = rotaryEncoder.value

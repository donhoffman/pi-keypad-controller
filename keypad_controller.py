#!/usr/bin/env python

import time
import logging

import matrix_keypad
import door_latch

KEYPAD_IDS = ['inside', 'outside']

def main():
    keypad1 = matrix_keypad.Keypad(0x20, 0)
    keypad2 = matrix_keypad.Keypad(0x20, 1)
    latch1 = door_latch.Latch(KEYPAD_IDS[0])
    latch2 = door_latch.Latch(KEYPAD_IDS[1])

    while True:
        ch = None
        ch = keypad1.getch()
        if ch:
            latch1.input(ch)
        ch = None
        ch = keypad2.getch()
        if ch:
            latch2.input(ch)
        time.sleep(0.01)


if __name__ == '__main__':
    main()
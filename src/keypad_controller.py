#!/usr/bin/env python

import logging
import time
from os import environ

import door_latch
import matrix_keypad

KEYPAD_IDS = ['inside', 'outside']
LOG_BASE_PATH = environ.get('LOG_BASE_PATH', './')
DB_BASE_PATH = environ.get('DB_BASE_PATH', './')

def main():
    log_location = LOG_BASE_PATH + 'keypad.log'
    logging.basicConfig(filename=log_location, level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s')
    logging.info('Starting Keypad Controller.')
    keypad0 = matrix_keypad.Keypad(0x20, 0)
    keypad1 = matrix_keypad.Keypad(0x20, 1)
    latch0 = door_latch.Latch(KEYPAD_IDS[0], 0)
    latch1 = door_latch.Latch(KEYPAD_IDS[1], 1)

    while True:
        ch = keypad0.getch()
        if ch:
            latch0.input(ch)

        ch = keypad1.getch()
        if ch:
            latch1.input(ch)

        time.sleep(0.01)


if __name__ == '__main__':
    main()
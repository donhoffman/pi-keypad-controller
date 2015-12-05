import datetime
import logging
import sqlite3
import time
from os import environ

import relays


class Latch:

    DIGIT_TIMEOUT = 60
    LOCKOUT_TIMEOUT = 300
    LOCKOUT_THRESHOLD = 5
    VALID_CH = set('0123456789#*')

    def __init__(self, latch_id, latch_index):
        self._logger = logging.getLogger(__name__)
        self._latch_id = unicode(latch_id).lower()
        self._latch_index = int(latch_index)
        self._digits = ''
        self._time_lastchar = 0
        self._time_end_lockout = None
        self._invalid_count = 0

    # noinspection PyMethodMayBeStatic
    def _db_connect(self):
        db_name = environ.get('DB_BASE_PATH', './') + 'keypad.db'
        return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


    def input(self, c):
        c = str(c)
        if c not in self.VALID_CH:
            return
        now = time.time()
        if (now - self._time_lastchar) > self.DIGIT_TIMEOUT:
            self._digits = ''
        self._time_lastchar = now
        if c not in '#*':
            self._digits += c
            return

        code = int(self._digits)
        self._digits = ''
        if c == '#':
            if self._validate_code(code):
                logging.info('Opening door \'%s\'', self._latch_id)
                relays.fire(self._latch_index)
        if c == '*':
            self._do_command(code)


    def _validate_code(self, code):
        #Check for lockout
        if self._time_end_lockout:
            if time.time() < self._time_end_lockout:
                logging.error("Code entered during lockout.")
                return False
            self._time_end_lockout = None

        conn = None
        try:
            conn = self._db_connect()
            c = conn.cursor()

            #Is this a valid user
            c.execute('SELECT name FROM users WHERE code=?', (int(code),) )
            row = c.fetchone()
            if not row:
                logging.error('Unknown code entered.')
                if ++self._invalid_count > self.LOCKOUT_THRESHOLD:
                    self._invalid_count = 0
                    self._time_end_lockout = time.now() + self.LOCKOUT_TIMEOUT
                return False

            #Note:  we don't lock out on permission issues
            #Valid user.  Check permissions.
            name = unicode(row[0])
            c.execute('''
              SELECT enabled, use_timeout, not_before, not_after
                FROM permissions WHERE name=? AND keypad_id=?''', (name, self._latch_id))
            row = c.fetchone()
            if not row:
                logging.error('User \'%s\' has no permissions.', name)
                return False
            enabled = bool(row[0])
            if not enabled:
                logging.error("Attempt to use disabled code for user %s", name)
                return False
            # noinspection PyUnusedLocal
            use_timeout = row[1]
            not_before = row[2]
            not_after = row[3]
            if not_before and datetime.now() < not_before:
                logging.error("Attempt to use code too soon for user %s", name)
                return False
            if not_after and datetime.now() > not_after:
                logging.error("Attempt to use expired code for user %s", name)
                return False
            logging.info("Valid code entered by user %s", name)
            return True
        except sqlite3.Error as e:
            logging.error("Database error: %s", e)
            return False
        finally:
            if conn:
                conn.close()


    def _do_command(self, code):
        pass


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='./keypad.log', level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s')
    test_code = '12345#'
    latch = Latch('Outside', 0)
    for ch in test_code:
        latch.input(ch)

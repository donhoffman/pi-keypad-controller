import time
import sqlite3

DB_NAME = "./keypad.db"

class Latch:

    DIGIT_TIMEOUT = 60
    VALID_CH = set('0123456789#*')

    def __init__(self, latch_id):
       self._latch_id = unicode(latch_id)
       self._digits = ''
       self._time_lastchar = int(0)

    def input(self, ch):
        ch = str(ch)
        if ch not in self.VALID_CH:
            return
        now = time.time()
        if (now - self._time_lastchar) > self.DIGIT_TIMEOUT:
            self._digits = ''
        self._time_lastchar = now
        if ch not in '#*':
            self._digits += ch
            return

        code = int(self._digits)
        self._digits = ''
        if ch == '#':
            self._validate_code(code)
        if ch == '*':
            self._do_command(code)


    def _validate_code(self, code):
        print 'Code for latch', self._latch_id, '-', str(code)
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('SELECT name FROM users WHERE code=?', (int(code),) )
            row = c.fetchone()
            if not row:
                return False
            name = unicode(row[0])
            c.execute('SELECT enabled FROM permissions WHERE name=? AND keypad_id=?',
                      (name, self._latch_id))
            row = c.fetchone()
            if not row:
                return False
            enabled = bool(row[0])
            return enabled
        except sqlite3.Error, e:
            return False
        finally:
            if conn:
                conn.close()


    def _do_command(self, code):
        pass


if __name__ == '__main__':
    latch = Latch('inside')
    latch.input('1')
    latch.input('2')
    latch.input('3')
    latch.input('4')
    latch.input('5')
    latch.input('#')
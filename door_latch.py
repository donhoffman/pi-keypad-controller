import time

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

    def _do_command(self, code):
        pass
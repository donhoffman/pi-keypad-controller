import smbus
import time

class Keypad:

    IODIRA = 0x00  # I/O direction register base address
    PULUPA = 0x0C  # PullUp enable register base address
    GPIOA = 0x12  # GPIO pin register base address
    OLATA = 0x14  # Output Latch register base address

    # Keypad Column output values
    KEYCOL = [0b11110111, 0b11111011, 0b11111101, 0b11111110]

    # Keypad keycode matrix (Storm 1000 Series)
    KEYCODE = [['1', '4', '7', '*'],  # KEYCOL0
               ['2', '5', '8', '0'],  # KEYCOL1
               ['3', '6', '9', '#'],  # KEYCOL2
               ['A', 'B', 'C', 'D']]  # KEYCOL3

    # Decide the row
    DECODE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 3, 0]

    # initialize I2C comm, 1 = rev2 Pi, 0 for Rev1 Pi
    i2c = smbus.SMBus(1)

    # get a keystroke from the keypad
    def getch(self):
        for col in range(0, 4):
            self.i2c.write_byte_data(self._i2c_addr, self.OLATA + self._port, self.KEYCOL[col])
            key = self.i2c.read_byte_data(self._i2c_addr, self.GPIOA + self._port) >> 4
            if key != 0b1111:
                row = self.DECODE[key]
                while (self.i2c.read_byte_data(self._i2c_addr, self.GPIOA + self._port) >> 4) != 15:
                    time.sleep(0.01)
                return self.KEYCODE[col][row]
        #No keypress
        return None


    # initialize the keypad class
    def __init__(self, addr, ioport):
        self._i2c_addr = int(addr)
        self._port = int(ioport)
        # upper 4 bits are inputs
        self.i2c.write_byte_data(self._i2c_addr, self.IODIRA + self._port, 0xF0)
        # enable upper 4 bits pull-ups
        self.i2c.write_byte_data(self._i2c_addr, self.PULUPA + self._port, 0xF0)

# test code
def main():
    keypad = Keypad(0x20, 0)
    while True:
        ch = None
        while not ch:
            ch = keypad.getch()
            time.sleep(0.01)
        print ch

        if ch == 'D':
            exit()

if __name__ == '__main__':
    main()
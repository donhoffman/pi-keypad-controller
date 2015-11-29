import smbus
import time

IODIRA = 0x00   # I/O direction register base address
PULUPA = 0x0C   # PullUp enable register base address
GPIOA = 0x12    # GPIO pin register base address
OLATA = 0x14    # Output Latch register base address

ADDR = 0x21     # Address on 12c bus
PORT = 1        # Which port, 0 or 1?

DEFAULT_ON_TIMEOUT = 3

i2c = smbus.SMBus(1)

RELAY_PIN = [0b10000000, 0b01000000]

# Set all pins as outputs.
i2c.write_byte_data(ADDR, IODIRA + PORT, 0)
i2c.write_byte_data(ADDR, PULUPA + PORT, 0)

def fire(relay_id, timeout=DEFAULT_ON_TIMEOUT):
    i2c.write_byte_data(ADDR, GPIOA + PORT, RELAY_PIN[relay_id])
    time.sleep(timeout)
    i2c.write_byte_data(ADDR, GPIOA + PORT, 0)


if __name__ == '__main__':
    while True:
        print 'Turning on...\a'
        i2c.write_byte_data(ADDR, GPIOA + PORT, 0b01000000)
        time.sleep(5)
        print 'Turning off...\a'
        i2c.write_byte_data(ADDR, GPIOA + PORT, 0)
        time.sleep(5)

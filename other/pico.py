from machine import Signal, Pin, Timer
import time

# Pins
TX_PIN = 4
RX_PIN = 5

READERS_CLOCK_PIN = 16
READERS_LOAD_PIN = 17
READERS_DATA_PIN = 18

CLOCK = 19
RESET = 20

# Communication
START_BYTE = 0x5a

CMD_READ = 0x01
CMD_RESET = 0x02
CMD_CLOCK_UP = 0x03
CMD_CLOCK_DOWN = 0x04

RESP_READY = 0x10
RESP_OK = 0x20

# Delays
DELAY_RESETTING = 100  # ms


class Readers:
    MODULE_COUNT = 1
    MODULE_IO_BITS = 8
    MODULE_IO_COUNT = 4

    S_TO_NS_DIVIDER = 1_000_000_000

    def __init__(self, clock_pin: int, load_pin: int, data_pin: int) -> None:
        # Initialising
        self.clock = Pin(clock_pin, Pin.OUT)
        self.load = Pin(load_pin, Pin.OUT)
        self.data = Pin(data_pin, Pin.IN)

        # Inverting
        self.clock = Signal(self.clock, invert=False)
        self.load = Signal(self.load, invert=True)
        self.data = Signal(self.data, invert=False)

    @classmethod
    def turn_delay(cls, pin: Signal, delay=0.1) -> None:
        pin.on()
        time.sleep(delay) # / cls.S_TO_NS_DIVIDER)
        pin.off()
        time.sleep(delay) # / cls.S_TO_NS_DIVIDER)
    
    def read(self) -> Iterator[bytes]:
        self.turn_delay(self.load)
        
        for _ in range(self.MODULE_COUNT * self.MODULE_IO_COUNT):
            integer = 0b00000000

            for i in range(self.MODULE_IO_BITS):
                self.turn_delay(self.clock)
                integer |= self.data.value() << i
                print(self.data.value(), end="")
            print()
            yield integer
                
    def read_bytes(self) -> list[bytes]:
        return bytes(self.read())


if __name__ == "__main__":
    # uart = UART(1, 9600, parity=None, stop=1, bits=8, rx=Pin(RX_PIN), tx=Pin(TX_PIN))
    readers = Readers(READERS_CLOCK_PIN, READERS_LOAD_PIN, READERS_DATA_PIN)

    clock = Pin(CLOCK, Pin.OUT)
    reset = Pin(RESET, Pin.OUT)
    
    # uart.write()
    # input()
    # print(bytes([RESP_READY]))
    
    while True:
        readers.read_bytes()
        print("===")
        
        readed = input()
        
        if readed and readed[0] == START_BYTE:
            command = readed[1]
            
            print(command)

            if command == CMD_READ:
                cpu_data = readers.read_bytes()
                
                # uart.write(posilam_filipovi)
                print(cpu_data)

            elif command == CMD_CLOCK_UP:
                clock.on()

            elif command == CMD_CLOCK_DOWN:
                clock.off()

            elif command == CMD_RESET:
                reset.on()
                time.sleep_ms(DELAY_RESETTING)

                for i in range(10):
                    clock.on()
                    time.sleep_ms(DELAY_RESETTING)
                    clock.off()
                    time.sleep_ms(DELAY_RESETTING)

                reset.off()

                # uart.write(bytes([RESP_OK]))
                print(bytes([RESP_OK]))

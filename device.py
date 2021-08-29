from serial.tools.list_ports_common import ListPortInfo
from serial import Serial

import serial.tools.list_ports
import time


class Reader:
    BITS = 32

    def __init__(self, variable: str, inverted_x=False, inverted_y=False):
        self.variable = variable
        self.inverted_x = inverted_x
        self.inverted_y = inverted_y

    @staticmethod
    def swap_bits(n, p1, p2):
        # Move p1'th to rightmost side
        bit1 = (n >> p1) & 1

        # Move p2'th to rightmost side
        bit2 = (n >> p2) & 1

        # XOR the two bits
        x = (bit1 ^ bit2)

        # Put the xor bit back to their original positions
        x = (x << p1) | (x << p2)

        # XOR 'x' with the original number so that the
        # two sets are swapped
        result = n ^ x

        return result

    def normalize(self, data: int) -> int:
        """
        Normalize data
        :param data: raw data
        :return: normalized data
        """

        if self.inverted_x:
            for bit in range(0, self.BITS // 2, 2):
                data = self.swap_bits(data, bit, self.BITS - bit)

        if (self.inverted_x and not self.inverted_y) or self.inverted_y:
            for bit in range(0, self.BITS, 2):
                data = self.swap_bits(data, bit, bit + 1)

        return data


class Device:
    BAUDRATE = 115_200

    ARDUINO_READY = "<Arduino Ready>"
    PONG = "hello"

    DELIMITER = ","

    DELAY = 0.05

    def __init__(self, socketio):
        self.__socketio = socketio
        self.serial = Serial()

        self.readers = [
            Reader("self.data.write_back", inverted_y=True),
            Reader("self.data.read_register_1"),
            Reader("self.data.PC_to_IM", inverted_y=True)
        ]

    @staticmethod
    def scan_ports() -> serial.tools.list_ports.comports:
        return serial.tools.list_ports.comports()

    def read_output(self):
        assert self.serial.is_open, "Serial is not initialized"
        return self.serial.readline().decode("utf-8").strip()

    def command(self, command):
        self.serial.write(command + b"\n")
        return self.read_output()

    def start(self, port: str):
        if not self.serial.is_open:
            self.serial = Serial(port, self.BAUDRATE, timeout=.1)

            while True:
                out = self.read_output()
                if out == self.ARDUINO_READY:
                    break

        self.__socketio.emit("connect_confirmation", namespace="/pineapple")

    def close(self):
        assert self.serial.is_open, "Serial is closed"

        self.serial.close()

    def ping(self):
        return self.command(b"H") == self.PONG

    def get_data(self):
        numbers = self.command(b"GD").rstrip(self.DELIMITER).split(self.DELIMITER)

        for n, i in enumerate(numbers):
            yield self.readers[n].variable, self.readers[n].normalize(int(i, 16))

    def clock_up(self):
        return self.command(b"CU")

    def clock_down(self):
        return self.command(b"CD")

    def reset(self):
        self.command(b"RU")
        time.sleep(self.DELAY)

        for i in range(10):
            self.clock_up()
            time.sleep(self.DELAY)
            self.clock_down()
            time.sleep(self.DELAY)

        self.command(b"RD")
        time.sleep(self.DELAY)
        self.clock_up()
        time.sleep(self.DELAY)
        self.clock_down()

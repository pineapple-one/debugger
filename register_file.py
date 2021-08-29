from block import Block
from data import Data
import numpy


class RegisterFile(Block):
    """
    Register File

    Inputs:
     - instruction from InstructionMemory

    Outputs:
     - write_back
     - Read_register_1
     - Read_register_2
    """

    def __init__(self, data: Data) -> None:
        super().__init__(data)

        self.registers = numpy.zeros(32)

        self.register_names = [
            "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
            "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6"
        ]

    def clock_up(self):
        self.write()
        self.read()
        self.mux()

    def clock_down(self):
        self.read()
        self.mux()

    def write(self) -> None:
        write_register = self.data.instruction & 0b00000000000000000000111110000000  # 11-7        
        write_to_register = write_register >> 7

        if self.data.RF_STORE and write_to_register != 0:
            self.registers[write_to_register] = self.data.write_back

            self.data.read_register_1 = self.data.write_back
            self.data.read_register_2 = self.data.write_back

            # write to reg 0x15 <-- 0x0000001
            # logger.info(f"write to reg {hex(write_to_register)} ({self.register_names[write_to_register]}) <-- 0x{hex(int(self.data.write_back))[2:].zfill(8)}")
            # "write to reg " + hex(write_to_register) + " <-- 0x" + hex(self.data.write_back))

    def read(self) -> None:
        write_register = self.data.instruction & 0b00000000000000000000111110000000  # 11-7        
        write_to_register = write_register >> 7

        # Read from - Instruction Memory - instruction
        read_register_1 = self.data.instruction & 0b00000000000011111000000000000000  # 19-15
        read_register_2 = self.data.instruction & 0b00000001111100000000000000000000  # 24-20        

        assert not (self.data.RF_STORE and self.data.RF_LOAD), Exception("RF_LOAD and RF_STORE cannot be true at once!")

        # Jenom pro propuštění hodnot
        if self.data.RF_STORE and write_to_register != 0:
            self.data.read_register_1 = self.data.write_back

        if self.data.RF_STORE and write_to_register != 0:
            self.data.read_register_2 = self.data.write_back

        if not self.data.RF_STORE and not self.data.RF_LOAD:
            self.data.read_register_1 = 0b00000000000000000000000000000000
            self.data.read_register_2 = 0b00000000000000000000000000000000

        # Mode loading
        if self.data.RF_LOAD:
            if read_register_1 >> 15 == 0:
                self.data.read_register_1 = 0
            else:
                self.data.read_register_1 = int(self.registers[read_register_1 >> 15])

            if read_register_2 >> 20 == 0:
                self.data.read_register_2 = 0
            else:
                self.data.read_register_2 = int(self.registers[read_register_2 >> 20])

            # RB0_should_be = self.debug_data.get_value("RB0", self.data.pulse_count)
            # RB1_should_be = self.debug_data.get_value("RB1", self.data.pulse_count)

            # logger.info(f"reading RB0: {hex(read_register_1 >> 15)} ({self.register_names[read_register_1 >> 15]}) = 0x{hex(int(self.data.read_register_1))[2:].zfill(8)} (should be: 0x{hex(RB0_should_be)[2:].zfill(8)})")
            # logger.info(f"reading RB1: {hex(read_register_2 >> 20)} ({self.register_names[read_register_2 >> 20]}) = 0x{hex(int(self.data.read_register_2))[2:].zfill(8)} (should be: 0x{hex(RB1_should_be)[2:].zfill(8)})")
            #
            # if RB0_should_be != self.data.read_register_1:
            #     # logger.error("RB0 error!!")
            #
            # if RB1_should_be != self.data.read_register_2:
            #     # logger.error("RB1 error!!")

            # logger.info("reg1: " + hex(read_register_1 >> 15) + " --> 0x" + hex(int(self.data.read_register_1)))
            # logger.info("reg2: " + hex(read_register_2 >> 20) + " --> 0x" + hex(int(self.data.read_register_2)))

    def mux(self):
        if not self.data.ALU_SRC:
            self.data.mux_out = self.data.read_register_2

        elif self.data.ALU_SRC:
            self.data.mux_out = self.data.immediate_value
            # slli x2 x2 1
            # 0x00111113

# if __name__ == "__main__":
#     RegisterFile(Data())

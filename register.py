from block import Block
from data import Data


class Register(Block):
    def __init__(self, data: Data) -> None:
        super().__init__(data)

        self.stored_value = 0b00000000000000000000000000000000

    def clock_up(self):
        self.at_clock()
        self.paste()

    def clock_down(self):
        self.paste()

    # def clock_down(self):
    #     # self.at_clock()

    def at_clock(self):
        assert not (self.data.MEM_LOAD and self.data.ALU_G), Exception("MEM_LOAD and ALU_G cannot be true at once!")

        if (self.data.MEM_LOAD or self.data.ALU_G) and self.data.uCounter == 0:
            # logger.info("Proběhla podmínka")
            self.stored_value = 0

        else:
            if self.data.MEM_LOAD:
                self.stored_value = self.data.ram_out
                # logger.info(f"stored from RAM {self.stored_value},\t0b{bin(self.stored_value)[2:].zfill(32)}")

            if self.data.ALU_G:
                self.stored_value = self.data.alu_out
                # logger.info(f"stored from ALU {self.stored_value},\t0b{bin(self.stored_value)[2:].zfill(32)}")
            #
            if (not self.data.ALU_G and not self.data.MEM_LOAD) and not self.data.RF_STORE:  # chyba!
                self.stored_value = 0

            # logger.info(f"REG_RTB_G: {self.data.REG_RTB_G}  MEM_LOAD: {self.data.MEM_LOAD} ALU_G: {self.data.ALU_G}")

    def paste(self):
        # logger.info(f"here, {self.data.REG_RTB_G=}, {self.data.SH_RTB_EN=}")

        if not self.data.REG_RTB_G and self.data.uCounter == 0:
            # logger.info(f"Putting 0 to write back")
            self.stored_value = 0
            self.data.write_back = self.stored_value

        if not self.data.REG_RTB_G:
            # logger.info(f"Pasted value: {self.stored_value}")
            self.data.write_back = self.stored_value

            # logger.info(f"stored from ALU {self.stored_value},\t0b{bin(self.stored_value)[2:].zfill(32)}")
            # logger.info(f"read RB0: {hex(read_register_1 >> 15)} ({self.register_names[read_register_1 >> 15]}) <-- 0x{hex(int(self.data.read_register_1))[2:].zfill(8)}")

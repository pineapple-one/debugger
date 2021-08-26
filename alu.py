from block import Block
from data import Data


class ALU(Block):
    """ 
    Inputs:
        - X - 32b vstupní data
        - Y - 32b vstupní data
        - i - 31. bit v instruckti (předposlední)

        - funct3: 
            000: add ('i' = 0)
            000: sub ('i' = 1)
            010: slt (set if less than) (pokud pravda tak výsledek = 1)
            011: sltu (set if less than unsigned) (pokud pravda tak výsledek = 1)
            100: xor
            110: or
            111: and

        - funct3; porovnávání: (nastavování 'branch' pokud je to pravda)
            000: beq (branch if equal)
            001: bne (branch if not equal)
            100: blt (branch if less than)
            101: bge (branch if greater or equal)
            110: bltu (branch if less than unsigned)
            111: bgeu (branch if greater or equal unsigned)

    Outputs:
        - result - 32b ouptut
        - branch - 1b, potvrzení podmíněného skoku

    """

    def __init__(self, data: Data) -> None:
        super().__init__(data)

    def clock_up(self):
        self.at_clock()

    def clock_down(self):
        self.at_clock()

    def at_clock(self):
        result = 0

        prepared_instruction = bin(self.data.instruction)[2:].zfill(32)
        funct3 = int(prepared_instruction[17:20], 2)
        i = int(prepared_instruction[1], 2)

        # funct3 = (self.data.instruction & 0b00000000000000000111000000000000) >> 12
        # i = (self.data.instruction & 0b01000000000000000000000000000000) >> 30
        # print(prepared_instruction, funct32, funct3)

        X = self.data.read_register_1
        Y = self.data.mux_out

        # logger.info(f"DEBUG -> RB0: {self.data.read_register_1}, MUXO: {self.data.mux_out}, f3: {funct3}, i: {i}")

        n = X & 0xffffffff
        signed_X = (n ^ 0x80000000) - 0x80000000

        n = Y & 0xffffffff
        signed_Y = (n ^ 0x80000000) - 0x80000000

        alu_op_0 = self.data.ALU_OP_0
        alu_op_1 = self.data.ALU_OP_1
        if alu_op_0 and not alu_op_1:
            funct3 = 0
            i = 0

        elif alu_op_1:
            i = 0

        # --------------------------------
        #             ALU
        # --------------------------------

        self.data.Branch = 0

        if funct3 == 0b000:
            # add
            if i == 0:
                result = (X + Y) & 0xffffffff

            # sub
            else:
                result = (X - Y) & 0xffffffff

            # beq
            if X == Y:
                self.data.Branch = 1

        # bne
        elif funct3 == 0b001:
            if X != Y:
                self.data.Branch = 1

        # slt
        elif funct3 == 0b010:
            if signed_X < signed_Y:
                result = 1

        # sltu
        elif funct3 == 0b011:
            if X < Y:
                result = 1

        # xor
        elif funct3 == 0b100:
            result = X ^ Y

            # blt
            if signed_X < signed_Y:
                self.data.Branch = 1

        # bge
        elif funct3 == 0b101:
            if signed_X >= signed_Y:
                self.data.Branch = 1

        # or
        elif funct3 == 0b110:
            result = X | Y

            # bltu
            if X <= Y:
                self.data.Branch = 1

        # and
        elif funct3 == 0b111:
            result = X & Y

            # bgeu
            if X >= Y:
                self.data.Branch = 1

        self.data.alu_out = int(result) & 0xffffffff

        # ALU_should_be = self.debug_data.get_value("ALU", self.data.pulse_count)
        # logger.info(f"Operand X: {X}  Y: {Y}")
        # logger.info(
        #     f"ALU result = {result} (0x{hex(result)[2:].zfill(8)})  Branch = {is_branch} (should be: 0x{hex(ALU_should_be)[2:].zfill(8)})")

        # if ALU_should_be != result:
        #     # logger.error("ALU error!!")

# if __name__ == '__main__':
#     f3 = 0b000
#     i = 0
#
#     data = Data()
#     alu = ALU(data, logger)
#
#     data.ALU_OP_0 = 0
#     data.ALU_OP_1 = 0
#
#     data.read_register_1 = 0xffffffff & 1
#     data.mux_out = 0xffffffff & 0
#     data.instruction = (f3 << 12) | (i << 30)
#
#     alu.at_clock()
#     print(f"result: {data.alu_out}, 0b{bin(data.alu_out)[2:].zfill(32)}")
#     print(f"branch: {data.Branch}")

from block import Block
from data import Data


class ImmediateGenerator(Block):
    """
    Dekóduje konstanty z instrukce.

    Máme 6 typů instrukcí (R, I, S, SB, U, UJ), z toho 5 má v sobě nějaké konstanty (všechny mimo typ R)
    (Více na https://i.stack.imgur.com/Gkjuc.png)

    Inputs:
    - INS - 32 bitová instrukce z instruction memory
    - IMM_GEN_CTR[0:3]

    Outputs:
    - IMM_to_PC - vygenerovaná konstanta
    """

    def __init__(self, data: Data) -> None:
        """
        Init of Immediate generator

        return: None
        """

        super().__init__(data)

        self.local_immediate_value = 0b00000000000000000000000000000000  # 32 bit

        self.at_clock()  # Při inicializaci je potřeba náskok jednoho taktu

    def clock_up(self):
        self.at_clock()

    def clock_down(self):
        self.at_clock()

    def at_clock(self) -> None:
        # Předělá instrukci na binární hodnotu s doplněnýma nulama do 32b
        instruction = bin(self.data.instruction)[2:].zfill(32)
        imm_gen_ctr = (self.data.IMM_GEN_CTR_2 << 2) + (self.data.IMM_GEN_CTR_1 << 1) + (self.data.IMM_GEN_CTR_0 << 0)

        if imm_gen_ctr == 0:  # I-type
            immediate_11_0 = instruction[0:12]
            immediate_sign_bit = instruction[0]
            self.local_immediate_value = int(immediate_sign_bit * 20 + immediate_11_0, 2)

        elif imm_gen_ctr == 1:  # S-type
            immediate_4_0 = instruction[20:25]
            immediate_11_5 = instruction[0:7]
            immediate_sign_bit = instruction[0]
            self.local_immediate_value = int(immediate_sign_bit * 20 + immediate_11_5 + immediate_4_0, 2)

        elif imm_gen_ctr == 2:  # SB-type
            immediate_4_1 = instruction[20:24]
            immediate_10_5 = instruction[1:7]
            immediate_11 = instruction[24]
            immediate_12 = instruction[0]
            self.local_immediate_value = int(immediate_12 * 20 + immediate_11 + immediate_10_5 + immediate_4_1 + "0", 2)

        elif imm_gen_ctr == 3:  # U-type
            immediate_31_12 = instruction[0:20]
            self.local_immediate_value = int(immediate_31_12 + "0" * 12, 2)

        elif imm_gen_ctr == 4:  # UJ-type
            immediate_20 = instruction[0]
            immediate_10_1 = instruction[1:11]
            immediate_11 = instruction[11]
            immediate_19_12 = instruction[12:20]
            self.local_immediate_value = int(immediate_20 * 12 + immediate_19_12 + immediate_11 + immediate_10_1 + "0",
                                             2)

        self.data.immediate_value = self.local_immediate_value
        # logger.info(f"Immediate: {self.toSigned32(self.data.immediate_value)} (0x{hex(self.data.immediate_value)[2:].zfill(8)}); type select: {imm_gen_ctr}")

        if self.data.IMM_RTB_G == 0:
            # logger.info("immediate --> write_back")
            self.data.write_back = self.local_immediate_value

        # program_counter.at_clock()

    def toSigned32(self, n):
        n = n & 0xffffffff
        return n | (-(n & 0x80000000))

# if __name__ == "__main__":
#     # data = Data()
#     # data.instruction = 0x00080137
#     # data.IMM_GEN_CTR_0 = 1
#     # data.IMM_GEN_CTR_1 = 1
#     # data.IMM_GEN_CTR_2 = 0
#     # immediate_generator = ImmediateGenerator(data)
#     # immediate_generator.at_clock()
#     # print(hex(data.immediate_value))
#     instruction = 0b11110000111100001111000011110000
#     print(bin(instruction)[2:][0:10])

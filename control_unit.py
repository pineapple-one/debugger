from block import Block
from data import Data


class ControlUnit(Block):
    """
    Inputs:
    - CLK
    - CPU_BUSY - from Shifter
    - RST
    - OP_CODE - from Instruction Memory

    Outputs:
    - (uCounter)
    - MicroCodes - 24 bits

    Microcodes:
    - ALU_OP_0 (alu operation 0)
    - MEM_STORE (memory store - RAM)
    - RTB_SEL_0 (return bus select 0)
    - PC_SRC_0 (program counter select source 0)
    - RTB_SEL_1 (return bus select 1)
    - ALI_OP_1 (alu operation 1)
    - TAKE_BRANCH (conditional branch)
    - PC_SRC_1 (program counter select source 0)
    - IMM_GEN_CTR_0 (immediate generator control 0)
    - IMM_GEN_CTR_1 (immediate generator control 1)
    - RF_STORE (register file store)
    - ALU_G (alu gate)
    - PCE (program counter enable)
    - RESERVED_0 (reserved - nothing)
    - ALU_SRC (alu source)
    - RESERVED_1 (reserved - nothing)
    - SH_LOAD (shifter load)
    - SH_LATCH (shifter latch)
    - RF_LOAD (register file load)
    - MEM_LOAD (memory load - RAM)
    - IMM_GEN_CTR_2 (immediate generator control 2)
    """

    DICTIONARY = {
        # Instructions:
        # add, sub, slr, sll, xor, or, sra, and
        0x33:
            [
                ["ALU_G", "SH_LATCH", "RF_LOAD"],
                ["ALU_G", "SH_LOAD", "RF_LOAD"],
                ["RF_STORE"],
                ["PCE"]
            ],

        # Instructions:
        # lb, lh, lw, lbu, lhu
        0x3:
            [
                ["ALU_OP_0", "ALU_SRC", "RF_LOAD", "MEM_LOAD"],
                ["RF_STORE"],
                ["PCE"]
            ],

        # Instructions:
        # addi, slli, xori, ori, srai, srli, andi
        0x13:
            [
                ["ALU_OP_0", "ALU_OP_1", "ALU_SRC", "SH_LATCH", "RF_LOAD"],
                ["ALU_OP_0", "ALU_OP_1", "ALU_G", "ALU_SRC", "SH_LOAD", "RF_LOAD"],
                ["ALU_OP_0", "ALU_OP_1", "RF_STORE", "ALU_SRC"],
                ["PCE"]
            ],

        # Instructions:
        # sb, sh, sw
        0x23:
            [
                ["ALU_OP_0", "MEM_STORE", "IMM_GEN_CTR_0", "ALU_SRC", "RF_LOAD"],
                ["PCE"]
            ],

        # Instructions:
        # beq, bne, blt, bge, bltu, bgeu
        0x63:
            [
                ["PC_SRC_0", "IMM_GEN_CTR_1", "RF_LOAD"],
                ["PC_SRC_0", "TAKE_BRANCH", "IMM_GEN_CTR_1", "PCE", "RF_LOAD"]
            ],

        # Instructions:
        # lui
        0x37:
            [
                ["RTB_SEL_0", "IMM_GEN_CTR_0", "IMM_GEN_CTR_1"],
                ["RTB_SEL_0", "IMM_GEN_CTR_0", "IMM_GEN_CTR_1", "RF_STORE"],
                ["PCE"]
            ],

        # Instructions:
        # jal
        0x6f:
            [
                ["RTB_SEL_1"],
                ["RTB_SEL_1", "RF_STORE"],
                ["PC_SRC_0", "PCE", "IMM_GEN_CTR_2"]
            ],

        # Instructions:
        # jalr
        0x67:
            [
                ["RTB_SEL_1"],
                ["RTB_SEL_1", "RF_STORE"],
                ["ALU_OP_1", "ALU_G", "ALU_SRC", "RF_LOAD"],
                ["ALU_OP_1", "PC_SRC_1", "ALU_G", "ALU_SRC", "RF_LOAD"],
                ["ALU_OP_1", "PC_SRC_1", "ALU_G", "PCE", "ALU_SRC", "RF_LOAD"]
            ],

        # Instructions:
        # auipc
        0x17:
            [
                ["PC_SRC_0", "RTB_SEL_1", "IMM_GEN_CTR_0", "IMM_GEN_CTR_1"],
                ["PC_SRC_0", "RTB_SEL_1", "IMM_GEN_CTR_0", "IMM_GEN_CTR_1", "RF_STORE"],
                ["PCE"]
            ]
    }

    def __init__(self, data: Data) -> None:
        # self.data.uCounter = 0
        self.uCounter_reset_delay = 0

        super().__init__(data)

    def init(self):
        self.clock_down()

    def clock_up(self) -> None:
        if self.data.CPU_BUSY == 0:
            if self.data.PCE == 1:
                self.data.uCounter = 0
                self.uCounter_reset_delay = 1  # Potřebný delay po resetu uCounteru pro podmínku výše
                self.clear_opcodes()
                self.instruction()
                # logger.info("")
                # logger.info(f"uCounter updated to: {self.data.uCounter}")
                # print(f"uCounter updated to: {self.data.uCounter}")
            self.decoder()

    def clock_down(self) -> None:
        if self.data.CPU_BUSY == 0:
            self.clear_opcodes()
            # if self.uCounter_reset_delay == 1: # Jeden takt se nesmí vykonat nic = po resetu uCounteru
            #     self.uCounter_reset_delay = 0

            # else:
            # logger.info(f"uCounter updated to: {self.data.uCounter}")
            # print(f"uCounter updated to: {self.data.uCounter}")
            # self.__socketio.emit("u_counter", self.data.uCounter, namespace="/pineapple")
            self.instruction()
            self.data.uCounter += 1

            self.decoder()

    # def init(self):
    #     # WHY ?!?!?
    #     # self.clock_down()
    #     # Místo toho jsem dal:
    #     # self.data.uCounter += 1
    #     self.clear_opcodes()
    #     self.instruction()
    #     self.decoder()

    # def clock_up(self) -> None:
    #     if self.data.CPU_BUSY == 0:
    #         if self.data.PCE == 1:
    #             self.data.uCounter = 0
    #             self.uCounter_reset_delay = 1  # Potřebný delay po resetu uCounteru pro podmínku výše
    #             self.clear_opcodes()
    #             self.instruction()
    #             # logger.info("")
    #             # logger.info(f"uCounter updated to: {self.data.uCounter}")
    #             # print(f"uCounter updated to: {self.data.uCounter}")
    #             # print("uCounter Reset = 1")
    #         self.decoder()

    #     print(f"-------- up, uC: {self.data.uCounter}")

    # def clock_down(self) -> None:
    #     if self.data.CPU_BUSY == 0:

    #         if self.uCounter_reset_delay == 1:  # Jeden takt se nesmí vykonat nic = po resetu uCounteru
    #             self.uCounter_reset_delay = 0
    #             # self.instruction()
    #             self.clear_opcodes()
    #             self.instruction()

    #         else:
    #         # logger.info(f"uCounter updated to: {self.data.uCounter}")
    #             # self.clear_opcodes()
    #             # self.instruction()
    #             self.clear_opcodes()
    #             self.instruction()
    #             self.data.uCounter += 1

    #         # print(f"uCounter updated to: {self.data.uCounter}")

    #         self.decoder()
    #     print(f"-------- dw, uC: {self.data.uCounter}")

    def instruction(self) -> None:
        opcode = self.data.instruction & 0b00000000000000000000000001111111

        # logger.info(self.DICTIONARY[opcode][self.data.uCounter])
        # print(self.DICTIONARY[opcode][self.data.uCounter])

        for i in self.DICTIONARY[opcode][self.data.uCounter]:
            # print(f"{i}")
            # obrovský if switch
            # self.# logger.info(i)
            if i == "ALU_OP_0":
                self.data.ALU_OP_0 = 1

            elif i == "MEM_STORE":
                self.data.MEM_STORE = 1

            elif i == "RTB_SEL_0":
                self.data.RTB_SEL_0 = 1

            elif i == "PC_SRC_0":
                self.data.PC_SRC_0 = 1

            elif i == "RTB_SEL_1":
                self.data.RTB_SEL_1 = 1

            elif i == "ALU_OP_1":
                self.data.ALU_OP_1 = 1

            elif i == "TAKE_BRANCH":
                self.data.TAKE_BRANCH = 1

            elif i == "PC_SRC_1":
                self.data.PC_SRC_1 = 1

            elif i == "IMM_GEN_CTR_0":
                self.data.IMM_GEN_CTR_0 = 1

            elif i == "IMM_GEN_CTR_1":
                self.data.IMM_GEN_CTR_1 = 1

            elif i == "RF_STORE":
                self.data.RF_STORE = 1

            elif i == "ALU_G":
                self.data.ALU_G = 1

            elif i == "PCE":
                self.data.PCE = 1

            elif i == "ALU_SRC":
                self.data.ALU_SRC = 1

            elif i == "SH_LOAD":
                self.data.SH_LOAD = 1

            elif i == "SH_LATCH":
                self.data.SH_LATCH = 1

            elif i == "RF_LOAD":
                self.data.RF_LOAD = 1

            elif i == "MEM_LOAD":
                self.data.MEM_LOAD = 1

            elif i == "IMM_GEN_CTR_2":
                self.data.IMM_GEN_CTR_2 = 1

            # TODO reset všech ostatních na nulu (funkce dole)

    def clear_opcodes(self) -> None:
        self.data.ALU_OP_0 = 0  # 0
        self.data.MEM_STORE = 0  # 1
        self.data.RTB_SEL_0 = 0  # 2
        self.data.PC_SRC_0 = 0  # 3
        self.data.RTB_SEL_1 = 0  # 4
        self.data.ALU_OP_1 = 0  # 5
        self.data.TAKE_BRANCH = 0  # 6
        self.data.PC_SRC_1 = 0  # 7
        self.data.IMM_GEN_CTR_0 = 0  # 8
        self.data.IMM_GEN_CTR_1 = 0  # 9
        self.data.RF_STORE = 0  # 10
        self.data.ALU_G = 0  # 11
        self.data.PCE = 0  # 12
        self.data.ALU_SRC = 0  # 14
        self.data.SH_LOAD = 0  # 16
        self.data.SH_LATCH = 0  # 17
        self.data.RF_LOAD = 0  # 18
        self.data.MEM_LOAD = 0  # 19
        self.data.IMM_GEN_CTR_2 = 0  # 20

    def cu_reset(self) -> None:
        # TODO
        """
        Reset Control Unit when reseting CPU
        return: None
        """
        pass

    def decoder(self) -> None:
        if self.data.SH_RTB_EN == 0:
            self.data.REG_RTB_G = 1
            self.data.IMM_RTB_G = 1
            self.data.PC_RTB_G = 1

        elif self.data.SH_RTB_EN == 1 and (self.data.RTB_SEL_0 == 0 and self.data.RTB_SEL_1 == 0):
            self.data.REG_RTB_G = 0
            self.data.IMM_RTB_G = 1
            self.data.PC_RTB_G = 1

        elif self.data.SH_RTB_EN == 1 and (self.data.RTB_SEL_0 == 0 and self.data.RTB_SEL_1 == 1):
            self.data.REG_RTB_G = 1
            self.data.IMM_RTB_G = 1
            self.data.PC_RTB_G = 0

        elif self.data.SH_RTB_EN == 1 and (self.data.RTB_SEL_0 == 1 and self.data.RTB_SEL_1 == 0):
            self.data.REG_RTB_G = 1
            self.data.IMM_RTB_G = 0
            self.data.PC_RTB_G = 1

        elif self.data.SH_RTB_EN == 1 and (self.data.RTB_SEL_0 == 1 and self.data.RTB_SEL_1 == 1):
            self.data.REG_RTB_G = 1
            self.data.IMM_RTB_G = 1
            self.data.PC_RTB_G = 1

            # logger.info(f"REG_RTB_G --> {self.data.REG_RTB_G} | IMM_RTB_G --> {self.data.IMM_RTB_G} | PC_RTB_G --> {self.data.PC_RTB_G}")

# if __name__ == "__main__":
#     d = Data()
#     d.instruction = 0b00000000000000000000000001100111
#
#     c = ControlUnit(d)
#     c.instruction()
#
#     for i in range(10):
#         c.clock_up()
#         c.clock_down()

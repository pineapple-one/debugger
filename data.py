class Data:
    def __init__(self):
        """
        Control codes
        """

        self.DIRECTORY = ""
        # @property
        # def ALU_OP_0():
        #     return self.ALU_OP_0

        self.ALU_OP_0 = 0  # 0
        self.MEM_STORE = 0  # 1
        self.RTB_SEL_0 = 0  # 2
        self.PC_SRC_0 = 0  # 3
        self.RTB_SEL_1 = 0  # 4
        self.ALU_OP_1 = 0  # 5
        self.TAKE_BRANCH = 0  # 6
        self.PC_SRC_1 = 0  # 7
        self.IMM_GEN_CTR_0 = 0  # 8
        self.IMM_GEN_CTR_1 = 0  # 9
        self.RF_STORE = 0  # 10
        self.ALU_G = 0  # 11
        self.PCE = 0  # 12
        self.ALU_SRC = 0  # 14
        self.SH_LOAD = 0  # 16
        self.SH_LATCH = 0  # 17
        self.RF_LOAD = 0  # 18
        self.MEM_LOAD = 0  # 19
        self.IMM_GEN_CTR_2 = 0  # 20

        self.REG_RTB_G = 0
        self.IMM_RTB_G = 0
        self.PC_RTB_G = 0  #

        self.CPU_BUSY = 0

        self.Branch = 0  # Output from ALU

        self.SH_RTB_EN = 1  # From Shifter
        """
        """
        self.pulse_count = 0  #
        # self.cycle_count = 0
        self.actual_clock = 0  # 0 = sestupná hrana, 1 = nástupná hrana
        self.running = True  # Podmínka běhu programu - aby zbytečně necyklil na místě
        self.uCounter = 0
        self.uCounter_debug = 0

        """
        Buses
        """
        self.instruction = 0b00000000000000000000000000000000
        self.immediate_value = 0b00000000000000000000000000000000
        self.write_back = 0b00000000000000000000000000000000  # 32 bit
        # Immediate generator -> program counter
        # self.IMM_to_PC =    0b00000000000000000000000000000000     # 32 bit 
        # Program counter to Instruction memory
        self.PC_to_IM = 0b00000000000000000000000000000000  # 32 bit

        # Register File
        self.read_register_1 = 0b00000000000000000000000000000000
        self.read_register_2 = 0b00000000000000000000000000000000
        self.mux_out = 0b00000000000000000000000000000000

        # ALU out
        self.alu_out = 0b00000000000000000000000000000000

        # RAM out
        self.ram_out = 0b00000000000000000000000000000000

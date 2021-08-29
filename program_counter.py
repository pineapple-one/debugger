from block import Block
from data import Data


class ProgramCounter(Block):
    """
    Počítá adresy právě vykonáváné instrukce.

    Celkově má Program Counter 3 módy:
        1) Přičítá k aktuální adrese konstantu 4
        2) Přičítá k aktuální adrese konstantu z IMM gen. (vstup Y)
        3) Skočí absolutně na adresu přivedenou na vstup OUT_in

    Inputs:
    - CLK
    - PC_Source_1 (SRC1) - Když je 1, skáče se na adresu na vstupu OUT_in
    - Take_branch (T_BRCH) - Generován Control Unitem, říká, že tahle instrukce je skoková
    - PC_Source (SRC0) - Když je 0 - PC bude přičítat 4, když 0 - přičte konstantu z IMM gen
    - Program_counter_enable (PCE) - aktivuje PC, provede přičtení
    - Branch - Signál z ALU - potvrzení, že může skočit. Skočí, pouze pokud je 1
               zároveň s Take_branch
    - RST - reset PC
    - Y - vstup z IMM gen. pro relativní přičtení
    - OUT_in - bypass sčítačky unvnitř PC - absolutní skok na adresu

    Outputs:
    - X - Výstup do Instruction Memory
    - OUT - výstup na writeback - pro zápis adresy do registrů
          - OG2
            stav 1 - Povolen vstup z WB do PC na OUT_in
            stav 0 - Zápis na WB z výstupu OUT pro zápis do registrů
    """

    def __init__(self, data: Data) -> None:
        """
        Init of Program counter

        :return: None
        """

        super().__init__(data)
        self.actual_index = 0  # value X from Logisim = output to IM
        self.mode = 0

        assembly_guidance_file = open("programs/APP.lss")
        self.assembly_guidance = assembly_guidance_file.readlines()
        assembly_guidance_file.close()

    def clock_up(self):
        # Výpočet ve sčítačce se provádí s každým clockem!

        self.get_pc_mode()

        # [self.mode_1, self.mode_2, self.mode_3][self.mode+1]()

        if self.data.PCE or (self.data.Branch and self.data.TAKE_BRANCH) or not self.data.PC_RTB_G:
            if self.mode == 1:
                self.mode_1()

            elif self.mode == 2:
                self.mode_2()

            elif self.mode == 3:
                self.mode_3()

            # if not self.data.PC_RTB_G:
            # logger.info(f"PC_RTB_G enabled for writing to WB - value: {self.data.write_back}")
            # self.data.write_back = self.actual_index # Zápiše vypočtenou adresu na Writeback

            self.data.PC_to_IM = self.actual_index
            # PC_should_be = self.debug_data.get_value("PC", self.data.pulse_count)
            #
            # # self.assembly_guidance.fin
            # string_to_find = f"  {hex(self.actual_index)[2:]}:\t"

            # for line in self.assembly_guidance:
            #     if string_to_find in line:
            #         # logger.info(f"new addr loaded: {hex(self.actual_index)}, m = {self.mode}, ins: \'{line.replace(string_to_find, '')[18:]}\', (should be: {PC_should_be})")
            #
            # if PC_should_be != self.actual_index:
            #     # logger.error("PC error!!")

    def mode_1(self) -> None:
        if self.data.PC_RTB_G:
            self.actual_index += 4
        else:
            self.data.write_back = self.actual_index + 4

    def mode_2(self) -> None:

        value_y = self.data.immediate_value

        # if self.data.pulse_count == 265:
        #     # logger.info(f"200: Mode: {hex(self.actual_index)=}, {hex(value_y)=} > {self.actual_index + value_y}")

        if self.data.PC_RTB_G:
            self.actual_index = (self.actual_index + value_y) & 0xffffffff
        else:
            self.data.write_back = (self.actual_index + value_y) & 0xffffffff

    def mode_3(self) -> None:
        if self.data.PC_RTB_G:
            self.actual_index = self.data.write_back

    def get_pc_mode(self):
        """
        Returns mode of Program Counter
        """
        # print(self.data.PC_SRC_0, self.data.TAKE_BRANCH, self.data.PC_SRC_1, self.data.Branch, self.data.TAKE_BRANCH)

        if self.data.PC_SRC_1:
            self.mode = 3

        elif (self.data.PC_SRC_0 and not self.data.TAKE_BRANCH) or (self.data.Branch and self.data.TAKE_BRANCH):
            # print(self.data.PC_SRC_0, self.data.TAKE_BRANCH)
            # logger.info(f"Take branch: {self.data.TAKE_BRANCH}")
            self.mode = 2

        # (not self.data.PC_SRC_0 or self.data.TAKE_BRANCH or (not self.data.Branch or not self.data.TAKE_BRANCH)):
        else:
            self.mode = 1

# if __name__ == "__main__":
#     import time
#     data = Data()
#     data.PCE = 1
#     data.PC_SRC_1 = 1
#     data.immediate_value = 50
#     data.write_back = 12401
#     program_counter = ProgramCounter(data)
#     # data.PC_SRC_1 = 0
#     while True:
#         program_counter.at_clock()
#         print(data.PC_to_IM)
#         time.sleep(1)

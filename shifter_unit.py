from block import Block
from data import Data


class ShifterUnit(Block):
    """
    Inputs:
        - SH_LATCH  - příprava na použití shifteru
                    - otevře vnitřní registr pro data z RB0
                    - S nástupnou hranou uloží

        - SH_LOAD   - Povolí posouvání
        - RF_STORE  - neimplementujeme
        - PCE - pro reset když se posouvá PC
        - Data_in   - vstupní data z RB0
        - Instrukce - z ní vytežení funct3 pro nastavení chování shifteru
        - I         - Aritmetický / logický posuv
        - RS2       - Prvních 5 bitů z multiplexoru - určuje o kolik se data posunou
        - RST
    Outputs:
        - SH_BUSY = CPU_BUSY
                    - pozastavení microcounteru při shiftování

        - OUT       - datový výstup
        - SH_RTB_EN - Blokování dekodéru v Control unit 


    POZOR: Hazardní stav při posuvu nulou !!!
    """

    def __init__(self, data: Data) -> None:
        super().__init__(data)
        self.latched_value = 0

        # Definování konstant
        self.SH_LEFT = 0
        self.SH_RIGHT = 1
        self.SH_BUSY = 2
        self.OUT_EN = 3
        self.SH_STR_EN = 4

        self.f3 = 0b000
        self.rs2 = 0b000000
        self.ctr = 0b000000
        self.sh_load = 0b0
        self.i = 0

        self.internal_register = 0
        self.input_data = 0

    def clock_up(self):
        if self.data.SH_LOAD or self.data.SH_LATCH:
            self.get_init_data()
            address_to_eeprom = self.f3 | (self.rs2 << 3) | (self.ctr << 8) | (self.data.SH_LOAD << 14)
            what_to_do = self.generate(bin(address_to_eeprom)[2:].zfill(17))

            if self.data.SH_LATCH == 1:
                # logger.info(f"SH latch, {self.internal_register=}")
                self.internal_register = self.input_data

            if (what_to_do >> self.SH_LEFT) & 1 == 1:
                if (what_to_do >> self.SH_STR_EN) & 1 == 1:
                    self.internal_register = (self.internal_register << 1) & 0xffffffff
                    # logger.info(f"shift to left by one > ({bin(self.internal_register)})")

            elif (what_to_do >> self.SH_RIGHT) & 1 == 1:
                if (what_to_do >> self.SH_STR_EN) & 1 == 1:
                    if self.i == 0:
                        self.internal_register = (self.internal_register >> 1) & 0xffffffff
                        # logger.info(f"shift to right by one > ({bin(self.internal_register)})")

                    elif self.i == 1:
                        if self.internal_register & 2 ** 31 != 0:
                            # logger.info("MSB detected")
                            self.internal_register = ((self.internal_register >> 1) | (1 << 31)) & 0xffffffff
                        else:
                            self.internal_register = (self.internal_register >> 1) & 0xffffffff

                        # logger.info(f"shift to right by one > ({bin(self.internal_register)})")

            if (what_to_do >> self.SH_BUSY) & 1 == 1:
                # logger.info("CPU BUSY")
                self.data.CPU_BUSY = 1

            if (what_to_do >> self.OUT_EN) & 1 == 1:
                # logger.info(f"HOTOVO: výsledná hodnota je: {self.internal_register}")
                self.data.SH_RTB_EN = 0
                self.data.CPU_BUSY = 0
                self.data.write_back = self.internal_register
                self.data.REG_RTB_G = 1
                self.data.IMM_RTB_G = 1
                self.data.PC_RTB_G = 1

    def clock_down(self):
        if self.data.SH_LOAD or self.data.SH_LATCH:
            self.get_init_data()
            address_to_eeprom = self.f3 | (self.rs2 << 3) | (self.ctr << 8) | (self.data.SH_LOAD << 14)
            what_to_do = self.generate(str(bin(address_to_eeprom)[2:]).zfill(17))

            # if self.data.pulse_count == 142:
            # logger.info(f"{what_to_do=}, {self.ctr=}, {self.f3=}, {self.rs2=}")

            if self.data.SH_LOAD and self.ctr == 0:
                self.ctr = 1
                # logger.info(f"Initial SH load, counter +1 {self.ctr=}")

            elif (what_to_do >> self.SH_BUSY) & 1 == 1 and self.data.SH_LOAD == 1 and (
                    what_to_do >> self.OUT_EN) & 1 == 0:
                self.ctr += 1
                # logger.info(f"internal counter = {self.ctr=}")

        if self.data.PCE == 1:
            # logger.info("resseting shifter")
            self.data.SH_RTB_EN = 1
            self.ctr = 0

    def get_init_data(self):
        prepared_instruction = bin(self.data.instruction)[2:].zfill(32)
        self.f3 = int(prepared_instruction[17:20], 2)
        self.i = int(prepared_instruction[1], 2)
        self.rs2 = int(self.data.mux_out) & 0b11111
        self.input_data = int(self.data.read_register_1)

    def generate(self, input):
        _L = int(input[2], 2)
        _CTR = int(input[3:9], 2)
        _RS2 = int(input[9:14], 2)
        _F3 = int(input[14:17], 2)

        out = 0

        # VERZE 6.1
        if _L == 1:
            if _F3 == 1:  # SLL
                if _RS2 == 0:  # posun o nulu
                    out |= 1 << self.OUT_EN
                # elif _RS2 == 1  and _CTR == 2:   # posun o jednicku -> problematický 0. krok
                #     out |= 1 << SH_LEFT | 1 << SH_BUSY | 1 << SH_STR_EN
                # elif _RS2 == 1  and _CTR == 3:   # posun o jednicku -> problematický 1. krok
                #     out |= 1 << OUT_EN
                elif _RS2 == (_CTR - 2):
                    out |= 1 << self.OUT_EN
                else:
                    if _CTR > 1:
                        out |= 1 << self.SH_STR_EN
                    out |= 1 << self.SH_LEFT | 1 << self.SH_BUSY

            if _F3 == 5:  # SR (A or L)
                if _RS2 == 0:  # posun o nulu
                    out |= 1 << self.OUT_EN
                elif _RS2 == (_CTR - 2):
                    out |= 1 << self.OUT_EN
                else:
                    if _CTR > 1:
                        out |= 1 << self.SH_STR_EN
                    out |= 1 << self.SH_RIGHT | 1 << self.SH_BUSY

        return out

# if __name__ == "__main__":
#     #           0 000000 00000 000
#     #           L  CTR   RS2   F3
#     # adress =  0b1_000001_00001_101
#
#     input_data = 0b00000000000000000000000000000001
#
#     f3 = 0b001
#     rs2 = 0b000011
#     ctr = 0b000000
#     sh_load = 0b0
#     i = 0
#
#     address_to_eeprom = f3 | (rs2 << 3) | (ctr << 8) | (sh_load << 14)
#
#     clk = 0
#     internal_register = 0
#     out_en = 0
#
#     # logger.info(generate(str(bin(address_to_eeprom)[2:]).zfill(17))[2:])
#
#     clk = 0
#     # logger.info(f"clock is: 0 (down) - sh_latch aktivní")
#     # sh_latch = 1
#
#     clk = 1
#     # logger.info(f"clock is: 1 (up) - zápis do vnitřního registru")
#     internal_register = input_data
#
#     clk = 0
#     # logger.info(f"clock is: 0 (down) - vypnutí sh_latch a zapnutí sh_load")
#     sh_load = 1
#     ctr += 1
#     address_to_eeprom = f3 | (rs2 << 3) | (ctr << 8) | (sh_load << 14)
#     what_to_do = generate(str(bin(address_to_eeprom)[2:]).zfill(17))
#     # logger.info(f"What to do = {hex(what_to_do)}")
#
#
#     for loop in range(40):
#         clk = 1
#         # logger.info(f"clock is: 1 (up)")
#
#         if (what_to_do >> SH_LEFT) & 1 == 1:
#             if (what_to_do >> SH_STR_EN) & 1 == 1:
#                 internal_register = (internal_register << 1) & 0xffffffff
#                 # logger.info(f"shift to left by one > ({bin(internal_register)})")
#
#         if (what_to_do >> SH_RIGHT) & 1 == 1:
#             if (what_to_do >> SH_STR_EN) & 1 == 1:
#                 if i == 0:
#                     internal_register = (internal_register >> 1) & 0xffffffff
#                     # logger.info(f"shift to right by one > ({bin(internal_register)})")
#
#                 elif i == 1:
#                     if internal_register & 2**31 != 0:
#                         # logger.info("MSB detected")
#                         internal_register = ((internal_register >> 1) | (1 << 31))  & 0xffffffff
#                     else:
#                         internal_register = (internal_register >> 1) & 0xffffffff
#
#                     # logger.info(f"shift to right by one > ({bin(internal_register)})")
#
#
#         if (what_to_do >> SH_BUSY) & 1 == 1:
#             # logger.info("CPU BUSY")
#
#         if (what_to_do >> OUT_EN) & 1 == 1:
#             # logger.info(f"HOTOVO: výsledná hodnota je: {internal_register}")
#
#         address_to_eeprom = f3 | (rs2 << 3) | (ctr << 8) | (sh_load << 14)
#         what_to_do = generate(str(bin(address_to_eeprom)[2:]).zfill(17))
#         # logger.info(f"What to do = {hex(what_to_do)}")
#
#         input()
#
# # -------------------------------------------------------
#
#
#         clk = 0
#         # logger.info(f"clock is: 0 (down)")
#
#
#         if (what_to_do >> SH_BUSY) & 1 == 1 and sh_load == 1 and out_en == 0:
#             ctr += 1
#             # logger.info(f"internal counter = {ctr}")
#
#
#         address_to_eeprom = f3 | (rs2 << 3) | (ctr << 8) | (sh_load << 14)
#         what_to_do = generate(str(bin(address_to_eeprom)[2:]).zfill(17))
#         # logger.info(f"What to do = {hex(what_to_do)}")
#
#         input()

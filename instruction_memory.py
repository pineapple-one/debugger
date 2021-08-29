from block import Block
from data import Data


class InstructionMemory(Block):
    """
    Inputs:
    - Addr - index adresy z Program Counteru

    Outputs:
    - Instrukce: - Přes splitter do dalších částí (RF)
                 - Celá instrukce (32 b) do IMM gen.
    """

    def __init__(self, file_name, data: Data):

        self.file_name = file_name

        self.content = None

        self.__load_machine_code()
        super().__init__(data)
        # self.()             # Při inicializaci je potřeba náskok jednoho taktu

    def init(self) -> None:
        self.data.instruction = self.content[0]

    def __load_machine_code(self) -> None:
        """
        Load machine code from file
        :return:
        """

        with open(self.file_name) as f:
            self.content = f.readlines()
            self.content = [int(i.strip(), 16) for i in self.content]

    # def state(self, location) -> None:
    #     self.data.instruction = self.content[location]

    def clock_up(self) -> None:
        addr = int(self.data.PC_to_IM / 4)

        try:
            self.data.instruction = self.content[addr]
            # logger.info(f"new instruction loaded: {hex(self.data.instruction)} (address = {hex(self.data.PC_to_IM)})")

        except IndexError:
            assert Exception(f"ERROR: addr: {hex(addr)}, ins: {hex(self.data.instruction)}")

        # Pokud se program zacyklil na konci:
        if self.data.instruction == 0x6f:
            self.data.running = False

        # if self.data.instruction == 0x00e7a023:
        #     input()

# if __name__ == "__main__":
#     instructionMemory = InstructionMemory("../APP.mhc", Data())

from data import Data


class InstructionMemory:
    """
    Inputs:
    - Address - index of address from Program Counter

    Outputs:
    - Instruction: - Via splitter to other parts (RF)
                   - Whole instruction (32 b) to IMM gen.
    """

    def __init__(self, file_name: str, data: Data):
        self.file_name = file_name
        self.data = data
        self.content = None

        self.__load_machine_code()

    def __load_machine_code(self) -> None:
        """
        Load machine code from file
        :return:
        """

        with open(self.file_name) as f:
            self.content = f.readlines()
            self.content = [int(i.strip(), 16) for i in self.content]

    def clock_up(self) -> None:
        """
        On clock up
        :return:
        """

        address = int(self.data.PC_to_IM / 4)

        try:
            self.data.instruction = self.content[address]

        except IndexError:
            raise Exception(f"ERROR: address: {hex(address)}, ins: {hex(self.data.instruction)}")

        # If the program loops at the end of the program
        if self.data.instruction == 0x6f:
            self.data.running = False

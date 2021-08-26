from block import Block
from PIL import Image
from data import Data
import numpy as np
import base64
import numpy
import io


class DataMemory(Block):
    def __init__(self, data: Data, socketio) -> None:

        self.__socketio = socketio
        super().__init__(data)

        self.RAM = numpy.zeros(2 ** 19, dtype=numpy.uint8)
        self.VRAM = numpy.zeros(2 ** 13, dtype=numpy.uint8)
        self.last_time = 0

    def clock_up(self):
        self.load()
        self.store()

    def clock_down(self):
        self.load()

    def asynchronous(self):
        # TODO VRAM -> property + setter
        # current = time.time()

        # if current - self.last_time > 0.1:
        #     self.last_time = current

        binary = []
        for x in self.VRAM:
            bit_array = bin(x).lstrip("0b").zfill(8)[::-1]

            for i in bit_array:
                binary.append(int(i) * 255)

        reshaped = np.reshape(binary, (256, 256))
        cropped = np.array(reshaped[0:150, 0:200])

        im = Image.fromarray(cropped.astype("uint8"))
        raw_bytes = io.BytesIO()
        im.save(raw_bytes, "BMP")
        raw_bytes.seek(0)  # return to the start of the file
        self.__socketio.emit("vga",
                             {"image": f"data:image/bmp;base64,{base64.b64encode(raw_bytes.read()).decode('utf-8')}"},
                             namespace="/pineapple")

    def update_vga(self):
        self.asynchronous()
        # p = Process(target=self.asynchronous)
        # p.start()

    def store(self):
        input_data = self.data.read_register_2
        input_address = self.data.alu_out

        prepared_instruction = bin(self.data.instruction)[2:].zfill(32)
        funct3 = int(prepared_instruction[17:20], 2)

        if self.data.MEM_STORE:
            bin_address = bin(input_address)[2:].zfill(32)

            # ukládání po bytech (b)
            if funct3 == 0b000:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # print(f"Write B to SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    self.VRAM[addr] = input_data & 0xff
                    self.update_vga()
                    print(f"Write B to VRAM ({addr}) --> {input_data}, {hex(input_address)}, {input_data}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    self.RAM[addr] = input_data & 0xff

            # ukládání po půlslovech (hw)
            elif funct3 == 0b001:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % (16)
                    print(f"Write HW to SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    self.VRAM[addr + 0] = (input_data & 0x00ff) >> 0
                    self.VRAM[addr + 1] = (input_data & 0xff00) >> 8
                    self.update_vga()
                    print(f"Write HW to VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    self.RAM[addr + 0] = (input_data & 0x00ff) >> 0
                    self.RAM[addr + 1] = (input_data & 0xff00) >> 8

            # ukládání po slovech (w)
            elif funct3 == 0b010:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % (16)
                    print(f"Write W to SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    self.VRAM[addr + 0] = (input_data & 0x000000ff) >> 0
                    self.VRAM[addr + 1] = (input_data & 0x0000ff00) >> 8
                    self.VRAM[addr + 2] = (input_data & 0x00ff0000) >> 16
                    self.VRAM[addr + 3] = (input_data & 0xff000000) >> 24
                    self.update_vga()
                    # print(f"Write W to VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    self.RAM[addr + 0] = (input_data & 0x000000ff) >> 0
                    self.RAM[addr + 1] = (input_data & 0x0000ff00) >> 8
                    self.RAM[addr + 2] = (input_data & 0x00ff0000) >> 16
                    self.RAM[addr + 3] = (input_data & 0xff000000) >> 24

    def load(self):
        if self.data.MEM_LOAD:

            input_data = self.data.read_register_2
            input_address = self.data.alu_out

            prepared_instruction = bin(self.data.instruction)[2:].zfill(32)
            funct3 = int(prepared_instruction[17:20], 2)
            bin_address = bin(input_address)[2:].zfill(32)
            prepared_data = 0b00000000000000000000000000000000

            # load byte (lb)
            if funct3 == 0b000:

                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # addr = input_address - 0x80000000
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    prepared_data = 0
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    print(f"Read B from SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    # addr = input_address - 0x40000000
                    sign_bit = (self.VRAM[addr] & 0x80) >> 7
                    prepared_data = int(str(sign_bit) * 24, 2) << 8 | self.VRAM[addr]

                    print(f"Read B from VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    # addr = input_address
                    sign_bit = (self.RAM[addr] & 0x80) >> 7
                    prepared_data = int(str(sign_bit) * 24, 2) << 8 | self.RAM[addr]

            # load half (lh)
            elif funct3 == 0b001:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # addr = input_address - 0x80000000
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    prepared_data = 0
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    print(f"Read HW from SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    # addr = input_address - 0x40000000
                    sign_bit = (self.VRAM[addr] & 0x80) >> 7
                    prepared_data |= self.VRAM[addr + 0]
                    prepared_data |= self.VRAM[addr + 1] << 8
                    prepared_data |= int(str(sign_bit) * 16, 2) << 16
                    print(f"Read HW from VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    # addr = input_address % 524288  # 2 ** 19
                    addr = input_address

                    sign_bit = (self.RAM[addr] & 0x80) >> 7
                    prepared_data |= self.RAM[addr + 0]
                    prepared_data |= self.RAM[addr + 1] << 8
                    prepared_data |= int(str(sign_bit) * 16, 2) << 16

            # load word (lw)
            elif funct3 == 0b010:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # addr = input_address - 0x80000000
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    prepared_data = 0
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    print(f"Read W from SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    # addr = input_address - 0x40000000
                    prepared_data |= self.VRAM[addr + 0] << 0
                    prepared_data |= self.VRAM[addr + 1] << 8
                    prepared_data |= self.VRAM[addr + 2] << 16
                    prepared_data |= self.VRAM[addr + 3] << 24
                    # print(f"Read W from VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    # addr = input_address
                    prepared_data |= self.RAM[addr + 0] << 0
                    prepared_data |= self.RAM[addr + 1] << 8
                    prepared_data |= self.RAM[addr + 2] << 16
                    prepared_data |= self.RAM[addr + 3] << 24

                    # load byte unsigned (lbu)
            elif funct3 == 0b100:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # addr = input_address - 0x80000000
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    prepared_data = 0
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    # print(f"Read lbu from SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    # addr = input_address - 0x40000000
                    prepared_data = self.VRAM[addr]
                    # print(f"Read lbu from VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    prepared_data = self.RAM[input_address]

            # load half unsigned (lhu)
            elif funct3 == 0b101:
                # special registers
                if bin_address[0] == "1":
                    addr = input_address % 16
                    # addr = input_address - 0x80000000
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    prepared_data = 0
                    #  !!!!!!!!!!!! Load 0 every time !!!!!!!!!!!!!!!!
                    print(f"Read lbu from SP ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # VRAM
                elif bin_address[1] == "1":
                    addr = input_address % 8192  # 2 ** 13
                    # addr = input_address - 0x40000000
                    prepared_data = self.VRAM[addr]
                    prepared_data |= self.VRAM[addr + 1] << 8
                    print(f"Read lbu from VRAM ({addr}) --> {input_data}, pulse count: {self.data.pulse_count}")
                # SRAM
                else:
                    addr = input_address % 524288  # 2 ** 19
                    # addr = input_address
                    prepared_data = self.RAM[addr]
                    prepared_data |= self.RAM[addr + 1] << 8

            # print(f"Load: {bin(prepared_data)}")
            self.data.ram_out = prepared_data


# if __name__ == '__main__':
#     data = Data()
#     ram = DataMemory(data, logger)
#
#     f3 = 0b001
#     data.instruction = (f3 << 12)
#
#     data.MEM_STORE = 1
#     data.MEM_LOAD = 0
#
#     # address:
#     data.alu_out = 0xffffffff & 4
#     # data:
#     data.read_register_2 = 0xffffffff & 0b00000011_10000010
#
#     ram.clock_up()
#     print(f"Storing: ram[{data.alu_out}]= {ram.RAM[4]}")
#
#     f3 = 0b100
#     data.instruction = (f3 << 12)
#
#     data.MEM_STORE = 0
#     data.MEM_LOAD = 1
#
#     ram.clock_down()
#     # print(f"Loading: ram[{data.alu_out}]= {ram.RAM[4]}; word = {ram.RAM[data.alu_out]},{ram.RAM[data.alu_out+1]},{ram.RAM[data.alu_out+2]},{ram.RAM[data.alu_out+3]}")

import time

from immediate_generator import *
from instruction_memory import *
from program_counter import *
from register_file import *
from shifter_unit import *
from control_unit import *
from data_memory import *
from register import *
from alu import *

from threading import Thread

from device import Device


# FREQUENCY = 500  # Hz

class Pineapple(Thread):
    def __init__(self, socketio):
        self.__socketio = socketio
        self.debug = None
        self.target_count = 0

        super().__init__()

        self.data = None
        self.program_counter = None
        self.instruction_memory = None
        self.control_unit = None
        self.immediate_generator = None
        self.register_file = None
        self.shifter_unit = None
        self.alu = None
        self.data_memory = None
        self.register = None

        self.arduino = Device(self.__socketio)

        self.init()

    def init(self):
        self.data = Data()
        self.program_counter = ProgramCounter(self.data)
        self.instruction_memory = InstructionMemory("programs/APP.mhc", self.data)
        self.control_unit = ControlUnit(self.data)
        self.immediate_generator = ImmediateGenerator(self.data)
        self.register_file = RegisterFile(self.data)
        self.shifter_unit = ShifterUnit(self.data)
        self.alu = ALU(self.data)
        self.data_memory = DataMemory(self.data, socketio=self.__socketio)
        self.register = Register(self.data)

    def check(self):
        if self.debug:
            temp_wb = 0
            temp_rb0 = 0
            temp_addr = 0

            for n, i in enumerate(self.arduino.get_data()):
                data = i[1]

                if n == 0:
                    temp_wb = int(bin(data)[2:].zfill(32)[::-1],2)

                if n == 1:
                    temp_rb0 = data

                if n == 2:
                    temp_addr = data
                    

            self.__socketio.emit("bus_data", {
                "source": "cpu",
                "type": "wb",
                "hex": hex(temp_wb)[2:].zfill(8)
            }, namespace="/pineapple")

            self.__socketio.emit("bus_data", {
                "source": "cpu",
                "type": "addr",
                "hex": hex(temp_addr)[2:].zfill(8)
            }, namespace="/pineapple")

            self.__socketio.emit("bus_data", {
                "source": "cpu",
                "type": "rb0",
                "hex": hex(temp_rb0)[2:].zfill(8)
            }, namespace="/pineapple")

            if temp_addr != self.data.PC_to_IM:
                if not ((self.data.PC_to_IM - 4) == data and self.data.uCounter-1 == 0):
                    self.found_error()
            
            if temp_rb0 != self.data.read_register_1:
                if not ((self.data.PC_to_IM - 4) == data and self.data.uCounter-1 == 0):
                    self.found_error()

            if temp_rb0 != self.data.read_register_1:
                if not self.data.uCounter == 0:
                    self.found_error()
                


    def found_error(self):
        self.__socketio.emit("running", False, namespace="/pineapple")
        self.__socketio.emit("error", True, namespace="/pineapple")
        self.target_count = self.data.pulse_count
        self.send_data_to_web()

        while self.data.pulse_count == self.target_count:
            time.sleep(0.1)
            
        self.__socketio.emit("error", False, namespace="/pineapple")
        self.__socketio.emit("running", True, namespace="/pineapple")


    def make_debug(self):
        """
        Send debug information
        :return:
        """
        # # print("posílám,", self.data.uCounter)
        # self.__socketio.emit("u_counter", self.data.uCounter, namespace="/pineapple")
        # self.__socketio.emit("clock", self.data.actual_clock, namespace="/pineapple")
        # self.__socketio.emit("branch", self.data.TAKE_BRANCH, namespace="/pineapple")

        # # print("--"*10)
        # # print("uC",self.data.uCounter, "clock", self.data.actual_clock, "pulse", self.data.pulse_count, "PCE", self.data.PCE)

        # opcode = self.data.instruction & 0b00000000000000000000000001111111

        # # logger.info(self.DICTIONARY[opcode][self.data.uCounter])

        # self.__socketio.emit("micro_codes", {
        #     "instruction": hex(opcode),
        #     "micro_codes": self.control_unit.DICTIONARY[opcode],
        #     "u_counter": self.data.uCounter
        # }, namespace="/pineapple")

        # self.__socketio.emit("source_highlight", [hex(self.data.PC_to_IM)[2:]],
        #                      namespace="/pineapple")

        if self.data.pulse_count % 128 == 0:
            self.__socketio.emit("pulse_counter", self.data.pulse_count, namespace="/pineapple")

        if self.data.pulse_count == self.target_count:
            self.__socketio.emit("running", False, namespace="/pineapple")

            run_once = False
            while self.data.pulse_count == self.target_count:
                if run_once is False:
                    run_once = True
                    self.send_data_to_web()
                time.sleep(0.1)
                
            self.__socketio.emit("running", True, namespace="/pineapple")

        # self.__socketio.emit("cpu_busy", self.data.CPU_BUSY, namespace="/pineapple")
        

    def send_data_to_web(self):
        # print("posílám,", self.data.uCounter)
        self.__socketio.emit("u_counter", self.data.uCounter, namespace="/pineapple")
        self.__socketio.emit("clock", self.data.actual_clock, namespace="/pineapple")
        self.__socketio.emit("branch", self.data.TAKE_BRANCH, namespace="/pineapple")
        self.__socketio.emit("pulse_counter", self.data.pulse_count, namespace="/pineapple")

        # print("--"*10)
        # print("uC",self.data.uCounter, "clock", self.data.actual_clock, "pulse", self.data.pulse_count, "PCE", self.data.PCE)
        for i, reg in enumerate(self.register_file.registers):
            self.__socketio.emit("register_file", {
                "index": i,
                "hex": "0x" + hex(int(reg))[2:].zfill(8),
                "bin": "0b" + bin(int(reg))[2:].zfill(32)
            }, namespace="/pineapple")

        # write_register = self.data.instruction & 0b00000000000000000000111110000000  # 11-7
        # write_to_register = write_register >> 7

        # if self.data.RF_STORE and write_to_register != 0:
        #     print("sendiiiing")

        for idx in range(8):
            source = "sim"
            src_type = ""
            data_hex = ""
            
            if idx == 0:
                src_type = "addr"
                data_hex = "0x" + hex(self.data.PC_to_IM)[2:].zfill(8)
            elif idx == 1:
                src_type = "ins"
                data_hex = "0x" + hex(self.data.instruction)[2:].zfill(8)
            elif idx == 2:
                src_type = "imm"
                data_hex = "0x" + hex(self.data.immediate_value)[2:].zfill(8)
            elif idx == 3:
                src_type = "rb0"
                data_hex = "0x" + hex(self.data.read_register_1)[2:].zfill(8)
            elif idx == 4:
                src_type = "rb1"
                data_hex = "0x" + hex(self.data.read_register_2)[2:].zfill(8)
            elif idx == 5:
                src_type = "alu"
                data_hex = "0x" + hex(self.data.alu_out)[2:].zfill(8)
            elif idx == 6:
                src_type = "ram"
                data_hex = "0x" + hex(self.data.ram_out)[2:].zfill(8)
            elif idx == 7:
                src_type = "wb"
                data_hex = "0x" + hex(self.data.write_back)[2:].zfill(8)

            self.__socketio.emit("bus_data", {
                "source": source,
                "type": src_type,
                "hex": data_hex
            }, namespace="/pineapple")
            

        opcode = self.data.instruction & 0b00000000000000000000000001111111

        # logger.info(self.DICTIONARY[opcode][self.data.uCounter])

        self.__socketio.emit("micro_codes", {
            "instruction": hex(opcode),
            "micro_codes": self.control_unit.DICTIONARY[opcode],
            "u_counter": self.data.uCounter
        }, namespace="/pineapple")

        self.__socketio.emit("source_highlight", [hex(self.data.PC_to_IM)[2:]],
                             namespace="/pineapple")

        self.__socketio.emit("cpu_busy", self.data.CPU_BUSY, namespace="/pineapple")

    def send_code(self):
        """
        Send code
        :return:
        """

        with open("programs/APP.lss") as f:
            code = "".join(f.readlines()).split("Disassembly of section .text:")[1].strip().replace("<", "(").replace(">", ")").replace(" ", "&nbsp;").replace("\n", "<br>").replace("\t", "&nbsp;"*4)
            self.__socketio.emit("source_load", {"code": code}, namespace="/pineapple")

    def run(self):
        self.__socketio.emit("running", True, namespace="/pineapple")
        self.send_code()
        d = [self.program_counter, self.instruction_memory, self.control_unit, self.immediate_generator,
             self.program_counter, self.register_file, self.shifter_unit, self.alu, self.data_memory, self.register]

        if self.debug:
            self.arduino.reset()

        while self.data.running:
            # self.data.cycle_count += 1

            if self.debug:
                self.make_debug()
                self.check()

            # logger.info(self.data.pulse_count)

            # logger.info("\r\n"*2 + "-"*30 + f" {self.data.pulse_count} up " + "-"*30)

            # Náběžná hrana
            self.data.pulse_count += 1
            self.data.actual_clock = 1

            if self.debug:
                self.arduino.clock_up()

            # print("Sending clock up")
            for i in d:
                i.clock_up()

            # self.make_debug()

            # # TODO: Dát do funcke
            # if self.data.pulse_count == self.target_count:
            #     self.__socketio.emit("running", False, namespace="/pineapple")
            #     while self.data.pulse_count == self.target_count:
            #         time.sleep(0.1)
            #     self.__socketio.emit("running", True, namespace="/pineapple")

            # WB_should_be = debug_data.get_value("WB", self.data.pulse_count)
            # logger.info(f"writeback = {hex(self.data.write_back)} (should be: 0x{hex(WB_should_be)[2:].zfill(8)})")

            # if WB_should_be != self.data.write_back:
                # logger.error("WB error!!")

            # time.sleep(1 / (FREQUENCY * 2))

            if self.debug:
                self.make_debug()
                self.check()
            
            # Sestupná hrana
            self.data.pulse_count += 1
            self.data.actual_clock = 0

            # print("Sending clock down")
            if self.debug:
                self.arduino.clock_down()

            # logger.info("\r\n"*2 + "-"*30 + f" {self.data.pulse_count} down " + "-"*30)
            for i in d:
                i.clock_down()

            # self.make_debug()

            # # TODO: Dát do funcke
            # if self.data.pulse_count == self.target_count:
            #     self.__socketio.emit("running", False, namespace="/pineapple")
            #     while self.data.pulse_count == self.target_count:
            #         time.sleep(0.1)
            #     self.__socketio.emit("running", True, namespace="/pineapple")

            # WB_should_be = debug_data.get_value("WB", self.data.pulse_count)
            # logger.info(f"writeback = {hex(self.data.write_back)} (should be: 0x{hex(WB_should_be)[2:].zfill(8)})")

            # if WB_should_be != self.data.write_back:
            #     # logger.error("WB error!!")

            # time.sleep(1 / (FREQUENCY * 2))
            # if self.data.pulse_count % 10_000 == 0:
            #     p1 = (time.time() - o)
            #
            #     print(f"{1/p1:.2f}")

            # print(hex(self.data.PC_to_IM))

        self.__socketio.emit("running", False, namespace="/pineapple")

        self.send_data_to_web()

    def stop(self):
        self.data.running = False


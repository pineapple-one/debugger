from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["alu.pyx", "shifter_unit2.pyx", "block.pyx", "control_unit.pyx", "data.pyx", "data_memory.pyx", "immediate_generator.pyx", "instruction_memory.pyx", "pineapple.pyx", "program_counter.pyx", "register.pyx", "register_file.pyx"])
)

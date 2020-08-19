"""CPU functionality."""

import sys
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

try:
    map_file = dirpath + sys.arg[1]
catch:
    print("ERROR - arg expected")

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.sp = 0XF4
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.op_size = 1

    def ram_read(self, addr_to_read): # addr_to_read is an index that points to a space in RAM
        return self.ram[addr_to_read]

    def ram_write(self, MAR, MDR): #MAR is an address in RAM, whereas MDR is a value to write
        self.ram[MAR] = MDR

    def load(self, map_file):

        address = 0
        
        if len(map_file) < 2:
            print("ERROR ==> provide file arg in CLI")

        instruction_set = open(map_file, 'r')
        my_list = []
        for instruction in instruction_set:
            if (instruction[0]) == '#':
                continue
            if (instruction[0]) == '\n':
                continue
            else:
                my_var = int(instruction.splitlines()[0].split()[0], 2)
                my_list.append(my_var)

        for instruction in my_list:
            self.ram[address] = instruction
            address += 1
        
    def alu(self, op, reg_a, reg_b):

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        is_running = True
        while is_running:
            IR = self.ram_read(self.pc)
            if IR == self.PUSH:
                # decrement stack pointer
                self.sp -= 1
                # save value from register that has already been written too
                value = self.reg[self.ram_read(self.pc + 1)] 
                # save value to stack
                self.ram[self.sp] = value
                # save op size
                self.op_size = 2
            elif IR == self.POP:
                # pop stack value and save to register
                self.reg[self.ram(self.pc + 1)] = self.ram[self.sp]
                self.sp += 1
                self.op_size = 2
            elif IR == self.LDI: 
                reg_index = self.ram_read(self.pc + 1)  
                value = self.ram_read(self.pc + 2)
                self.reg[reg_index] = value
                self.op_size = 3
            elif IR == self.PRN:
                reg_index = self.ram_read(self.pc + 1)
                print(self.reg[reg_index])
                self.op_size = 2
            elif IR == self.MUL:
                # print("it ran")
                self.alu("MUL", self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.op_size = 3
            elif IR == self.HLT:
                is_running = False
                self.op_size = 1
                
            self.pc += self.op_size

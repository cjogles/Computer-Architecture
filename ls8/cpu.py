"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # ram holds up to 256 different addresses since 8 bit cpu can only go that high
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0XF4] # register 7 == stack pointer per spec instructions
        self.pc = 0 # program counter
        self.op_size = 0 # operation size
        self.LDI = 0b10000010 # load value immedielty to given register
        self.PRN = 0b01000111 # print value at given register
        self.HLT = 0b00000001 # halt program
        self.MUL = 0b10100010 # multiply reg_a and reg_b
        self.PUSH = 0b01000101 # push value at given register onto stack
        self.POP = 0b01000110 # pop value at given register off of stack
        self.CALL = 0b01010000 # call subroutine
        self.RET = 0b00010001 # return from subroutine
        self.ADD = 0b10100000 # add reg_a and reg_b

    def ram_read(self, MAR): # addr_to_read is an index that points to a space in RAM
        return self.ram[MAR]

    def ram_write(self, MAR, MDR): #MAR is an address in RAM, whereas MDR is a value to write
        self.ram[MAR] = MDR

    def load(self):

        address = 0
        
        if len(sys.argv[1]) < 2:
            print("ERROR ==> provide file arg in CLI")

        instruction_set = open(sys.argv[1], 'r')
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
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
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
                self.registers[7] -= 1
                MAR = self.registers[7]
                reg_index = self.ram_read(self.pc + 1)
                MDR = self.registers[reg_index] 
                self.ram_write(MAR, MDR)
                self.op_size = 2
            elif IR == self.POP:
                reg_index = self.ram_read(self.pc + 1)
                value = self.ram[self.registers[7]]
                self.registers[reg_index] = value
                self.registers[7] += 1
                self.op_size = 2
            elif IR == self.LDI: 
                reg_index = self.ram_read(self.pc + 1)  
                value = self.ram_read(self.pc + 2)
                self.registers[reg_index] = value
                self.op_size = 3
            elif IR == self.PRN:
                reg_index = self.ram_read(self.pc + 1)
                print("PRINTED ==> ", self.registers[reg_index])
                self.op_size = 2
            elif IR == self.MUL:
                self.alu("MUL", self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.op_size = 3
            elif IR == self.ADD:
                self.alu("ADD", self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.op_size = 3
            elif IR == self.CALL:
                # Calls a subroutine (function) at the address stored in the register.
                # 1. The address of the ***instruction*** _directly after_ `CALL` is
                # pushed onto the stack. This allows us to return to where we left off 
                # when the subroutine finishes executing.
                # 2. The PC is set to the address stored in the given register. We jump to that 
                # location in RAM and execute the first instruction in the subroutine. The PC can 
                # move forward or backwards from its current location.
                MAR = self.pc + 2 # I have the address
                self.registers[7] -= 1 #decrement stack pointer
                self.ram[self.registers[7]] = MAR 
                some_var = self.registers[self.ram[self.pc + 1]]
                self.pc = some_var 
                self.op_size = 0 
            elif IR == self.RET:
                # Pop the value from the top of the stack and store it in the `PC`.
                # 00010001
                # 11
                self.pc = self.ram[self.registers[7]]
                self.registers[7] += 1
                self.op_size = 0
            elif IR == self.HLT:
                is_running = False
                self.op_size = 1
                
            self.pc += self.op_size 

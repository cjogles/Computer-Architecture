"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.op_size = 1

    def ram_read(self, addr_to_read): # addr_to_read is an index that points to a space in RAM
        return self.ram[addr_to_read]

    def ram_write(self, MAR, MDR): #MAR is an address in RAM, whereas MDR is a value to write
        # memory address register
        # memory data register
        # MAR contains address that is being read or written to
        # MDR contains data that was read or the data to write
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI - Write to register command
            0b00000000, # R0 - register 0
            0b00001000, # 8 - value 8
            0b01000111, # PRN - print command
            0b00000000, # R0 - register 0
            0b00000001, # HLT - halt command
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
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
        """Run the CPU."""
        # the whole point is to run the instructions that have been loaded in RAM
        is_running = True
        while is_running:
            cmd = self.ram_read(self.pc)
            if cmd == self.LDI: 
                reg_index = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)
                self.reg[reg_index] = value
                self.op_size = 3
            elif cmd == self.PRN:
                reg_index = self.ram_read(self.pc + 1)
                print(self.reg[reg_index])
                self.op_size = 2
            elif cmd == self.HLT:
                is_running = False
                self.op_size = 1
            self.pc += self.op_size


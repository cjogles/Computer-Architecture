"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 8 bit memory in ram, because I can only comprehend that much via 8 bit
        self.reg = [0] * 8  # 8 general-purpose 8-bit numeric registers R0-R7.
        self.MAR = [0] * 1  # holds the memory address we're reading or writing
        self.MDR = [0] * 1  # holds the value to write or the value just read
        self.PC = 0  # program counter keeps track of program address
        self.FL = [0] * 8 # flags I keep track of
        self.IR = [0] * 1 # instruction register I will be using in run()
        self.SP = self.reg[7] # * R7 is reserved as the stack pointer (SP)
        self.IM = self.reg[5] # * R5 is reserved as the interrupt mask (IM)
        self.IS = self.reg[6] # * R6 is reserved as the interrupt status (IS)
        self.reg[7] = 0xF4 # R7 is reserved as the stack pointer (SP), so set it here
        self.L = self.FL[5] # per spec
        self.G = self.FL[6] # per spec
        self.E = self.FL[7] # per spec

        global HLT, PRN, LDI, PUSH, POP, CALL, RET, JMP, JNE, JEQ, MUL, ADD, CMP, AND

        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        ADD = 0b10100000
        CMP = 0b10100111
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        JMP = 0b01010100
        JNE = 0b01010110
        JEQ = 0b01010101
        AND  = 0b10100000

    def load(self, program_filename):
        """Load a program into memory."""
        # Load program into memory
        address = 0
        with open(program_filename) as f:
            for line in f:
                line = line.split("#")
                line = line[0].strip()
                if line == '':
                    continue
                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            self.L, self.G, self.E = 0, 0, 0
            if (self.reg[reg_a] < self.reg[reg_b]):
                self.L = 1
            elif (self.reg[reg_a] > self.reg[reg_b]):
                self.G = 1
            else:
                self.E = 1
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # REMEMBER:
    # MAR holds the memory address we are reading or writing.
    # MDR holds the value to write or just read
    def ram_read(self):
        self.MDR = self.reg[self.MAR]

    def ram_write(self):
        self.reg[self.MAR] = self.MDR

    def run(self):
        running = True
        while running:

            self.IR = self.ram[self.PC]
            intruction_count = (self.IR >> 6) + 1

            if self.IR == LDI:
                self.MAR = self.ram[self.PC + 1]
                self.MDR = self.ram[self.PC + 2]
                self.ram_write()
                self.PC += intruction_count

            elif self.IR == PRN: 
                self.MAR = self.ram[self.PC + 1]
                self.ram_read()
                print("PRINTED ==> ", self.MDR)
                self.PC += intruction_count

            elif self.IR == MUL:
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                op = "MUL"
                self.alu(op, reg_a, reg_b)
                self.PC += intruction_count

            elif self.IR == ADD:
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                self.alu("ADD", reg_a, reg_b)
                self.PC += intruction_count

            elif self.IR == CMP:
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                op = "CMP"
                self.alu(op, reg_a, reg_b)
                self.PC += intruction_count

            elif self.IR == PUSH:
                self.SP -= 1
                self.MAR = self.ram[self.PC + 1]
                self.MDR = self.reg[self.MAR] 
                self.ram[self.SP] = self.MDR 
                self.PC += intruction_count

            elif self.IR == POP:
                self.MDR = self.ram[self.SP] 
                self.MAR = self.ram[self.PC + 1]
                self.reg[self.MAR] = self.MDR 
                self.SP += 1
                self.PC += intruction_count

            elif self.IR == CALL:
                self.MAR = self.PC + 2
                self.SP -= 1
                self.ram[self.SP] = self.MAR
                self.MAR = self.ram[self.PC + 1]
                self.PC = self.reg[self.MAR]

            elif self.IR == RET:
                self.MAR = self.ram[self.SP]
                self.SP += 1
                self.PC = self.MAR

            elif self.IR == JMP:
                self.MAR = self.ram[self.PC + 1]
                self.PC = self.reg[self.MAR]

            elif self.IR == JNE:
                if self.E == 0:
                    self.MAR = self.ram[self.PC + 1]
                    self.PC = self.reg[self.MAR]
                else:
                    self.PC += intruction_count

            elif self.IR == JEQ:
                if self.E == 1:
                    self.MAR = self.ram[self.PC + 1]
                    self.PC = self.reg[self.MAR]
                else:
                    self.PC += intruction_count

            elif self.IR == HLT: 
                running = False

            else:
                print("Unknown instruction")
                running = False

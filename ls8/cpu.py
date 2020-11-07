"""CPU functionality."""

import sys


HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8  # 8 general-purpose registers
        self.ram = [0] * 256     # hold 256 bytes of memory 
        self.pc = 0              # add properties for any internal registers
        self.running = True 
        self.branchtable = {}
        self.stack_pointer = 0xf4
        self.reg[7] = self.stack_pointer # Initialize the stack pointer. R7 is the dedicated stack pointer.

        # Flags
        self.E = None
        self.L = None
        self.G = None
      
        # Instructions
        self.branchtable[HLT] = self.handleHLT
        self.branchtable[LDI] = self.handleLDI
        self.branchtable[PRN] = self.handlePRN
        self.branchtable[MUL] = self.handleMUL
        self.branchtable[PUSH] = self.handlePUSH
        self.branchtable[POP] = self.handlePOP
        self.branchtable[ADD] = self.handleADD
        self.branchtable[RET] = self.handleRET
        self.branchtable[CALL] = self.handleCALL
      

    # should accept the address to read 
    # and return the value stored there.
    def ram_read(self, MAR):
        return self.ram[MAR]

    # should accept a value to write, 
    # and the address to write it to.
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        # passing file name to read 
        # commands  
        # stack instructions

        address = 0
        # file = sys.argv[1]

        if len(sys.argv) != 2:
            print("Wrong number of arguments, please pass file name")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#", 1)[0] # slip the line on the comment char
                        line = int(line, 2) # initialize base of 2
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        
        except FileNotFoundError:
            print(f"Could not find file {sys.argv[1]}")
            sys.exit(1)


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
        

    def handleHLT(self, a=None, b=None):
        # print("HLT")
        # exit
        self.running = False

    def handleLDI(self, a, b):
        # print("LDI")
        # set specified register to specified value
        self.reg[a] = b
        self.pc += 3

    def handlePRN(self, a, b=None):
        # print("PRN")
        # print value from specified register
        print(self.reg[a])
        self.pc += 2

    def handleMUL(self, a, b):
        # print("MUL")
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handlePUSH(self, a, b=None):
        # print("PUSH")
        # decrement stack pointer
        self.stack_pointer -= 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        # get register number and value stored at specified reg number
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]

        # store value in ram
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def handlePOP(self, a, b=None):
        # print("POP")
        # get value from ram
        address = self.stack_pointer
        val = self.ram[address]

        # store at given register
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val

        # increment stack pointer and program counter
        self.stack_pointer += 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        self.pc += 2

    def handleADD(self, a, b):
        # print("ADD")
        result = self.reg[a] + self.reg[b]
        self.reg[a] = result
        self.pc += 3

    def handleRET(self, a, b):
        # print("RET")
        # pop from stack
        val = self.ram[self.stack_pointer]
        # set pc back to previous
        self.pc = val
        # increment stack pointer
        self.stack_pointer += 1

    def handleCALL(self, a, b):
        # print("CALL")
        # return counter, save to stack
        rc = self.pc + 2
        self.stack_pointer -= 1
        self.ram[self.stack_pointer] = rc

        self.pc = self.reg[a]


    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)
            
            a = self.ram_read(self.pc + 1)
            b = self.ram_read(self.pc + 2)

            if IR not in self.branchtable:
                print(f'Unknown: {IR} at {self.pc}')
                self.running = False
            else:
                f = self.branchtable[IR]
                f(a, b)
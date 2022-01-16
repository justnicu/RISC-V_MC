import math
from computer.components.RAM import RAM

RAM = RAM.getInstance()

class CPU:
    INSTANCE = None

    @staticmethod
    def getInstance():
        if CPU.INSTANCE == None:
            CPU.INSTANCE = CPU()
        return CPU.INSTANCE

    # x0 - x31, pc
    registers = {
        "zero": 0,
        "ra": 0,
        "sp": 0,
        "gp": 0,
        "tp": 0,
        "t0": 0,
        "t1": 0,
        "t2": 0,
        "s0": 0,
        "s1": 0,
        "a0": 0,
        "a1": 0,
        "a2": 0,
        "a3": 0,
        "a4": 0,
        "a5": 0,
        "a6": 0,
        "a7": 0,
        "s2": 0,
        "s3": 0,
        "s4": 0,
        "s5": 0,
        "s6": 0,
        "s7": 0,
        "s8": 0,
        "s9": 0,
        "s10": 0,
        "s11": 0,
        "t3": 0,
        "t4": 0,
        "t5": 0,
        "t6": 0,
        "pc": 0
    }

    instruction = {
        "mc": 0,
        "opcode": 0,
        "rd": 0,
        "rs1": 0,
        "rs2": 0,
        "imm": 0,
        "funct3": 0,
        "funct7": 0,
        "DONE": 0
    }


    def empty(self):
        for name, val in self.registers.items():
            self.registers[name] = 0
        for name, val in self.instruction.items():
            self.instruction[name] = 0

    def run(self):
        while self.instruction["DONE"] == 0:
            instruction = {
                "mc": 0,
                "opcode": 0,
                "rd": 0,
                "rs1": 0,
                "rs2": 0,
                "imm": 0,
                "funct3": 0,
                "funct7": 0,
                "DONE": 0
            }

            print(self.registers["pc"])
            print(self.instruction["opcode"])

            self.instructionFetch()
            self.instructionDecode()
            self.execute()

    def instructionFetch(self):
        self.instruction["mc"] = RAM.getInformation(self.registers["pc"])

    def instructionDecode(self):
        binaryCode = bin(self.instruction["mc"])[2:]
        binaryCode = binaryCode.zfill(32)

        opcode = int(binaryCode[-7:], 2)
        self.instruction["opcode"] = opcode

        if opcode == 0x33:
            self.instruction["rd"] = (self.instruction["mc"] & 0xf80) >> 7
            self.instruction["funct3"] = (self.instruction["mc"] & 0x7000) >> 12
            self.instruction["rs1"] = (self.instruction["mc"] & 0xf8000) >> 15
            self.instruction["rs2"] = (self.instruction["mc"] & 0xf80000) >> 20
            self.instruction["funct7"] = (self.instruction["mc"]) >> 25

        elif opcode == 0x13 or opcode == 0x3:
            self.instruction["rd"] = (self.instruction["mc"] & 0xf80) >> 7
            self.instruction["funct3"] = (self.instruction["mc"] & 0x7000) >> 12
            self.instruction["rs1"] = (self.instruction["mc"] & 0xf8000) >> 15
            imm = (self.instruction["mc"] & 0xfff00000) >> 20
            self.instruction["imm"] = (imm & 0x7ff) - (imm & 0x800)

        elif opcode == 0x23:
            self.instruction["funct3"] = (self.instruction["mc"] & 0x7000) >> 12
            self.instruction["rs1"] = (self.instruction["mc"] & 0xf8000) >> 15
            self.instruction["rs2"] = (self.instruction["mc"] & 0xf80000) >> 20
            imm = ((self.instruction["mc"] & 0xf80) >> 7) + (((self.instruction["mc"]) >> 25) << 5)
            self.instruction["imm"] = (imm & 0x7ff) - (imm & 0x800)

        elif opcode == 0x37 or opcode == 0x17:
            self.instruction["rd"] = (self.instruction["mc"] & 0xf80) >> 7
            self.instruction["imm"] = (self.instruction["mc"] & 0xfffff000) >> 12

        elif opcode == 0x63:
            self.instruction["funct3"] = (self.instruction["mc"] & 0x7000) >> 12
            self.instruction["rs1"] = (self.instruction["mc"] & 0xf8000) >> 15
            self.instruction["rs2"] = (self.instruction["mc"] & 0xf80000) >> 20
            imm = (((self.instruction["mc"] & 0xf80) >> 8) << 1) + ((((self.instruction["mc"]) >> 25) & 0x3f) << 5) + ((self.instruction["mc"] & 0x80) << 11) + ((self.instruction["mc"] >> 31) << 12)
            self.instruction["imm"] = (imm & 0xfff) - (imm & 0x1000)

        elif opcode == 0x6f:
            imm = (((self.instruction["mc"] >> 21) << 1) & 0x7ff) + (((self.instruction["mc"] >> 20) & 0x1) << 11) + (((self.instruction["mc"] >> 12) & 0xff) << 12) + ((self.instruction["mc"] >> 31) << 20)
            self.instruction["imm"] = (imm & 0xfffff) - (imm & 0x100000)

        elif opcode == 0x73:
            if self.registers['a0'] == 1:
                print("Pass")
            else:
                print("Failure")
            self.instruction["DONE"] = True

    def execute(self):
        if self.instruction["opcode"] == 0x6F:
            self.registers["pc"] += self.instruction["imm"] // 4

        elif self.instruction["opcode"] == 0x13:
            if self.instruction["funct3"] == 0:
                rdKey = self.registerKey(self.instruction["rd"])
                rs1Key = self.registerKey(self.instruction["rs1"])

                if rdKey != "zero":
                    self.registers[rdKey] = (self.registers[rs1Key] + self.instruction["imm"]) & 0xFFFFFFFF
                    self.registers[rdKey] = (self.registers[rdKey] & 0x7fffffff) - (self.registers[rdKey] & 0x80000000)

            elif self.instruction["funct3"] == 6:
                rdKey = self.registerKey(self.instruction["rd"])
                rs1Key = self.registerKey(self.instruction["rs1"])

                if rdKey != "zero":
                    self.registers[rdKey] = self.registers[rs1Key] | self.registers["imm"]

            elif self.instruction["funct3"] == 0:
                rdKey = self.registerKey(self.instruction["rd"])
                rs1Key = self.registerKey(self.instruction["rs1"])
                shamt_i = self.instruction["imm"] & 0x1F

                if rdKey != "zero":
                    self.registers[rdKey] = ((self.registers[rs1Key] << shamt_i) & 0xffffffff)

            self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x3:
            if self.instruction["funct3"] == 2:
                rdKey = self.registerKey(self.instruction["rd"])
                rs1Key = self.registerKey(self.instruction["rs1"])

                memoryAddress = self.instruction["imm"] + self.registers[rs1Key]
                memoryAddressValue = self.memoryAccess(memoryAddress)
                memoryAddressValue = (memoryAddressValue & 0x7fffffff) - (memoryAddressValue & 0x80000000)

                if rdKey != "zero":
                    self.registers[rdKey] - memoryAddressValue

            self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x23:
            rs1Key = self.registerKey(self.instruction["rs1"])
            rs2Key = self.registerKey(self.instruction["rs2"])

            if self.instruction["funct3"] == 2:
                memoryAddress = self.registers[rs1Key] + self.instruction["imm"]
                value = self.registers[rs2Key]

                if value < 0:
                    value += (1 << 32)
                self.writeBack(memoryAddress, value)

            self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x63:
            if self.instruction["funct3"] == 0:
                rs1Key = self.registerKey(self.instruction["rs1"])
                rs2Key = self.registerKey(self.instruction["rs2"])

                if self.registers[rs1Key] == self.registers[rs2Key]:
                    print("debug" + str(self.instruction["imm"]))
                    self.registers["pc"] += self.instruction["imm"] // 4

                else:
                    self.registers["pc"] += 1

            elif self.instruction["funct3"] == 1:
                rs1Key = self.registerKey(self.instruction["rs1"])
                rs2Key = self.registerKey(self.instruction["rs2"])

                if self.registers[rs1Key] != self.registers[rs2Key]:
                    self.registers["pc"] += self.instruction["imm"] // 4

                else:
                    self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x37:
            rdKey = self.registerKey(self.instruction["rd"])

            if rdKey != "zero":
                self.registers[rdKey] = self.instruction["imm"] << 12

                self.registers[rdKey] == (self.registers[rdKey] & 0x7fffffff) - (self.registers[rdKey] & 0x80000000)

            self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x17:
            rdKey = self.registerKey(self.instruction["rd"])
            imm = (self.instruction["imm"] << 12) + self.registers["pc"] * 4

            if rdKey != "zero":
                self.registers[rdKey] = imm

            self.registers["pc"] += 1

        elif self.instruction["opcode"] == 0x33:
            if self.instruction["funct3"] == 5:
                if (self.instruction["rs2"] & 0xFE0) == 0:
                    rdKey = self.registerKey(self.instruction["rd"])
                    rs1Key = self.registerKey(self.instruction["rs1"])
                    rs2Key = self.registerKey(self.instruction["rs2"])

                    if rdKey != "zero":
                        shift = self.registers[rs2Key] & 0x1F

                        if shift == 0:
                            self.registers[rdKey] = self.registers[rs1Key]

                        else:
                            val = self.registers[rs1Key]

                            if val < 0:
                                val += (1 << 32)
                                binary = bin(val)[2:].zfill(32)
                                shifted = ("0" * shift) + binary[:-shift]
                                val = int(shifted, 2)

                            else:
                                val = val >> shift

                            self.registers[rdKey] = val

            elif self.instruction["funct3"] == 4:
                rdKey = self.registerKey(self.instruction["rd"])
                rs1Key = self.registerKey(self.instruction["rs1"])
                rs2Key = self.registerKey(self.instruction["rs2"])

                if rdKey != "zero":
                    self.registers[rdKey] = self.registers[rs1Key] ^ self.registers[rs2Key]

            elif self.instruction["funct3"] == 6:
                if ((self.instruction["rs2"] & 0xfe0) >> 5) == 1:
                    rdKey = self.registerKey(self.instruction["rd"])
                    rs1Key = self.registerKey(self.instruction["rs1"])
                    rs2Key = self.registerKey(self.instruction["rs2"])

                    if rdKey != "zero":
                        if self.registers[rs2Key] == 0:
                            self.registers[rdKey] = self.registers[rs1Key]

                        elif self.registers[rs1Key] * self.registers[rs2Key] > 0:
                            self.registers[rdKey] = self.registers[rs1Key] % self.registers[rs2Key]

                        else:
                            self.registers[rdKey] = self.registers[rs1Key] - math.ceil(self.registers[rs1Key] / self.registers[rs2Key]) * self.registers[rs2Key]

            self.registers["pc"] += 1

        else:
            self.registers["pc"] += 1


    def memoryAccess(self, position):
        return RAM.getInformation((position - RAM.OFFSET) // 4)

    def writeBack(self, position, data):
        RAM.write((position - RAM.OFFSET) // 4, data)

    def registerKey(self, idx):
        return list(self.registers.keys())[idx]

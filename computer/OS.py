from os import listdir
from os.path import isfile, join

from computer.components.RAM import RAM
from computer.components.CPU import CPU

RAM = RAM.getInstance()
CPU = CPU.getInstance()

class OS:
    STORAGE_PATH = "./computer/components/storage"
    INSTANCE = None

    @staticmethod
    def getInstance():
        if OS.INSTANCE == None:
            OS.INSTANCE = OS()
        return OS.INSTANCE

    def getFiles(self):
        files = [self.STORAGE_PATH + "/" + file for file in listdir(self.STORAGE_PATH) if isfile(join(self.STORAGE_PATH, file))]
        return files

    def runExecutables(self):
        files = self.getFiles()

        for mc in files:
            instructions, data = self.parseFile(mc)

            RAM.empty()
            CPU.empty()

            RAM.initStack(instructions, data)
            RAM.loadStack(instructions, data)

            CPU.run()


    def parseFile(self, file):
        currentSection = ".text"
        instructions = {}
        data = {}
        lastDataAddress = None

        with open(file, "r") as file:
            for line in file.readlines():
                if ".data" in line:
                    currentSection = ".data"

                line = line.replace("\n", "")
                line = line.split(":")

                if len(line) == 2 and line[1] != "":
                    address = line[0].strip()
                    instruction = line[1].strip()

                    if currentSection == ".text":
                        instructions[address] = instruction

                    elif currentSection == ".data":
                        if lastDataAddress == None:
                            lastDataAddress = address
                            data[lastDataAddress] = instruction

                        elif int(address, 16) - int(lastDataAddress, 16) == 2:
                            data[lastDataAddress] = data[lastDataAddress] + instruction

                        else:
                            lastDataAddress = address
                            data[lastDataAddress] = instruction

        return instructions, data

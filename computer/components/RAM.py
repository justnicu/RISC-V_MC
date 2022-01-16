class RAM:
    INSTANCE = None

    @staticmethod
    def getInstance():
        if RAM.INSTANCE == None:
            RAM.INSTANCE = RAM()
        return RAM.INSTANCE

    def __init__(self):
        self.OFFSET = 0
        self.stack = []

    def initStack(self, instructions, data):
        minAddress = min(instructions.keys())
        maxAddress = max(instructions.keys())

        if data:
            minAddress = min(minAddress, min(data.keys()))
            maxAddress = max(maxAddress, max(data.keys()))

        size = (int(maxAddress, 16) - int(minAddress, 16)) // 4 + 1
        self.stack = [0 for aux in range(size)]

    def loadStack(self, instructions, data):
        realOffset = True
        for address, instruction in instructions.items():
            if realOffset:
                self.OFFSET = int(address, 16)
            realOffset = False;
            address = int(address, 16)
            instruction = int(instruction, 16)

            position = (address - self.OFFSET) // 4
            self.stack[position] = instruction

        for address, info in data.items():
            address = int(address, 16)
            info = int(info, 16)

            position = (address - self.OFFSET) // 4
            self.stack[position] = info

    def empty(self):
        self.OFFSET = 0
        self.stack = []

    def getInformation(self, position):
        return self.stack[position]

    def write(self, position, data):
        size = len(self.stack)
        space = position - size
        if space > 0:
            self.stack = self.stack + [0 for aux in range(space + 1)]

        self.stack[position] = data

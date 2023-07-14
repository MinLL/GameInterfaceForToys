from interfaces.interface import Interface
from common.util import *
import ReadWriteMemory

class MemoryReaderInterface(Interface):
    def __init__(self, toy_type):
        Interface.__init__(self, "Memory Reader", toy_type)

    def execute(self):
        pass


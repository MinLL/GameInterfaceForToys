
from common.util import *
from toys.vibrators.vibrator import Vibrator



import ctypes
import time
import threading

# Define necessary structures
class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

class XboxControllerInterface(Vibrator):
    def __init__(self):
        self.taskList = []
        t1 = threading.Thread(target=self.t1, args=(), daemon=True)
        t1.start()
        super().__init__("Xbox controller")
    
    def t1(self):
        # print('time thread '," running ....")
        xinput = ctypes.windll.xinput1_1
        XInputSetState = xinput.XInputSetState
        XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
        XInputSetState.restype = ctypes.c_uint
        self.taskList = []
        vibration = XINPUT_VIBRATION(int(1 * 65535), int(1 * 65535))
        XInputSetState(0, ctypes.byref(vibration))
        time.sleep(5)
        vibration = XINPUT_VIBRATION(int(0 * 65535), int(0 * 65535))
        XInputSetState(0, ctypes.byref(vibration))

        nowStrength = 0
        while True:
            time.sleep(0.5)
            r = 0
            newtaskList = []
            for i in self.taskList:
                i[0] -= 0.5
                if i[0] <= 0:
                    continue
                if i[1] > r:
                    r = i[1]
                newtaskList.append(i)
            self.taskList = newtaskList
            strength = r/100.0*0.8
            if strength > 0.01 : strength += 0.2
            if strength > 1: strength = 1
            # print("0.5s passed " + str(strength) + str(self.taskList))
            if nowStrength != strength:
                vibration = XINPUT_VIBRATION(int(strength * 65535), int(strength * 65535))
                XInputSetState(0, ctypes.byref(vibration))
                nowStrength = strength
    
    def shutdown(self):
        pass
        
    def connect(self):
        return

    def check_in(self):
        return
        

    def vibrate(self, duration, strength, pattern=""):
        # print('addCommand',self.command)
        self.taskList.append([duration,strength])
    
    def stop(self):
        # print('cleanTaskList')
        self.taskList.clear()

    def shutdown(self):
        pass
    
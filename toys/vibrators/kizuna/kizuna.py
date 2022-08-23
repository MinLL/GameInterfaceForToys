import bluetooth
import serial
from serial.tools.list_ports import (comports)
import datetime
from toys.vibrators.vibrator import Vibrator
from common.util import *
from settings import *

class KizunaInterface(Vibrator):
    KIZUNA_NAME = "KIZUNA SMART"
    UPDATE_DELAY = datetime.timedelta(seconds = 0.4)

    def __init__(self):
        super().__init__("Kizuna")
        self.kizuna_serial_port = None
        self.last_updated = datetime.datetime.utcnow()
        self.stop_time = None

    def shutdown(self):
        if self._is_connected():
            self.kizuna_serial_port.close()
    
    def connect(self):
        self._open_serial_port()

    def check_in(self):
        now = datetime.datetime.utcnow()
        if (self.stop_time is not None and now >= self.stop_time):
            self.stop_time = None
            self.stop()
        
    def vibrate(self, duration, strength):
        now = datetime.datetime.utcnow()
        # Delay to avoid overwhelming the motor with sudden changes
        if (now - self.last_updated >= self.UPDATE_DELAY):
            self._write_speed(min(9, strength // 10))
            self.stop_time = now + datetime.timedelta(seconds = duration)
            # Fresh time to ensure the delay isn't shortened by scheduler delays
            self.last_updated = datetime.datetime.utcnow()

    def stop(self):
        self._write_speed(0)

    def _open_serial_port(self):
        nearby_devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = 1)
        kizuna_info = [i for i in nearby_devices if i[1] == "KIZUNA SMART"]
        if len(kizuna_info) == 1:
            addr = kizuna_info[0][0]
            addr_short = addr.replace(":", "")

            com_ports = comports()
            kizuna_comport = [p for p in com_ports if addr_short in p.hwid]

            if len(kizuna_comport) == 1:
                try:
                    kizuna_serial = serial.Serial(kizuna_comport[0].device)
                    info("Connected to Kizuna Smart Controller on port {}".format(kizuna_comport[0].name))
                    self.kizuna_serial_port = kizuna_serial
                except Exception as err:
                    fail(err)
                return 
        fail("Failed to find Kizuna Smart Controller")

    def _write_speed(self, speed):
        if not self._is_connected():
            pass
        elif (speed >= 0 and speed <= 9):
            self.kizuna_serial_port.write(bytes(str(speed) + "\r\n", "ASCII"))
        else:
            fail("Bad speed: " + speed)

    def _is_connected(self):
        return self.kizuna_serial_port is not None

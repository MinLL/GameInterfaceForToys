import requests
from common.util import *
from toys.vibrators.vibrator import Vibrator
import settings
import random
import math

class LovenseInterface(Vibrator):
    def __init__(self):
        self.COMMAND_URL = "http://{}/command".format(settings.LOVENSE_HOST)
        super().__init__("Lovense")

    def shutdown(self):
        pass
    
    def _command(self, command, duration):
        info("Sending vibrate command")
        params = {
            'command':"Function",
            'action': command,
            'timeSec': duration,
            'apiVer':1
        }
        return requests.post(self.COMMAND_URL, verify=False, json=params)

    def _send_pattern(self, duration, pattern, interval=1000):
        pattern = ";".join([str(self.scale_strength(x)) for x in pattern])
        info("Sending pattern command: {} at interval {}".format(str(pattern), interval))
        # interval should be 100 minimum, ms inbetwen steps
        params = {
            'command': "Pattern",
            'rule': "V:1;F:vrp;S:{}#".format(interval),
            'strength': pattern,
            'timeSec': duration,
            'apiVer': 1
        }
        return requests.post(self.COMMAND_URL, verify=False, json=params)
    
    def connect(self):
        return

    def check_in(self):
        return

    def scale_strength(self, strength):
        return math.ceil(strength * (float(settings.LOVENSE_STRENGTH_SCALE) / 100))
    
    def vibrate(self, duration, strength, pattern=""):
        if pattern == "":
            strength = self.scale_strength(strength)
            strength = math.ceil(int(strength)/5) # Lovense supports 0-20 scale for vibrations
            r = self._command("Vibrate:"+str(strength), duration)
        else:
            r = self._send_pattern(duration, random.choice(self.patterns[pattern]), (350 + (1000 - strength * 10)))
        if r.json()['code'] == 200:
            success("  " + str(r.json()))
        else:
            fail("  " + str(r.json()))
    def stop(self):
        r = self._command("Stop", 0)
        if r.json()['code'] == 200:
            success("  " + str(r.json()))
        else:
            fail("  " + str(r.json()))

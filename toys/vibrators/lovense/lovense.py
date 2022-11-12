import requests
from common.util import *
from toys.vibrators.vibrator import Vibrator
from settings import LOVENSE_HOST

class LovenseInterface(Vibrator):
    COMMAND_URL = "http://{}/command".format(LOVENSE_HOST)

    def __init__(self):
        super().__init__("Lovense")

    def shutdown(self):
        pass
    
    def _command(self, command, duration):
        params = {
            'command':"Function",
            'action': command,
            'timeSec': duration,
            'apiVer':1
        }
        return requests.post(self.COMMAND_URL, verify=False, json=params)
        
    def connect(self):
        return

    def check_in(self):
        return
        
    def vibrate(self, duration, strength):
        
        r = self._command("Vibrate:"+str(strength), duration)
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

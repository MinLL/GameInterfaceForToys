import requests
from common.util import *
from toys.vibrators.vibrator import Vibrator

class LovenseInterface(Vibrator):
    COMMAND_URL = "http://127.0.0.1:20010/command"

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
        r = self._command("Action:"+str(strength), duration)
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

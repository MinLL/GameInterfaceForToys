from common.util import *
from toys.vibrators.vibrator import Vibrator
from toys.base import FEATURE_EDGE
import settings
import random
import math
import websockets
import asyncio
import json

class EdgeomaticInterface(Vibrator):
    def __init__(self):
        super().__init__("Edge-o-matic 3000", tags=[FEATURE_EDGE])
        self.duration = 0
        self.ws = None
        self.checking_in = False
        
    async def shutdown(self):
        if self.ws:
            return await self.ws.close()

    async def connect(self):
        info("Connecting to " + settings.MAUSTEC_HOST)
        self.ws = await websockets.connect(settings.MAUSTEC_HOST)
        info("Connected.")


    async def check_in(self):
        if self.checking_in: 
            return
        if not self.ws:
            await self.connect()
            return
        self.checking_in = True
        try:
            data = await self.ws.recv()
            data = json.loads(data)
            if "readings" in data:
                self.motor_strength = data["readings"]["motor"]
                self.runMode = data["readings"]["runMode"]
                # info("motor strength = {}, runMode = {}".format(self.motor_strength, self.runMode))
                #  {"readings":{"pressure":2129,"pavg":2131,"motor":0,"arousal":0,"millis":8962305,"scaledArousal":0,"runMode":"Manual","permitOrgasm":false,"postOrgrasm":false,"lock":false}}
        except websockets.exceptions.ConnectionClosedError:
            await self.connect()
        self.checking_in = False

    async def _setMode(self, mode):
        info("Setting mode to {}".format(mode))
        data = {
            "setMode": mode
        }
        return await self._send_cmd(data)

    async def _send_cmd(self, data):
        while True:
            try:
                return await self.ws.send(str(data))
            # Device does not respond to standard websockets ping/pong, and keeps timing out.
            # This is a work-around. TODO: Fix this properly.
            except websockets.exceptions.ConnectionClosedError:
                return await self.connect()
        
    def scale_strength(self, strength):
        # Unit takes a 0-258 range. Scale 0-100 strength accordingly
        min_strength = 0
        max_strength = 258
        vibrateRange = (100 - 0)  
        stimRange = (max_strength - min_strength)
        # cast float to integer for compatibility with func.
        return int((((strength - 0) * stimRange) / vibrateRange) + min_strength)
    
    async def _setMotor(self, strength):
        strength = self.scale_strength(strength)
        info("Setting motor strength to "+ str(strength))
        data = {
            "setMotor": int(strength)
        }
        return await self._send_cmd(data)
    

    async def _runMode(self, mode, duration, strength=0, pattern=""):
        is_manual = (mode == "manual")
        if self.duration > 0:
            self.duration += duration
            info("Added {} to duration. Remaining: {}".format(duration, self.duration - self.i))
            return
        info("Running mode {} for {} seconds".format(mode, duration))
        self.duration = duration
        await self._setMode(mode)
        if is_manual:
            pattern = random.choice(self.patterns[pattern])
            pattern_counter = 0
        self.i = 0
        while self.i < (self.duration):
            if is_manual:
                if pattern_counter >= len(pattern):
                    pattern_counter = 0
                await self._setMotor(self.scale_strength(pattern[pattern_counter] * 5))
                pattern_counter += 1
            await asyncio.sleep(0.25)
            self.i += 0.25
        await self.stop()
        
    async def vibrate(self, duration, strength, pattern=""):
        await self._setMotor(strength)
        await self._runMode("manual", duration, strength, pattern)

    async def vibrate_plus(self, duration, strength, pattern=""):
        await self._runMode("automatic", duration)

    async def stop(self):
        if self.duration != 0:
            self.duration = 0
            timeout = 0
            while (self.motor_strength != 0 or self.runMode != "Manual") and timeout < 20:
                await self._setMode("manual")
                await self._setMotor(0)
                await self.check_in()
                await asyncio.sleep(0.2)
                timeout += 1
            


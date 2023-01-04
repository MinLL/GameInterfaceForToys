import asyncio
import time
from buttplug.client import (ButtplugClientWebsocketConnector, ButtplugClient,
                             ButtplugClientConnectorError)
import settings
from common.util import *
from toys.vibrators.vibrator import Vibrator

class ButtplugInterface(Vibrator):
    CLIENT_NAME = "GameInterfaceForToys"
    _BASE_VIBRATE_STRENGTH_COEFFICIENT = 0.01
    _MAX_STRENGTH = 100
    VIBRATE_STRENGTH_COEFFICIENT = _BASE_VIBRATE_STRENGTH_COEFFICIENT * \
        (min(_MAX_STRENGTH, int(settings.BUTTPLUG_STRENGTH_MAX)) / _MAX_STRENGTH)

    def shutdown(self):
        pass
    
    def __init__(self):
        super().__init__("ButtplugIO")
        info("Buttplug.io vibrate strength coefficient: {}".format(self.VIBRATE_STRENGTH_COEFFICIENT))
        self.stop_time = -1
        self.client = ButtplugClient(self.CLIENT_NAME)

    async def connect(self):
        connector = ButtplugClientWebsocketConnector(settings.BUTTPLUG_SERVER_ADDRESS)
        try:
            await self.client.connect(connector)
        except ButtplugClientConnectorError as e:
            print("Could not connect to Buttplug.io server, exiting: {}".format(e.message))
            return

        # Immediately scan for devices and just connect whatever we find
        await self.client.start_scanning()
        await asyncio.sleep(3)
        while (len(self.client.devices) == 0):
            print("Searching for devices...")
            await asyncio.sleep(2)
        print("Found devices: {}".format(self.client.devices.values()))
        await self.client.stop_scanning()

    async def check_in(self):
        if (self.stop_time > 0 and time.time() > self.stop_time):
            self.stop_time = -1
            await self.stop()

    async def vibrate(self, duration, strength, pattern="", toys=[]):
        for device in self.client.devices.values():
            if len(toys) > 0:
                if not device.name in [toy['name'] for toy in toys]:
                    print("{} does not match {}".format(device.name, str([toy['name'] for toy in toys])))
                    continue
            if "VibrateCmd" in device.allowed_messages.keys():
                await device.send_vibrate_cmd(strength * self.VIBRATE_STRENGTH_COEFFICIENT)
        self.stop_time = time.time() + duration

    async def stop(self):
        for device in self.client.devices.values():
            await device.send_stop_device_cmd()

    def get_toys(self):
        ret = {}
        for device in self.client.devices.values():
            ret[device.name] = {
                "name": device.name,
                "id": device.name,
                "battery": -1,
                "enabled": True,
                "interface": self.properties['name']
            }
        return ret

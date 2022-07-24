import asyncio
import bluetooth
import datetime
import io
import os
import random
import re
import requests
import serial
import time
from buttplug.client import (ButtplugClientWebsocketConnector, ButtplugClient,
                             ButtplugClientConnectorError)
from dg_interface import CoyoteInterface
from serial.tools.list_ports import (comports)
import types
from constants import *
from settings import *

## Don't edit anything below this line.
VERSION = "Alpha 4"

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MAX_VIBRATE_STRENGTH = 100

class FatalException(Exception):
    pass

def info(s):
    print(colors.OKCYAN + "[SkyrimToyInterface] [i] " +str(s) + colors.ENDC)

def success(s):
    print(colors.OKGREEN + "[SkyrimToyInterface] [+] " + str(s) + colors.ENDC)

def fail(s):
    print(colors.FAIL + "[SkyrimToyInterface] [-] " + str(s) + colors.ENDC)
    beep()

def beep():
    print("\a")

class ChasterInterface(object):
    def __init__(self, lock_name, developer_token, toys):
        self.toys = toys
        self.lock_name = lock_name
        self.token = developer_token
        self.api_root = "https://api.chaster.app/"
        self.extensions = {}
        self.enabled = True
        self.wheel_hooks = {
            'slsi_shock1': self.slsi_shock1,
            'slsi_shock2': self.slsi_shock2,
            'slsi_dice': lambda: "Dice Game: {}".format(self.roll_dice()),
            'slsi_gear': lambda: "Gear Task: {}".format(self.assign_task("Match your characters bondage outfit for two hours.")),
            'slsi_plug': lambda: "Plug Task: {}".format(self.assign_task("Insert a plug and keep it there for at least an hour.")),
            'slsi_clamps': lambda: "Clamp Task: {}".format(self.assign_task("Wear your clamps for at least 20 minutes.") ),
            'slsi_overstimulate': self.overstimulate,
            'slsi_tease': self.tease,
        }

    def slsi_shock1(self):
        return self.toys.vibrate(5, 80)

    def slsi_shock2(self):
        return self.toys.vibrate(10, 100)
    
    def overstimulate(self):
        return self.toys.vibrate(random.randint(300, 600) , 100)

    def tease(self):
        return self.toys.vibrate(240, 5)
        

    def setup(self):
        try:
            self.select_lock(self.lock_name)
        except Exception as e:
            fail(str(e))
            fail("Failed to initialize chaster. Disabling for this run.")
            self.enabled = False
            return
        
    def _api(self, method, endpoint, data={}):
        if not self.enabled:
            raise Exception("Chaster is disabled.")
        headers = {
            "Authorization": "Bearer " + self.token,
            "accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "SkyrimToyInterface {}".format(VERSION)
        }
        if method == "GET":
            return requests.get(self.api_root + endpoint, headers=headers, timeout=10)
        elif method == "POST":
            return requests.post(self.api_root + endpoint, headers=headers, json=data, timeout=10)
        else:
            raise FatalException("Unsupported method type to ChasterInterface")


    def _get_locks(self):
        r = self._api("GET", "locks?status=active")
        try:
            if r.status_code == 401:
                fail("User is unauthorized to fetch list of locks (Is your token valid?)")
                raise FatalException("Invalid Chaster Token")
            if r.status_code != 200:
                fail("Failed to fetch lock status: " + str(r.json()))
                return
            return r.json()
        except Exception as e:
            fail(r.text)
            raise e
        
    def select_lock(self, lock_name):
        info("select_lock({})".format(lock_name))
        locks = self._get_locks()
        lock_found = False
        for lock in locks:
            if lock['title'] == lock_name:
                if (lock_found):
                    raise FatalException("Found more than one lock matching name. Archive unused locks!")
                lock_found = lock
        if not lock_found:
            raise FatalException("Failed to find lock matching name: " + str(lock_name))
        self.lock = lock_found
        success("  Found lock: " + lock_name)
        success("  Status: " + lock['status'])
        success("  Role: " + lock['role'])
        info("Processing extensions...")
        for extension in self.lock['extensions']:
            success("  Found [{}] extension".format(extension['slug']))
            self.extensions[extension['slug']] = extension
        return lock_found
    
    def update_time(self, duration):
        info("update_time({})".format(duration))
        r = self._api("POST", "locks/{}/update-time".format(self.lock["_id"]), {"duration": duration})
        if r.status_code != 204:
            fail("  Failed to update lock time: Status code {}: {}".format(r.status_code, str(r.json())))
            return
        success("  Updated lock duration by {} seconds.".format(duration))

    def _run_extension(self, extension, foo):
        try:
            payload = foo()
            url = "locks/{}/extensions/{}/action".format(self.lock['_id'], self.extensions[extension]['_id'])
            info("Running {} on extension {}".format(payload['action'], extension))
            r = self._api("POST", url, foo())
            if r.status_code == 201:
                success("  Extension executed successfully.")
            else:
                fail("  Failed to execute extension ({}): {}".format(r.status_code, r.text))
            return r
        except KeyError:
            fail("  Extension {} not enabled for lock {}".format(extension, self.lock['title']))
    
    def assign_task(self, task, points=0):
        beep()
        return self._run_extension(extension="tasks", foo=lambda: {
            'action': 'assignTask',
            'payload':{
                'task': {
                    'task': task,
                    'points': points
                }
            }
        })

    def roll_dice(self):
        r = self._run_extension(extension="dice", foo=lambda: {
            'action': 'submit',
            'payload': {}
        })
        success("    Outcome: Changed lock duration by {} minutes".format(str((int(r.json()['duration'])) / 60)))
        return r

    def spin_wheel(self):
        r = self._run_extension(extension="wheel-of-fortune", foo=lambda: {
            'action': 'submit',
            'payload': {}
        })
        response = r.json()['text']
        if response in self.wheel_hooks.keys():
            response = self.wheel_hooks[response]()
        success("    Outcome: {}".format(response))
        return response


class LovenseInterface(object):
    COMMAND_URL = "http://127.0.0.1:20010/command"

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


class ButtplugInterface(object):
    BUTTPLUG_SERVER_URI = "ws://127.0.0.1:12345"
    CLIENT_NAME = "SkyrimToyInterface" 
    # Full strength:
    VIBRATE_STRENGTH_COEFFICIENT = 0.01
    # Or half strength:
    #VIBRATE_STRENGTH_COEFFICIENT = 0.005

    def shutdown(self):
        pass
    
    def __init__(self):
        self.stop_time = -1
        self.client = ButtplugClient(self.CLIENT_NAME)

    async def connect(self):
        connector = ButtplugClientWebsocketConnector(self.BUTTPLUG_SERVER_URI)
        try:
            await self.client.connect(connector)
        except ButtplugClientConnectorError as e:
            print("Could not connect to Buttplug.io server, exiting: {}".format(e.message))
            return

        # Immediately scan for devices and just connect whatever we find
        await self.client.start_scanning()
        while (len(self.client.devices) == 0):
            print("Searching for devices...")
            await asyncio.sleep(2)
        print("Found devices: {}".format(self.client.devices.values()))
        await self.client.stop_scanning()

    async def check_in(self):
        if (self.stop_time > 0 and time.time() > self.stop_time):
            self.stop_time = -1
            await self.stop()

    async def vibrate(self, duration, strength):
        for device in self.client.devices.values():
            if "VibrateCmd" in device.allowed_messages.keys():
                await device.send_vibrate_cmd(strength * self.VIBRATE_STRENGTH_COEFFICIENT)
        self.stop_time = time.time() + duration

    async def stop(self):
        for device in self.client.devices.values():
            await device.send_stop_device_cmd()


class KizunaInterface(object):
    KIZUNA_NAME = "KIZUNA SMART"
    UPDATE_DELAY = datetime.timedelta(seconds = 0.4)

    def __init__(self):
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
        


class ToyInterface(object):
    def shutdown(self):
        ret = []
        for toy in self.interface:
            ret += [toy.shutdown()]
        return ret
    
    def __init__(self, toy_type):
        self.interface = []
        for toy in toy_type:
            if toy == TOY_LOVENSE:
                self.interface += [LovenseInterface()]
            elif toy == TOY_BUTTPLUG:
                self.interface += [ButtplugInterface()]
            elif toy == TOY_COYOTE:
                self.interface += [CoyoteInterface(device_uid="C1:A9:D8:0C:CB:1D",
                                                 power_multiplier=7.68,
                                                 default_channel="a",
                                                 safe_mode=True)]  # See implementation for parameter details
            elif toy == TOY_KIZUNA:
                self.interface += [KizunaInterface()]
            else:
                raise FatalException("Unsupported toy type!")

    def connect(self):
        ret = []
        for toy in self.interface:
            ret += [toy.connect()]
        return ret

    def check_in(self):
        ret = []
        for toy in self.interface:
            ret += [toy.check_in()]
        return ret

    def vibrate(self, duration, strength):
        info("Vibrate - start(duration={}, strength={})".format(duration, strength))
        ret = []
        for toy in self.interface:
            info("  Vibrate - " +  str(toy))
            ret += [toy.vibrate(duration, strength)]
        return ret

    def stop(self):
        info("Vibrate - stop")
        ret = []
        for toy in self.interface:
            ret += [toy.stop()]
        return ret


class SkyrimScriptInterface(object):
    SEX_STAGE_STRENGTH_MULTIPLIER = 20

    def shutdown(self):
        return self.toys.shutdown()
        
    def __init__(self, toy_type=TOY_LOVENSE, token=False):
        self._cached_stamp = 0
        self.filename = LOG_PATH
        self.file_pointer = 0
        fd = open(self.filename, 'r')
        self._set_eof(fd)
        fd.close()
        self.chaster_enabled = (token and token != "")
        self.token = token
        self.toys = ToyInterface(toy_type)
        self.sex_stage = None

    def _chaster_spin_wheel(self, match):
        return self.chaster.spin_wheel()
    
    def setup(self):
        sexlab_hooks = {
            # Sexlab Support
            #SEXLAB - ActorAlias[min] SetActor
            re.compile(".+SEXLAB - ActorAlias\[{}\] SetActor.+".format(CHARACTER_NAME.lower()), re.I): self.sex_start,
            re.compile(".+SEXLAB - ActorAlias\[{}\]  - Resetting!+".format(CHARACTER_NAME.lower()), re.I): self.sex_end,
            re.compile(".+SEXLAB - Thread[(0-9)+] Event Hook - StageStart$", re.I): self.sex_stage_start
            
        }
        chaster_hooks = {}
        if self.chaster_enabled:
            chaster_hooks = {
                # Defeat integration
                re.compile(".+Defeat: SetFollowers / Scenario.+$"): self._chaster_spin_wheel, # Player was knocked down.
                re.compile(".+Defeat: PostAssault Marker Found.+$"): lambda m: self.chaster.update_time(random.randint(CHASTER_DEFEAT_MIN, CHASTER_DEFEAT_MAX)), # Party was defeated.
                re.compile(".+Defeat: Player victim - End scene, Restored.+$"): self._chaster_spin_wheel, #  Player actually died.
                # Naked Defeat integration
                re.compile(".+NAKED DEFEAT playeraliasquest: OnEnterBleedout\(\).+"): self._chaster_spin_wheel, # Player was knocked down.
                re.compile(".+NAKED DEFEAT playeraliasquest: \(#msg\) All is lost.+"): lambda m: self.chaster.update_time(random.randint(CHASTER_DEFEAT_MIN, CHASTER_DEFEAT_MAX)) # Party was defeated.
            }
        devious_hooks = {
            # Devious Devices Support
            re.compile(".+VibrateEffect.([0-9]+) for ([0-9]+).+"): self.vibrate,
            re.compile(".*\[SkyrimToyInterface\]: OnVibrateStop().*"): self.stop_vibrate,
            re.compile(".*\[SkyrimToyInterface\]: OnDeviceActorOrgasm().*"): self.player_orgasmed,
            re.compile(".*\[SkyrimToyInterface\]: OnDeviceEdgedActor().*"): self.player_edged,
            re.compile(".*\[SkyrimToyInterface\]: OnSitDevious().*"): self.player_sit,
            re.compile(".*Processing \[(.+)\].*"): self.dd_event
        }
        toys_hooks = {
            # Toys support
            re.compile(".+\[TOYS\] ControllerShake (Left|Right), ([0-9.]+), ([0-9]+.?[0-9]|.[0-9]+)+"): self.toys_vibrate

        }
        misc_hooks = {
            # Stack Dump Monitoring Support
            re.compile(".*\[SkyrimToyInterface\]: OnHit\(akProjectile='.*?', abPowerAttack='(TRUE|False)', abBashAttack='(TRUE|False)', abSneakAttack='(TRUE|False)', abHitBlocked='(TRUE|False)'\): \[health='([0-9.]+)\/([0-9.]+)', magicka='([0-9.]+)\/([0-9.]+)', stamina='([0-9.]+)\/([0-9.]+)'\].*"): self.on_hit,
            re.compile("^.+[tT]hreshold.+"): self.stack_overflow
        }
        self.hooks = {**sexlab_hooks, **chaster_hooks, **devious_hooks, **toys_hooks, **misc_hooks}

        if self.chaster_enabled:
            self.chaster = ChasterInterface(LOCK_NAME, self.token, self.toys)
            self.chaster.setup()
            
    def dd_event(self, match):
        # Processing [Nipple Piercings]
        return self.toys.vibrate(random.randint(2, 30), 10)
        
    def stack_overflow(self, match):
        if not WARN_ON_STACK_DUMP:
            return
        while(True):
            self.toys.vibrate(1, 100)
            beep()
            asyncio.sleep(2)
            
    def _set_eof(self, fd):
        fd.seek(0, io.SEEK_END)
        self.file_pointer = fd.tell()
        
    def vibrate(self, match):
        return self.toys.vibrate(int(match.group(2)) * DD_VIB_MULT, 20 * int(match.group(1)))

    def player_orgasmed(self, match):
        return self.toys.vibrate(60, 100)

    def player_edged(self, match):
        return self.toys.vibrate(60, 10)

    def player_sit(self, match):
        return self.toys.vibrate(5, 10)

    def on_hit(self, match):
        (power_attack, bash_attack, sneak_attack, hit_blocked, health, health_max, magicka, magicka_max, stamina, stamina_max) = match.groups()
        # Booleans are either 'TRUE' or 'False'.
        # AV's are a float
        
        # Start with an initial strength of 0.
        # Being hit sets strength 6. 47 of the potential strength is from being power attacked, the other 47 is from remaining health.
        strength = 6

        # If we got hit by a power attack, minimum strength is 25
        if power_attack == 'TRUE':
            strength = 25
        
        strength += 69 -(69 * (float(health) / float(health_max)))

        # If we blocked an attack, reduce strength by 10%
        if hit_blocked == 'TRUE':
            strength = 5

        return self.toys.vibrate(1, int(strength))
        
    def stop_vibrate(self, match):
        return self.toys.stop()
    
    def toys_vibrate(self, match):
        orientation = match.group(1) # left/right, unused for now
        return self.toys.vibrate(int(match.group(3)), int(match.group(2)))

    def sex_start(self, match):
        info("Sex_start")
        self.sex_stage = 0
        return 
    
    def sex_stage_start(self, match):
        # In case sex_start gets missed somehow
        if self.sex_stage == None:
            self.sex_stage = 0

        self.sex_stage += 1
        info("Sex_stage_start: {}".format(str(self.sex_stage)))
        # For stages 1-5, go from strength 20-100. Consider it a process of warming up or sensitization ;)
        return self.toys.vibrate(300, min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER))

    def sex_end(self, match):
        info("Sex_end")
        self.sex_stage = None
        return self.toys.stop()

    def parse_log(self):
        stamp = os.stat(self.filename).st_mtime
        ret = None
        if stamp != self._cached_stamp:
            try:
                self._cached_stamp = stamp
                fd = open(self.filename, 'r')
                fd.seek(self.file_pointer, 0)
                while True:
                    line = fd.readline()
                    if not line:
                        break
                    line = line.strip('\n')
                    print(line)
                    # Process hooks
                    try:
                        for reg in self.hooks.keys():
                            match = reg.match(line)
                            if match:
                                ret = self.hooks[reg](match)
                                break
                    except Exception as e:
                        fail("Encountered exception while executing hooks: {}".format(str(e)))
            except Exception as e:
                self._set_eof(fd)
                fd.close()
                raise e
            self._set_eof(fd)
            fd.close()
        return ret


# Run a task and wait for the result.
async def run_task(foo, run_async=False):
    if isinstance(foo, list):
        for item in foo:
            await run_task(item, run_async)
        return
    if isinstance(foo, types.CoroutineType):
        if run_async:
            asyncio.create_task(foo)
        else:
            await foo
    else:
        # No need to do anything if the task was not async.
        return

ssi = SkyrimScriptInterface(toy_type=TOY_TYPE, token=CHASTER_TOKEN)

async def main():
    try:
        ssi.setup()
        await run_task(ssi.toys.connect())
        await run_task(ssi.toys.vibrate(2, 10))
        await asyncio.sleep(2)
        await run_task(ssi.toys.stop())
        throttle = 0
        while True:
            await asyncio.sleep(0.1)
            try:
                if throttle >= 10:
                    throttle = 0
                    await run_task(ssi.toys.check_in())
                await run_task(ssi.parse_log(), run_async=True)
            except FatalException as e:
                fail("Caught an unrecoverable error: " + str(e))
                raise e
            except Exception as e:
                fail("Unhandled Exception ({}): {}".format(type(e), str(e)))
            throttle += 1
    # Make sure toys shutdown cleanly incase anything fatal happens.
    except Exception as e:
        info("Shutting down...")
        await run_task(ssi.shutdown())
        success("Goodbye!")
        raise e

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        info("Shutting down...")
        loop.run_until_complete(run_task(ssi.shutdown()))
        success("Goodbye!")
    


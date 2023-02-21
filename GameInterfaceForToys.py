import asyncio
import io
import os
import random
import re
import time
import types
import sys
import importlib
import yaml
import traceback
import math
import copy

from common.constants import *
from common.util import *
import settings
from toys.base import FEATURE_VIBRATOR, FEATURE_ESTIM
from events.eventloader import EventLoader
import toys.chastity.chaster.chaster
import PySimpleGUI as sg

MAX_VIBRATE_STRENGTH = 100

config_fields = {
    'Log Path': 'LOG_PATH',
    'Is the OS Windows?': 'IS_WINDOWS',
    'Character Name': 'CHARACTER_NAME',
    'Toy Type': 'TOY_TYPE',
    'Devious Devices Vib Multiplier': 'DD_VIB_MULT',
    'Warn On Stack Dump': 'WARN_ON_STACK_DUMP',
    'Warn On Stack Dump SOUND': 'WARN_ON_STACK_DUMP_SOUND',
    'Buttplug.io Strength Max': 'BUTTPLUG_STRENGTH_MAX',
    'Buttplug.io Server Address': 'BUTTPLUG_SERVER_ADDRESS',
    'Chaster Enabled': 'CHASTER_ENABLED',
    'Chaster Token': 'CHASTER_TOKEN',
    'Chaster Refresh Token': 'CHASTER_REFRESH_TOKEN',
    'Chaster Lock Name': 'LOCK_NAME',
    'Chaster Defeat Minimum Time to Add': 'CHASTER_DEFEAT_MIN',
    'Chaster Defeat Maximum Time to Add': 'CHASTER_DEFEAT_MAX',
    'Coyote E-Stim UID': 'COYOTE_UID',
    'Coyote E-Stim Multiplier': 'COYOTE_MULTIPLIER',
    'Coyote E-Stim Default Channel': 'COYOTE_DEFAULT_CHANNEL',
    'Coyote Sex Multiplier': 'COYOTE_SEX_MULT',
    'Coyote Plug Multiplier': 'COYOTE_PLUG_MULT',
    'Coyote On-Hit Multiplier': 'COYOTE_ON_HIT_MULT',
    'Coyote Minimum Power (0-768)': 'COYOTE_MIN_POWER',
    'Coyote Maximum Power (0-768)': 'COYOTE_MAX_POWER',
    'Lovense Host': 'LOVENSE_HOST',
    'Lovense Strength Max': 'LOVENSE_STRENGTH_SCALE',
    'Lovense Use New API': 'LOVENSE_USE_NEW_API',
    'Print Log Lines': 'PRINT_LOG_LINES',
    'Window Update Frequency': 'WINDOW_UPDATE_FREQUENCY',    
}


on_hit_patterns = {
    "bow": "arrow",
    "axe": "axe",
    "hammer": "blunt",
    "mace": "blunt",
    "fist": "unarmed",
    "unarmed": "unarmed",
    "sword": "blade",
    "dagger": "blade",
    "knife": "blade",
    "spear": "blade"
}

sex_animation_patterns = {


}

def conditional_import(moduleName):
    if moduleName not in sys.modules:
        return __import__(moduleName)

class ToyInterface(object):
    def shutdown(self):
        ret = []
        for toy in self.interface:
            ret += [toy.shutdown()]
        return ret
    
    def __init__(self, toy_type):
        tmp = []
        for toy in toy_type:
            if toy == TOY_LOVENSE:
                from toys.vibrators.lovense.lovense import LovenseInterface
                tmp += [LovenseInterface()]
            elif toy == TOY_XBOXCONTROLLER:
                from toys.vibrators.xbox_controller.xbox_controller import XboxControllerInterface
                tmp += [XboxControllerInterface()]
            elif toy == TOY_BUTTPLUG:
                from toys.vibrators.buttplugio.buttplug import ButtplugInterface
                tmp += [ButtplugInterface()]
            elif toy == TOY_COYOTE:
                from toys.estim.coyote.dg_interface import CoyoteInterface
                tmp += [CoyoteInterface(device_uid=settings.COYOTE_UID,
                                                 power_multiplier=settings.COYOTE_MULTIPLIER,
                                                 default_channel=settings.COYOTE_DEFAULT_CHANNEL,
                                                 safe_mode=settings.COYOTE_SAFE_MODE)]  # See implementation for parameter details
            elif toy == TOY_KIZUNA:
                from toys.vibrators.kizuna.kizuna import KizunaInterface
                tmp += [KizunaInterface()]
            elif toy == TOY_EDGEOMATIC:
                from toys.vibrators.maustec.edgeomatic3000 import EdgeomaticInterface
                tmp += [EdgeomaticInterface()]
            else:
                raise FatalException("Unsupported toy type!")
        self.vibrators = list(filter(lambda x: FEATURE_VIBRATOR in x.properties['features'], tmp))
        self.estim = list(filter(lambda x: FEATURE_ESTIM in x.properties['features'], tmp))
        self.interface = self.vibrators + self.estim
        self.available_toys = {}
        
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
    
    def vibrate(self, duration, strength, pattern="", event=None, vibrate_only=False):
        info("Toy Vibrate - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        if strength > 100:
            strength = 100
        toys = self.find_toys_for_event(event)
        if len(toys) == 0 or vibrate_only:
            interface = self.vibrators
        else:
            interface = self.interface
        # Event is disabled
        if event is not None and len(toys) == 0:
            info("Toy Vibrate - No toys for event {} are enabled.".format(event.name))
            return
        return self._do_action(interface, {"plus": False, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys})

    def vibrate_plus(self, duration, strength, pattern="", event=None, vibrate_only=False):
        strength = math.ceil(strength)
        info("Toy Vibrate+ - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        if strength > 100:
            strength = 100
        toys = self.find_toys_for_event(event)
        if len(toys) == 0 or vibrate_only:
            interface = self.vibrators
        else:
            interface = self.interface
        # Event is disabled
        if event is not None and len(toys) == 0:
            info("Toy Vibrate+ - No toys for event {} are enabled.".format(event.name))
            return
        return self._do_action(interface, {"plus": True, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys})

    def shock(self, duration, strength, pattern="", event=None, shock_only=False):
        strength = math.ceil(strength)
        if strength > 100:
            strength = 100
        toys = self.find_toys_for_event(event)
        if len(toys) == 0 or shock_only:
            interface = self.estim
        else:
            interface = self.interface
        # Event is disabled
        if event is not None and len(toys) == 0:
            info("Toy Shock - No toys for event {} are enabled.".format(event.name))
            return
        info("Toy Shock - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        return self._do_action(interface, {"plus": False, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys})

    def find_toys_for_event(self, event):
        if event is None:
            return []
        return [self.available_toys[toy] for toy in self.toy_event_map[event.name] if self.available_toys[toy]['enabled']]
    
    def _do_action(self, interfaces, params):
        ret = []
        toys = params['toys']
        for interface in interfaces:
            tmp_params = copy.copy(params)
            if len(toys) > 0:
                # Filter toys to only ones supported by target interface
                tmp_params['toys'] = [toy for toy in tmp_params['toys'] if interface.properties['name'] == toy['interface']]
                if len(tmp_params['toys']) > 0:
                    info("Invoking the following devices:")
                    for toy in tmp_params['toys']:
                        info(toy)
                    ret += [interface.action(tmp_params)]
            else:
                info("Invoking all devices in interface {}".format(interface.properties['name']))
                ret += [interface.action(params)]
        return ret

    async def get_toys(self):
        previous_toys = self.available_toys
        self.available_toys = {}
        for toy in self.interface:
            self.available_toys = {**self.available_toys,  **await run_task(toy.get_toys())}
            # self.available_toys = {**self.available_toys, **toy.get_toys()}
        success("Reloaded toys. Currently available toys:")
        for k, v in previous_toys.items():
            if k not in self.available_toys:
                self.available_toys[k] = v
                self.available_toys[k]['enabled'] = False
        for k, v in self.available_toys.items():
            info("  {} ({}) - battery {}%: {}".format(k, v['id'], v['battery'], (v['enabled'] and 'Enabled' or 'Disabled')))
        return self.available_toys
            
    def stop(self):
        info("Toy Vibrate - stop")
        ret = []
        for toy in self.interface:
            ret += [toy.stop()]
        return ret


class SkyrimScriptInterface(object):
    SEX_STAGE_STRENGTH_MULTIPLIER = 20

    def shutdown(self):
        return self.toys.shutdown()

    def __init__(self, toy_type=TOY_LOVENSE):
        self._cached_stamp = 0
        self.filename = settings.LOG_PATH
        self.file_pointer = 0
        self.toys = ToyInterface(toy_type)
        self.sex_stage = None
        self.dd_vibrating = False

    def _chaster_spin_wheel(self, match, event):
        return self.chaster.spin_wheel()

    def generic_chaster_add_time(self, match, event):
        params = event.params
        if 'TOTAL_TIME' in params:
            duration = params['TOTAL_TIME']
        elif 'MIN_TIME' and 'MAX_TIME' in params:
            duration = random.randint(int(params['MIN_TIME']), int(params['MAX_TIME']))
        else:
            fail("Malformed event - could not determine chastity duration")
            return
        self.chaster.update_time(duration)

    def player_defeated(self, match, event):
        self.chaster.spin_wheel()
        self.chaster.update_time(random.randint(settings.CHASTER_DEFEAT_MIN, settings.CHASTER_DEFEAT_MAX))


    def _parse_param(self, match, param):
        if '$' in param:
            index = param[1]
            if not index.isnumeric():
                warn("Found non-number index for generic event.")
                return param
            return match.group(int(index))
        else:
            return param
        
    def _parse_generic_params(self, match, params):
        if 'duration' in params:
            duration = int(self._parse_param(match, params['duration']))
        elif 'min_duration' in params and 'max_duration' in params:
            duration = random.randint(int(self._parse_param(match, params['min_duration'])), int(self._parse_param(match, params['max_duration'])))
        else:
            fail("Malformed event - Could not determine duration.")
            return
        if 'strength' in params:
            strength = int(self._parse_param(match, params['strength']))
        elif 'min_strength' in params and 'max_strength' in params:
            strength = random.randint(int(self._parse_param(match, params['min_strength'])), int(self._parse_param(match, params['max_strength'])))
        else:
            fail("Malformed event - could not determine strength.")
            return
        pattern = "pattern" in params and params['pattern'] or ""
        pattern = self._parse_param(match, pattern)
        return (duration, strength, pattern)
    
    def generic_random_vibrate(self, match, event):
        (duration, strength, pattern) = self._parse_generic_params(match, event.params)
        if not duration or not strength:
            return
        print("Generic_random_vibrate({}, {}, {}): {}".format(duration, strength, pattern, event.params))
        return self.toys.vibrate(duration, strength, pattern, event)

    def generic_random_shock(self, match, event):
        (duration, strength, pattern) = self._parse_generic_params(match, event.params)
        if not duration or not strength:
            return
        return self.toys.shock(duration, strength, pattern, event)
    
    def setup(self):
        try: 
            fd = open(self.filename, 'r', encoding='utf8')
            self._set_eof(fd)
            fd.close()
        except FileNotFoundError:
            fail("Could not open {} for reading - file does not exist.".format(self.filename))
        self.event_loader = EventLoader(self)
        
        if settings.CHASTER_ENABLED:
            from toys.chastity.chaster.chaster import ChasterInterface
            self.chaster = ChasterInterface(settings.LOCK_NAME, self.toys)
            self.chaster.setup()
        return self.load_toy_list()

    def on_animation_event(self, match, event):
        if self.dd_vibrating:
            info("Not processing on_animation_event - Already vibrating")
            return

        akSource = match.group(1)
        wornVagPlug = (match.group(2) == "TRUE")
        wornAnalPlug = (match.group(3) == "TRUE")
        wornVagPiercing = (match.group(4) == "TRUE")
        wornNipplePiercing = (match.group(5) == "TRUE") # Not currently supported
        moving = (akSource == "FootLeft" or akSource == "FootRight")
        sprinting = (akSource == "FootSprintLeft" or akSource == "FootSprintRight" or akSource == "tailSprint")
        jumping = (akSource == "JumpDown")
        pattern = ""

        if not wornVagPlug and not wornAnalPlug and not wornVagPiercing:
            return
        strength = 0
        if wornVagPlug:
            strength += 10
        if wornAnalPlug:
            strength += 5
        if wornVagPiercing:
            strength += 5
        if moving:
            strength *= 1
            pattern = "animation_walking;scale_intensity;interval=400"
        if sprinting:
            strength *= 2
            pattern = "animation_sprinting;scale_intensity;interval=200"
        if jumping:
            strength *= 2
            pattern = "animation_jumping;scale_intensity;interval=150"
        if strength > 0:
            return self.toys.vibrate(2, strength, pattern, event)
        
    def dd_event(self, match, event):
        # Processing [Nipple Piercings]
        return self.toys.vibrate(random.randint(2, 30), 10, event=event)
        
    def stack_overflow(self, match, event):
        if not WARN_ON_STACK_DUMP:
            return
        while(True):
            self.toys.vibrate(1, 100)
            beep()
            time.sleep(2)
            
    def _set_eof(self, fd):
        fd.seek(0, io.SEEK_END)
        self.file_pointer = fd.tell()

    def dd_vibrate(self, duration, strength, event):
        pattern = "vibrator_{}".format(strength)
        info("dd_vibrate(" + str(duration)+", "+ str(strength)+", "+pattern+")")
        ret =  [self.toys.vibrate_plus(duration * int(settings.DD_VIB_MULT), 20 * strength, pattern=pattern, event=event, vibrate_only=True)]
        ret.append(self.toys.shock(duration * int(settings.DD_VIB_MULT), math.ceil((20 * strength) * float(settings.COYOTE_PLUG_MULT)), pattern, event=event, shock_only=True))
        return ret
    
    def vibrate(self, match, event):
        self.dd_vibrating = True
        duration = int(match.group(2))
        strength = int(match.group(1))
        return self.dd_vibrate(duration, strength, event=event)

    def dd_anim(self, match, event):
        # Don't override existing dd vibrations
        if self.dd_vibrating:
            info("Not starting new vibration - already in dd vibrate")
            return
        self.toys.vibrate(60, 50, "dd_struggle", event),

    def dd_anim_stop(self, match, event):
        # Don't interrupt existing dd vibrations
        if self.dd_vibrating:
            info("Not stopping vibration - already in dd vibrate")
            return
        self.toys.stop()
        
    def fallout_dd_vibrate(self, match, event):
        strength = 50
        strText = match.group(1)
        if strText == "very weak":
            strength = 10
        elif strText == "weak":
            strength = 30
        elif strText == "strong":
            strength = 70
        elif strText == "very strong":
            strength = 100
        return self.toys.vibrate_plus(120, strength, event=event)

    def player_orgasmed(self, match, event):
        return self.toys.vibrate_plus(60, 100, event=event)

    def player_edged(self, match, event):
        return self.toys.vibrate_plus(60, 10, event=event)

    def player_sit(self, match, event):
        return self.toys.vibrate(5, 10, event=event)

    def on_hit(self, match, event):
        (source, power_attack, bash_attack, sneak_attack, hit_blocked, health, health_max, magicka, magicka_max, stamina, stamina_max) = match.groups()
        # Booleans are either 'TRUE' or 'False'.
        # AV's are a float
        
        # Start with an initial strength of 0.
        # Being hit sets strength 6. 47 of the potential strength is from being power attacked, the other 47 is from remaining health.
        
        source = source.lower()
        if source == "": # Animals and the like have an empty source name
            source = "unarmed"
        if source == "woven power":
            # Do nothing for self-damage from spellsiphon
            return
        
        strength = 6

        
        # If we blocked the attack, do nothing
        if hit_blocked == 'TRUE':
            return

        # If we got hit by a power attack, minimum strength is 25
        if power_attack == 'TRUE':
            strength = 25
        
        strength += 69 -(69 * (float(health) / float(health_max)))

        pattern = ""
        for k, v in on_hit_patterns.items():
            if k in source:
                pattern = v
                break
        if len(self.toys.estim) == 0:
            return self.toys.vibrate(2, strength, event=event)
        else:
            return self.toys.shock(1, math.ceil(int(strength) * float(settings.COYOTE_ON_HIT_MULT)), pattern, event)
        
    def stop_vibrate(self, match, event):
        self.dd_vibrating = False
        return self.toys.stop()
    
    def toys_vibrate(self, match, event):
        orientation = match.group(1) # left/right, unused for now
        return self.toys.vibrate(int(match.group(3)), int(match.group(2)), event=event)

    def sex_start_simple(self, match, event):
        return self.toys.vibrate_plus(300, MAX_VIBRATE_STRENGTH, "sex_simple", event=event)
    
    def sex_start(self, match, event):
        info("Sex_start")
        self.sex_animation = "untyped_sex"
        self.sex_stage = 0
        return 
    
    def sex_stage_start(self, match, event):
        # This could go up too fast if there are multiple scenes happening, but shouldn't move if
        # the player is involved in none of them.
        if self.sex_stage is not None:
            self.sex_stage += 1
            info("Sex_stage_start: {}".format(str(self.sex_stage)))
            # For stages 1-5, go from strength 20-100. Consider it a process of warming up or sensitization ;)
            return [self.toys.vibrate_plus(300, min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER), pattern=self.sex_animation, event=event, vibrate_only=True),
                    self.toys.shock(300, math.ceil(min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER) * float(settings.COYOTE_SEX_MULT)), pattern=self.sex_animation, event=event, shock_only=True)]

    def sex_end(self, match, event):
        info("Sex_end")
        self.sex_stage = None
        self.sex_animation = "untyped_sex"
        return self.toys.stop()

    def sex_animation_set(self, match, event):
        # This only fires if the player is in the scene, so no need for further filtering
        boobjob = match.group(1) == "TRUE"
        vaginal = match.group(2) == "TRUE"
        fisting = match.group(3) == "TRUE"
        masturbation = match.group(4) == "TRUE"
        anal = match.group(5) == "TRUE"
        oral = match.group(6) == "TRUE"
        if boobjob:
            self.sex_animation = "boobjob"
        if oral:
            self.sex_animation = "oral"
        if vaginal:
            self.sex_animation = "vaginal"
        if anal:
            self.sex_animation = "anal"
        # Ordered last, so that these override vaginal/anal/etc
        if fisting:
            self.sex_animation = "fisting"
        if masturbation:
            self.sex_animation = "masturbation"
        success("Set sex animation type to " + self.sex_animation)

    def load_toy_event_map(self):
        try:
            with io.open('toy-event-map.yaml', 'r', encoding='utf8') as stream:
                info('Loading Toy Event Mapping...')
                self.toys.toy_event_map = yaml.safe_load(stream)
                for event in self.event_loader.events:
                    if event.name not in self.toys.toy_event_map:
                        self.toys.toy_event_map[event.name] = []
                success('Done.')
        except FileNotFoundError:
            fail("Could not load toy - event mapping file - using defaults.")
            self.toys.toy_event_map = {}
            for event in self.event_loader.events:
                self.toys.toy_event_map[event.name] = []
            self.save_toy_event_map()

            
    def save_toy_event_map(self): 
        info('Saving Toy Event Mapping...')
        with io.open('toy-event-map.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self.toys.toy_event_map, outfile, default_flow_style=False, allow_unicode=True)
        success('Done.')

    def load_toy_list(self):
        try:
            with io.open('toys.yaml', 'r', encoding='utf8') as stream:
                info('Loading list of Toys...')
                self.toys.available_toys = yaml.safe_load(stream)
                for k, v in self.toys.available_toys.items():
                    # Toys we saw previously may not be in this session. Start disabled.
                    self.toys.available_toys[k]['enabled'] = False
                success('Done.')
        except FileNotFoundError:
            fail("Could not load list of toys - file does not exist. If you haven't set up any toys yet, this is normal.")
        # Fetch updated list of toys
        return self.toys.get_toys()

            
    def save_toy_list(self): 
        info('Saving List of Toys...')
        with io.open('toys.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self.toys.available_toys, outfile, default_flow_style=False, allow_unicode=True)
        success('Done.')

    
    def parse_log(self):
        stamp = os.stat(self.filename).st_mtime
        ret = None
        if stamp != self._cached_stamp:
            try:
                self._cached_stamp = stamp
                fd = open(self.filename, 'r', encoding='utf8')
                fd.seek(self.file_pointer, 0)
                while True:
                    line = fd.readline()
                    if not line:
                        break
                    line = line.strip('\n')
                    if settings.PRINT_LOG_LINES:
                        print(line)
                    # Process hooks
                    try:
                        for event in self.event_loader.events:
                            match = event.regex.match(line)
                            if match:
                                ret = event.function(match, event)
                                break
                    except Exception as e:
                        fail("Encountered exception while executing hooks: {}".format(str(e)))
                        traceback.print_exception(e)
            except Exception as e:
                self._set_eof(fd)
                fd.close()
                raise e
            self._set_eof(fd)
            fd.close()
        return ret


# Run a task and wait for the result.
async def run_task(foo, run_async=False, window=False):
    if isinstance(foo, list):
        ret = []
        for item in foo:
            ret += [await run_task(item, run_async)]
            if window:
                window.Refresh()
        return ret
    if isinstance(foo, types.CoroutineType):
        if run_async:
            asyncio.create_task(foo)
        else:
            return await foo
            if window:
                window.Refresh()
    else:
        # No need to do anything if the task was not async.
        return foo


async def test_plugs(window, ssi):
    for i in range(1, 6):
        await run_task(ssi.dd_vibrate(2, i, event=None), run_async=True)
        window.Refresh()
        timeout = 0
        await asyncio.sleep(4)
    await run_task(ssi.toys.stop())

async def test_sex(window, ssi):
    ssi.sex_start(False, event=None)
    ssi.sex_animation = random.choice(["boobjob", "vaginal", "fisting", "masturbation", "anal", "oral"])
    for i in range(0, 5):
        await run_task(ssi.sex_stage_start(False, event=None), run_async=True, window=window)
        window.Refresh()
        await asyncio.sleep(5)
    await run_task(ssi.sex_end(False, event=None))


async def main():
    try:
        # Set up GUI
        sg.theme('DarkGrey12')
        buttonColumn = [
            [sg.Text("Test Functions")],
            [sg.Button(GUI_TEST_VIBRATE)],
             [sg.Button(GUI_TEST_SHOCK)],
             [sg.Button(GUI_TEST_SEX)],
             [sg.Button(GUI_TEST_PLUG_VIBRATE)],
             [sg.Text("Configuration")],
            [sg.Button(GUI_OPEN_CONFIG)],
            [sg.Button(GUI_OPEN_TOY_CONFIG)],
            [sg.Button(GUI_REFRESH_TOYS)]
        ]
        if settings.CHASTER_ENABLED:
            buttonColumn.append([sg.Text("Chaster")])
            buttonColumn.append([sg.Button(GUI_CHASTER_SPIN_WHEEL)])
            buttonColumn.append([sg.Button(GUI_CHASTER_AUTHENTICATE)])
        layout = [
            [sg.Column(buttonColumn),
             sg.Column([[sg.Output(size=(120,60), background_color='black', text_color='white')]])
        ]]
        window = sg.Window('Game Interface For Toys', layout)
        window.read(timeout=1)
        load_config()
        try:
            await run_task(ssi.toys.connect())
            await run_task(ssi.setup())
            ssi.load_toy_event_map()
            ssi.save_toy_list()
        except Exception as e:
            traceback.print_exception(e)
            fail("Setup failed - please fix the above error and reload the window.")
        window.Refresh()

        throttle = 0
        window_last_read = time.time()
        while True:
            throttle += 1
            await asyncio.sleep(0.01)
            if time.time() - window_last_read  > float(settings.WINDOW_UPDATE_FREQUENCY):
                event, values = window.read(timeout=10) # Timeout after 10ms instead of sleeping
                window_last_read = time.time()
            else:
                event, values = (False, False)
            try:
                if event == sg.WIN_CLOSED:
                    await run_task(ssi.shutdown(), window=window)
                    window.close()
                    raise FatalException("Exiting")
                if event == GUI_TEST_VIBRATE:
                    await run_task(ssi.toys.vibrate(5, 10, "random"), run_async=True)
                if event == GUI_TEST_PLUG_VIBRATE:
                    await run_task(test_plugs(window, ssi), run_async=True)
                if event == GUI_TEST_SEX:
                    await run_task(test_sex(window, ssi), run_async=True)
                if event == GUI_TEST_SHOCK:
                    await run_task(ssi.toys.shock(2, 10, "random"), run_async=True)
                if event == GUI_CHASTER_SPIN_WHEEL:
                    await run_task(ssi._chaster_spin_wheel(False, event=None), run_async=True)
                if event == GUI_CHASTER_AUTHENTICATE:
                    info("Authenticating with chaster... Please login in the browser.")
                    await run_task(ssi.chaster.authenticate(window))
                    timeout = 0
                    while timeout < 60 and not toys.chastity.chaster.chaster.callback_hit:
                        info("Waiting for response...")
                        window.Refresh()
                        time.sleep(1)
                        timeout += 1
                    if timeout >= 60:
                        fail("Failed to authenticate with Chaster.")
                    else:
                        ssi.chaster.enabled = True
                        ssi.chaster.setup()
                        save_config()
                if event == GUI_REFRESH_TOYS:
                    await run_task(ssi.toys.get_toys(), run_async=True)
                if event == GUI_OPEN_TOY_CONFIG:
                    while True:
                        try:
                            if open_toy_event_modal(ssi): # Returns true if done
                                break
                        except ReloadException as e:
                            raise e
                        except Exception as e:
                            fail("Error while saving toy-event map ({}): {}".format(type(e), str(e)))
                            traceback.print_exception(e)
                            break
                if event == GUI_OPEN_CONFIG:
                    try:
                        open_config_modal()
                    except ReloadException as e:
                        raise e
                    except Exception as e:
                        fail("Error while saving config ({}): {}".format(type(e), str(e)))
                        traceback.print_exception(e)
                if throttle >= 0:
                    throttle = 0
                    await run_task(ssi.toys.check_in())
                await run_task(ssi.parse_log(), run_async=True)
            except FatalException as e:
                fail("Caught an unrecoverable error: " + str(e))
                raise e
            except FileNotFoundError as e:
                # User likely hasn't set up the log path.
                if throttle > 100:
                    fail("Could not open {} reading - File not found".format(str(e)))
            except Exception as e:
                fail("Unhandled Exception ({}): {}".format(type(e), str(e)))
                traceback.print_exception(e)
    # Make sure toys shutdown cleanly incase anything fatal happens.
    except Exception as e:
        info("Shutting down...")
        window.close()
        await run_task(ssi.shutdown())
        success("Goodbye!")
        raise e

def open_toy_event_modal(ssi):
    toy_layout = []
    toy_layout.append([sg.Text('Event Name', size=(25, 1))])
    for toy in ssi.toys.available_toys:
        toy_layout[0].append(sg.Text(toy, size=(15, 1)))
    i = 1
    last_origin = None
    for event in ssi.event_loader.events:
        if last_origin != event.origin:
            toy_layout.append([sg.HorizontalSeparator(), sg.Text(event.origin), sg.HorizontalSeparator()])
            last_origin = event.origin
            i += 1
        toy_layout.append([sg.Text(event.shortname, size=(25, 1))])
        for toy in ssi.toys.available_toys:
            toy_layout[i].append(sg.Checkbox("", size=(15, 1), key="{}:{}".format(event.name, toy), default=toy in ssi.toys.toy_event_map[event.name]))
        i += 1
    toy_layout.append([sg.Button(GUI_CONFIG_SAVE), sg.Button(GUI_CONFIG_EXIT), sg.Button(GUI_CONFIG_ENABLE_ALL), sg.Button(GUI_CONFIG_DISABLE_ALL)])
    toy_window = sg.Window('GIFT Toy:Event Map Configuration', [[sg.Column(toy_layout, scrollable=True)]], modal=True)
    while True:
        event, values = toy_window.read()
        if event == GUI_CONFIG_EXIT or event == sg.WIN_CLOSED:
            info('Exited toy-event configuration menu without saving.')
            break
        if event == GUI_CONFIG_ENABLE_ALL:
            for event in ssi.event_loader.events:
                for toy in ssi.toys.available_toys:
                    ssi.toys.toy_event_map[event.name].append(toy)
            toy_window.close()
            return False
        if event == GUI_CONFIG_DISABLE_ALL:
            for event in ssi.event_loader.events:
                for toy in ssi.toys.available_toys:
                    ssi.toys.toy_event_map[event.name] = []
            toy_window.close()
            return False
        if event == GUI_CONFIG_SAVE:
            for event in ssi.event_loader.events:
                ssi.toys.toy_event_map[event.name] = []
                for toy in ssi.toys.available_toys:
                    if values['{}:{}'.format(event.name, toy)]:
                        ssi.toys.toy_event_map[event.name].append(toy)
            ssi.save_toy_event_map()
            ssi.load_toy_event_map()
            toy_window.close()
            return True
    toy_window.close()
    return True

def open_config_modal():
    config_layout = []
    for k, v in config_fields.items():
        if v == 'LOG_PATH':
            config_layout.append([sg.Text('Path to Log File'), sg.FileBrowse('Select Log File', key=v)])
            config_layout.append([sg.Text('Old Log File Path: {}'.format(settings.LOG_PATH))])
        elif v == 'IS_WINDOWS':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.IS_WINDOWS)])
        elif v == 'CHASTER_ENABLED':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.CHASTER_ENABLED)])
        elif v == 'TOY_TYPE':
            config_layout.append([sg.Text('Supported Toys:'), sg.Checkbox(TOY_LOVENSE, key=TOY_LOVENSE, default=TOY_LOVENSE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_XBOXCONTROLLER, key=TOY_XBOXCONTROLLER, default=TOY_XBOXCONTROLLER in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_BUTTPLUG, key=TOY_BUTTPLUG, default=TOY_BUTTPLUG in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_COYOTE, key=TOY_COYOTE, default=TOY_COYOTE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_KIZUNA, key=TOY_KIZUNA, default=TOY_KIZUNA in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_EDGEOMATIC, key=TOY_EDGEOMATIC, default=TOY_EDGEOMATIC in settings.TOY_TYPE)
                                  ])
        elif v == 'LOVENSE_USE_NEW_API':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.LOVENSE_USE_NEW_API)])
        elif v == 'WARN_ON_STACK_DUMP':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.WARN_ON_STACK_DUMP),
                                sg.Radio("speaker","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=settings.WARN_ON_STACK_DUMP_SOUND),
                                sg.Radio("buzzer","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=not settings.WARN_ON_STACK_DUMP_SOUND)])
        elif v == 'WARN_ON_STACK_DUMP_SOUND':
            pass
        elif v == 'PRINT_LOG_LINES':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.PRINT_LOG_LINES)])
        else:
            config_layout.append([sg.Text(k), sg.Input(getattr(settings, v), size=(60, 1), key=v)])
    config_layout.append([sg.Button(GUI_CONFIG_SAVE), sg.Button(GUI_CONFIG_EXIT)])
    config_window = sg.Window('GIFT Configuration', config_layout, modal=True)
    while True:
        event, values = config_window.read()
        if event == GUI_CONFIG_EXIT or event == sg.WIN_CLOSED:
            info('Exited configuration menu without saving.')
            break
        if event == GUI_CONFIG_SAVE:
            for x in config_fields.values():
                if x == 'LOG_PATH':
                    if len(values['LOG_PATH']) > 0:
                        settings.LOG_PATH = values['LOG_PATH']
                    else:
                        info('Log path did not change.')
                elif x == 'TOY_TYPE':
                    toys = []
                    if values[TOY_LOVENSE] == True:
                        toys += [TOY_LOVENSE]
                    if values[TOY_XBOXCONTROLLER] == True:
                        toys += [TOY_XBOXCONTROLLER]
                    if values[TOY_BUTTPLUG] == True:
                        toys += [TOY_BUTTPLUG]
                    if values[TOY_COYOTE] == True:
                        toys += [TOY_COYOTE]
                    if values[TOY_KIZUNA] == True:
                        toys += [TOY_KIZUNA]
                    if values[TOY_EDGEOMATIC] == True:
                        toys += [TOY_EDGEOMATIC]
                    settings.TOY_TYPE = toys
                else:
                    setattr(settings, x, values[x])
            save_config()
            load_config()
            config_window.close()
            raise ReloadException()
    config_window.close()


def save_config():
    info('Saving Config...')
    with io.open('settings.yaml', 'w', encoding='utf8') as outfile:
        data = {}
        for x in config_fields.values():
            data[x] = getattr(settings, x)
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
        success('Done.')


def load_config():
    def safe_load_config(key):
        try:
            setattr(settings, key, data[key])
            info("{} = {}".format(key, data[key]))
        except:
            fail("No config value found for {}".format(key))
    try:
        with io.open('settings.yaml', 'r', encoding='utf8') as stream:
            info('Loading Config...')
            data = yaml.safe_load(stream)
            for x in config_fields.values():
                safe_load_config(x)
            success('Done.')
    except FileNotFoundError:
        fail("Could not load configuration file - using defaults.")
        save_config()

if __name__ == "__main__":
    load_config()
    loop = asyncio.get_event_loop()
    while True:
        ssi = SkyrimScriptInterface(toy_type=settings.TOY_TYPE)
        try:
            loop.run_until_complete(main())
        except ReloadException as e:
            # Reinitialize app on reload exception
            continue
        except FatalException as e:
            break
        except KeyboardInterrupt as e:
            info("Shutting down...")
            loop.run_until_complete(run_task(ssi.shutdown()))
            success("Goodbye!")
            break

    


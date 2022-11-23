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

from common.constants import *
from common.util import *
import settings
from toys.base import FEATURE_VIBRATOR, FEATURE_ESTIM

import PySimpleGUI as sg

MAX_VIBRATE_STRENGTH = 100

config_fields = {
    'Log Path': 'LOG_PATH',
    'Character Name': 'CHARACTER_NAME',
    'Toy Type': 'TOY_TYPE',
    'Devious Devices Vib Multiplier': 'DD_VIB_MULT',
    'Warn On Stack Dump': 'WARN_ON_STACK_DUMP',
    'Buttplug.io Strength Max': 'BUTTPLUG_STRENGTH_MAX',
    'Buttplug.io Server Address': 'BUTTPLUG_SERVER_ADDRESS',
    'Chaster Dev Token': 'CHASTER_TOKEN',
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
    'Lovense Host': 'LOVENSE_HOST',
    'Lovense Strength Max': 'LOVENSE_STRENGTH_SCALE',
    'Lovense Use New API': 'LOVENSE_USE_NEW_API'
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

    def vibrate(self, duration, strength, pattern=""):
        info("Toy Vibrate - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        if strength > 100:
            strength = 100
        return self._do_action(self.vibrators, {"plus": False, "duration": duration, "strength": strength, "pattern": pattern})

    def vibrate_plus(self, duration, strength, pattern=""):
        strength = math.ceil(strength)
        info("Toy Vibrate+ - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        if strength > 100:
            strength = 100
        return self._do_action(self.vibrators, {"plus": True, "duration": duration, "strength": strength, "pattern": pattern})

    def shock(self, duration, strength, pattern=""):
        strength = math.ceil(strength)
        if strength > 100:
            strength = 100
        info("Toy Shock - start(duration={}, strength={}, pattern={})".format(duration, strength, pattern))
        return self._do_action(self.estim, {"duration": duration, "strength": strength, "pattern": pattern})

    def _do_action(self, toys, params):
        ret = []
        for toy in toys:
            ret += [toy.action(params)]
        return ret
        
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
        
    def __init__(self, toy_type=TOY_LOVENSE, token=False):
        self._cached_stamp = 0
        self.filename = settings.LOG_PATH
        self.file_pointer = 0
        self.chaster_enabled = (token and token != "")
        self.token = token
        self.toys = ToyInterface(toy_type)
        self.sex_stage = None
        self.dd_vibrating = False

    def _chaster_spin_wheel(self, match):
        return self.chaster.spin_wheel()
    

    def player_defeated(self, match):
        self.chaster.spin_wheel()
        self.chaster.update_time(random.randint(CHASTER_DEFEAT_MIN, CHASTER_DEFEAT_MAX))

    def setup(self):
        try: 
            fd = open(self.filename, 'r')
            self._set_eof(fd)
            fd.close()
        except FileNotFoundError:
            fail("Could not open {} for reading - file does not exist.".format(self.filename))
        sexlab_hooks = {
            # Sexlab Support
            #SEXLAB - ActorAlias[min] SetActor
            re.compile(".+SEXLAB - ActorAlias\[{}\] SetActor.+".format(settings.CHARACTER_NAME.lower()), re.I): self.sex_start,
            re.compile(".+SEXLAB - ActorAlias\[{}\]  - Resetting!+".format(settings.CHARACTER_NAME.lower()), re.I): self.sex_end,
            re.compile(".+SEXLAB - Thread\[[0-9]+\] Event Hook - StageStart$", re.I): self.sex_stage_start,
            re.compile(".+OnSexlabAnimationStart\(boobjob='(.+)', vaginal='(.+)', fisting='(.+)', masturbation='(.+)', anal='(.+)', oral='(.+)'\).*", re.I): self.sex_animation_set
        }
        fallout_hooks = {
            # Fallout 4 AAF Support
            # AAF does not verbosely log, so we must depend on other mods that write log events on these hooks.
            # DD writes a specific log event when an animation involving the player starts, bostion devious helper writes one when it ends.
            # Use the two of these to capture a sex scene.
            # TODO: Write my own plugin that watches for these events.
            re.compile(".+DD: Player in AAF animation.*"): self.sex_start_simple,
            re.compile(".+BDH-INFO - OnAnimationStop.*"): self.sex_end,
            re.compile(".+AFV Report: Player is bleeding out in surrender.*"): self.player_defeated,
            re.compile(".+Your plug gives a painfull shock.+"): lambda m: self.toys.shock(random.randint(1, 5), random.randint(50,65)),
            re.compile(".+Your plug gives multiple painfull shocks.*"): lambda m: self.toys.shock(random.randint(5, 10), random.randint(75,85)),
            re.compile(".+You acidentally bump your .+ plug pumpbulb and it inflates.*"): lambda m: self.toys.vibrate(random.randint(5, 10), 20),
            re.compile(".+You hear your .+ plug pump whirr and inflating.*"): lambda m: self.toys.vibrate(random.randint(10, 20), 40),
            re.compile(".+Your .+ plug moves, sending pleasure trough your body.*"): lambda m: self.toys.vibrate(random.randint(5, 10), 10),
            re.compile(".+Your plugs stops vibrating.*"): lambda m: self.toys.stop(),
            re.compile(".+Your plug sends you into an uncontrollable orgasm.*"): self.player_orgasmed,
            re.compile(".+Your plug stops vibrating just before you can orgasm.*"): self.player_edged,
            re.compile(".+Your .+ plug.* start.* to vibrate ?(.*)"): self.fallout_dd_vibrate,
        }
        chaster_hooks = {}
        if self.chaster_enabled:
            from toys.chastity.chaster.chaster import ChasterInterface
            chaster_hooks = {
                # Defeat integration
                re.compile(".+Defeat: SetFollowers / Scenario.+$"): self._chaster_spin_wheel, # Player was knocked down.
                re.compile(".+Defeat: PostAssault Marker Found.+$"): lambda m: self.chaster.update_time(random.randint(settings.CHASTER_DEFEAT_MIN, settings.CHASTER_DEFEAT_MAX)), # Party was defeated.
                re.compile(".+Defeat: Player victim - End scene, Restored.+$"): self._chaster_spin_wheel, #  Player actually died.
                # Naked Defeat integration
                re.compile(".+NAKED DEFEAT playeraliasquest: OnEnterBleedout\(\).+"): self._chaster_spin_wheel, # Player was knocked down.
                re.compile(".+NAKED DEFEAT playeraliasquest: \(#msg\) All is lost.+"): lambda m: self.chaster.update_time(random.randint(settings.CHASTER_DEFEAT_MIN, settings.CHASTER_DEFEAT_MAX)) # Party was defeated.
            }
        devious_hooks = {
            # Devious Devices Support
            re.compile(".+VibrateEffect.([0-9]+) for ([0-9]+).+"): self.vibrate,
            re.compile(".*\[SkyrimToyInterface\]: OnVibrateStop().*"): self.stop_vibrate,
            re.compile(".*\[SkyrimToyInterface\]: OnDeviceActorOrgasm().*"): self.player_orgasmed,
            re.compile(".*\[SkyrimToyInterface\]: OnDeviceEdgedActor().*"): self.player_edged,
            re.compile(".*\[SkyrimToyInterface\]: OnSitDevious().*"): self.player_sit,
            re.compile(".*StartThirdPersonAnimation\({},(.+)\)".format(settings.CHARACTER_NAME.lower()), re.I): self.dd_anim,
            re.compile(".*EndThirdPersonAnimation\({}.+".format(settings.CHARACTER_NAME.lower()), re.I): self.dd_anim_stop,
            re.compile(".*Processing \[(.+)\].*"): self.dd_event
        }
        toys_hooks = {
            # Toys support
            re.compile(".+\[TOYS\] ControllerShake (Left|Right), ([0-9.]+), ([0-9]+.?[0-9]|.[0-9]+)+"): self.toys_vibrate

        }
        misc_hooks = {
            # Stack Dump Monitoring Support
            re.compile(".*\[SkyrimToyInterface\]: OnHit\(akSource='(.*?)', akProjectile='.*?', abPowerAttack='(TRUE|False)', abBashAttack='(TRUE|False)', abSneakAttack='(TRUE|False)', abHitBlocked='(TRUE|False)'\): \[health='([0-9.]+)\/([0-9.]+)', magicka='([0-9.]+)\/([0-9.]+)', stamina='([0-9.]+)\/([0-9.]+)'\].*"): self.on_hit,
            re.compile("^.+Suspended stack count is over our warning threshold.+"): self.stack_overflow
        }
        self.hooks = {**sexlab_hooks, **chaster_hooks, **devious_hooks, **toys_hooks, **misc_hooks, **fallout_hooks}

        if self.chaster_enabled:
            self.chaster = ChasterInterface(settings.LOCK_NAME, self.token, self.toys)
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
            time.sleep(2)
            
    def _set_eof(self, fd):
        fd.seek(0, io.SEEK_END)
        self.file_pointer = fd.tell()

    def dd_vibrate(self, duration, strength):
        pattern = "vibrator_{}".format(strength)
        info("dd_vibrate(" + str(duration)+", "+ str(strength)+", "+pattern+")")
        ret =  [self.toys.vibrate_plus(duration * int(settings.DD_VIB_MULT), 20 * strength, pattern=pattern)]
        ret.append(self.toys.shock(duration * int(settings.DD_VIB_MULT), math.ceil((20 * strength) * float(settings.COYOTE_PLUG_MULT)), pattern))
        return ret
    
    def vibrate(self, match):
        self.dd_vibrating = True
        duration = int(match.group(2))
        strength = int(match.group(1))
        return self.dd_vibrate(duration, strength)

    def dd_anim(self, match):
        # Don't override existing dd vibrations
        if self.dd_vibrating:
            info("Not starting new vibration - already in dd vibrate")
            return
        self.toys.vibrate(60, 50, "dd_struggle"),

    def dd_anim_stop(self, match):
        # Don't interrupt existing dd vibrations
        if self.dd_vibrating:
            info("Not stopping vibration - already in dd vibrate")
            return
        self.toys.stop()
        
    def fallout_dd_vibrate(self, match):
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
        return self.toys.vibrate_plus(120, strength)

    def player_orgasmed(self, match):
        return self.toys.vibrate_plus(60, 100)

    def player_edged(self, match):
        return self.toys.vibrate_plus(60, 10)

    def player_sit(self, match):
        return self.toys.vibrate(5, 10)

    def on_hit(self, match):
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
            return self.toys.vibrate(2, strength)
        else:
            return self.toys.shock(1, math.ceil(int(strength) * float(settings.COYOTE_ON_HIT_MULT)), pattern)
        
    def stop_vibrate(self, match):
        self.dd_vibrating = False
        return self.toys.stop()
    
    def toys_vibrate(self, match):
        orientation = match.group(1) # left/right, unused for now
        return self.toys.vibrate(int(match.group(3)), int(match.group(2)))

    def sex_start_simple(self, match):
        return self.toys.vibrate_plus(300, MAX_VIBRATE_STRENGTH)
    
    def sex_start(self, match):
        info("Sex_start")
        self.sex_animation = "untyped_sex"
        self.sex_stage = 0
        return 
    
    def sex_stage_start(self, match):
        # This could go up too fast if there are multiple scenes happening, but shouldn't move if
        # the player is involved in none of them.
        if self.sex_stage is not None:
            self.sex_stage += 1
            info("Sex_stage_start: {}".format(str(self.sex_stage)))
            # For stages 1-5, go from strength 20-100. Consider it a process of warming up or sensitization ;)
            return [self.toys.vibrate_plus(300, min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER), pattern=self.sex_animation),
                    self.toys.shock(300, math.ceil(min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER) * float(settings.COYOTE_SEX_MULT)), pattern=self.sex_animation)]

    def sex_end(self, match):
        info("Sex_end")
        self.sex_stage = None
        self.sex_animation = "untyped_sex"
        return self.toys.stop()

    def sex_animation_set(self, match):
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
        for item in foo:
            await run_task(item, run_async)
            if window:
                window.Refresh()
        return
    if isinstance(foo, types.CoroutineType):
        if run_async:
            asyncio.create_task(foo)
        else:
            await foo
            if window:
                window.Refresh()
    else:
        # No need to do anything if the task was not async.
        return


async def test_plugs(window, ssi):
    for i in range(1, 6):
        await run_task(ssi.dd_vibrate(2, i), run_async=True)
        window.Refresh()
        timeout = 0
        await asyncio.sleep(4)
    await run_task(ssi.toys.stop())

async def test_sex(window, ssi):
    ssi.sex_start(False)
    ssi.sex_animation = random.choice(["boobjob", "vaginal", "fisting", "masturbation", "anal", "oral"])
    for i in range(0, 5):
        await run_task(ssi.sex_stage_start(False), run_async=True, window=window)
        window.Refresh()
        await asyncio.sleep(5)
    await run_task(ssi.sex_end(False))


async def main():
    try:
        # Set up GUI
        sg.theme('DarkGrey12')
        buttonColumn = [[sg.Button(GUI_TEST_VIBRATE)],
                        [sg.Button(GUI_TEST_SHOCK)],
                        [sg.Button(GUI_TEST_SEX)],
                        [sg.Button(GUI_TEST_PLUG_VIBRATE)],
                        [sg.Button(GUI_OPEN_CONFIG)]
                        ]
        if ssi.chaster_enabled:
            buttonColumn.append([sg.Button(GUI_CHASTER_SPIN_WHEEL)])
        layout = [
            [sg.Column(buttonColumn),
             sg.Column([[sg.Output(size=(120,60), background_color='black', text_color='white')]])
        ]]
        window = sg.Window('Game Interface For Toys', layout)
        window.read(timeout=1)
        load_config()
        try:
            ssi.setup()
        except Exception as e:
            traceback.print_exception(e)
            fail("Setup failed - please fix the above error and reload the window.")
        await run_task(ssi.toys.connect(), run_async=True)
        window.Refresh()

        throttle = 0
        while True:
            throttle += 1
            await asyncio.sleep(0.01)
            event, values = window.read(timeout=10) # Timeout after 10ms instead of sleeping
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
                    await run_task(ssi._chaster_spin_wheel(False), run_async=True)
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
    
def open_config_modal():
    config_layout = []
    for k, v in config_fields.items():
        if v == 'LOG_PATH':
            config_layout.append([sg.Text('Path to Log File'), sg.FileBrowse('Select Log File', key=v)])
            config_layout.append([sg.Text('Old Log File Path: {}'.format(settings.LOG_PATH))])
        elif v == 'TOY_TYPE':
            config_layout.append([sg.Text('Supported Toys:'), sg.Checkbox(TOY_LOVENSE, key=TOY_LOVENSE, default=TOY_LOVENSE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_BUTTPLUG, key=TOY_BUTTPLUG, default=TOY_BUTTPLUG in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_COYOTE, key=TOY_COYOTE, default=TOY_COYOTE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_KIZUNA, key=TOY_KIZUNA, default=TOY_KIZUNA in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_EDGEOMATIC, key=TOY_EDGEOMATIC, default=TOY_EDGEOMATIC in settings.TOY_TYPE)
                                  ])
        elif v == 'LOVENSE_USE_NEW_API':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.LOVENSE_USE_NEW_API)])
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
                    print(values)
                    if values[TOY_LOVENSE] == True:
                        toys += [TOY_LOVENSE]
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
        with io.open('settings.yaml', 'r') as stream:
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
        ssi = SkyrimScriptInterface(toy_type=settings.TOY_TYPE, token=settings.CHASTER_TOKEN)
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

    


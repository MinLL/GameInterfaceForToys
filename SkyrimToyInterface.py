import asyncio
import io
import os
import random
import re
import time
import types
import sys
import importlib

from common.constants import *
from common.util import *
from settings import *
from toys.base import FEATURE_VIBRATOR, FEATURE_ESTIM

MAX_VIBRATE_STRENGTH = 100

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
                tmp += [CoyoteInterface(device_uid="C1:A9:D8:0C:CB:1D",
                                                 power_multiplier=7.68,
                                                 default_channel="a",
                                                 safe_mode=True)]  # See implementation for parameter details
            elif toy == TOY_KIZUNA:
                from toys.vibrators.kizuna.kizuna import KizunaInterface
                tmp += [KizunaInterface()]
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

    def vibrate(self, duration, strength):
        info("Toy Vibrate - start(duration={}, strength={})".format(duration, strength))
        if strength > 100:
            strength = 100
        return self._do_action(self.vibrators, {"duration": duration, "strength": strength})

    def shock(self, duration, strength):
        if strength > 100:
            strength = 100
        info("Toy Shock - start(duration={}, strength={})".format(duration, strength))
        return self._do_action(self.estim, {"duration": duration, "strength": strength})

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
            re.compile(".+SEXLAB - Thread\[[0-9]+\] Event Hook - StageStart$", re.I): self.sex_stage_start
        }
        fallout_hooks = {
            # Fallout 4 AAF Support
            # AAF does not verbosely log, so we must depend on other mods that write log events on these hooks.
            # DD writes a specific log event when an animation involving the player starts, bostion devious helper writes one when it ends.
            # Use the two of these to capture a sex scene.
            # TODO: Write my own plugin that watches for these events.
            re.compile(".+DD: Player in AAF animation.*"): self.sex_start_simple,
            re.compile(".+BDH-INFO - OnAnimationStop.*"): self.sex_end,
            re.compile(".+ AFV report: FindRapistFor {}.*".format(CHARACTER_NAME.lower()), re.I): lambda m: self.chaster.update_time(random.randint(CHASTER_DEFEAT_MIN, CHASTER_DEFEAT_MAX)), # player was defeated.
            re.compile(".+AFV Report: Player is bleeding out in surrender.*"): self._chaster_spin_wheel # Player was knocked down.
            
        }
        chaster_hooks = {}
        if self.chaster_enabled:
            from toys.chastity.chaster.chaster import ChasterInterface
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
            re.compile("^.+Suspended stack count is over our warning threshold.+"): self.stack_overflow
        }
        self.hooks = {**sexlab_hooks, **chaster_hooks, **devious_hooks, **toys_hooks, **misc_hooks, **fallout_hooks}

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
            time.sleep(2)
            
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

        
        # If we blocked the attack, do nothing
        if hit_blocked == 'TRUE':
            return

        # If we got hit by a power attack, minimum strength is 25
        if power_attack == 'TRUE':
            strength = 25
        
        strength += 69 -(69 * (float(health) / float(health_max)))

        return self.toys.shock(1, int(strength))
        
    def stop_vibrate(self, match):
        return self.toys.stop()
    
    def toys_vibrate(self, match):
        orientation = match.group(1) # left/right, unused for now
        return self.toys.vibrate(int(match.group(3)), int(match.group(2)))

    def sex_start_simple(self, match):
        return self.toys.vibrate(300, MAX_VIBRATE_STRENGTH)
    
    def sex_start(self, match):
        info("Sex_start")
        self.sex_stage = 0
        return 
    
    def sex_stage_start(self, match):
        # This could go up too fast if there are multiple scenes happening, but shouldn't move if
        # the player is involved in none of them.
        if self.sex_stage is not None:
            self.sex_stage += 1
            info("Sex_stage_start: {}".format(str(self.sex_stage)))
            # For stages 1-5, go from strength 20-100. Consider it a process of warming up or sensitization ;)
            return self.toys.vibrate(300, min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER)) + self.toys.shock(300, min(MAX_VIBRATE_STRENGTH, self.sex_stage * self.SEX_STAGE_STRENGTH_MULTIPLIER) / 2)

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
        await run_task(ssi.toys.shock(2, 10))
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
    


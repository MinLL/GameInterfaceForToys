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
import FreeSimpleGUI as sg
from interfaces.interface import Interface

MAX_VIBRATE_STRENGTH = 100
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
class LogReaderInterface(Interface):
    SEX_STAGE_STRENGTH_MULTIPLIER = 20

    def __init__(self, toy_type=TOY_LOVENSE):
        self._cached_stamp = 0
        self.filename = settings.LOG_PATH
        self.file_pointer = 0
        self.sex_stage = None
        self.dd_vibrating = False
        self.is_game_over = False
        Interface.__init__(self, "Log Reader", toy_type)
        
    def _chaster_spin_wheel(self, match, event):
        return self.chaster.spin_wheel()

    def generic_chaster_add_time(self, match, event):
        params = event.params
        if 'TOTAL_TIME' in params:
            duration = params['TOTAL_TIME']
        elif 'min_time' and 'max_time' in params:
            print(params)
            duration = random.randint(int(params['min_time']), int(params['max_time']))
        else:
            fail("Malformed event - could not determine chastity duration")
            return
        self.chaster.update_time(duration)

    def submissive_lola_punish_add_time(self, match, event):
        # Todo: Incorporate number of days added as part of the chaster scaling? This is already in the regex match.
        # Need to see how this works in Submissive Lola first.
        self.chaster.update_time(random.randint(int(settings.CHASTER_PUNISH_MIN), int(settings.CHASTER_PUNISH_MAX)))

    def player_defeated(self, match, event):
        self.chaster.spin_wheel()
        self.chaster.update_time(random.randint(int(settings.CHASTER_DEFEAT_MIN), int(settings.CHASTER_DEFEAT_MAX)))


    def _parse_param(self, match, param):
        if type(param) == str and  '$' in param:
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
        return self.toys.shock(duration, strength, pattern, event=event, shock_only=True)
    
    def setup(self):
        try: 
            fd = open(self.filename, 'r', encoding='utf8')
            self._set_eof(fd)
            fd.close()
        except FileNotFoundError:
            fail("Could not open {} for reading - file does not exist.".format(self.filename))
        return Interface.setup(self)

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

        if not wornVagPlug and not wornAnalPlug:
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

    def ud_vibrate_until_stop(self, match, event):
        self.dd_vibrating = True
        strength = int(match.group(1))
        return self.dd_vibrate(500, strength/20, event=event)

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
        if source == "zbf punishment cane":
            info("Detected punishment cane - Strength set to 50~100")
            strength = random.randint(50, 100)
        elif strength <= 0 or float(health) >= float(health_max):
            info("Too weak - Not shocking (strength={}, health={}, health_max={})".format(strength, health, health_max))
            return
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

    def nor_ero_stop(self, match, event):
        info("NoR Ero Stop")
        if self.is_game_over:
            fail("Not stopping toys - Game Over event playing")
            return
        self.toys.stop()

    def nor_gameover_start(self, match, event):
        info("NoR GameOver Start")
        self.is_game_over = True
        self.generic_random_vibrate(match, event)

    def nor_gameover_stop(self, match, event):
        info("NoR GameOver Stop")
        self.is_game_over = False
        self.toys.stop()
        
    def execute(self):
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

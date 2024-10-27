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
            elif toy == TOY_XTOYS:
                from toys.xtoys.interface import XToysInterface
                tmp += [XToysInterface()]
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
        return self._do_action(interface, {"plus": False, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys, "action": "vibrate"})

    def vibrate_until_stop(self,strength,pattern="",event=None,vibrate_only=False):
        self.vibrate(500,strength,pattern,event,vibrate_only)

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
        return self._do_action(interface, {"plus": True, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys, "action": "vibrate_plus"})

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
        return self._do_action(interface, {"plus": False, "duration": duration, "strength": strength, "pattern": pattern, "toys": toys, "action": "shock"})

    def find_toys_for_event(self, event):
        if event is None:
            return []
        return [self.available_toys[toy] for toy in self.toy_event_map[event.name] if self.available_toys[toy]['enabled']]
    
    def _do_action(self, interfaces, params):
        # Remove duplicate interfaces
        interfaces = set(interfaces)
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

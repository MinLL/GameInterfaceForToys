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
from interfaces.log_reader import LogReaderInterface
from interfaces.memory_reader import MemoryReaderInterface
from interfaces.pixel_reader import PixelReaderInterface


config_fields = {
    'Enabled Interfaces': 'ENABLED_INTERFACES',
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
    'Chaster Punish Event Minimum Time To Add': 'CHASTER_PUNISH_MIN',
    'Chaster Punish Event Maximum Time To Add': 'CHASTER_PUNISH_MAX',
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
    'Target Monitor for Screen Capture': 'OUTPUT_IDX',
    'XToys Webhook ID': 'XTOYS_WEBHOOK_ID'
}


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
             [sg.Button(GUI_TEST_SHOCK_10)],
             [sg.Button(GUI_TEST_SHOCK_30)],
             [sg.Button(GUI_TEST_SHOCK_50)],
             [sg.Button(GUI_TEST_SHOCK_80)],
             [sg.Button(GUI_TEST_SHOCK_100)],
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
                if event == GUI_TEST_SHOCK_10:
                    await run_task(ssi.toys.shock(2, 10, "random"), run_async=True)
                if event == GUI_TEST_SHOCK_30:
                    await run_task(ssi.toys.shock(2, 30, "random"), run_async=True)
                if event == GUI_TEST_SHOCK_50:
                    await run_task(ssi.toys.shock(2, 50, "random"), run_async=True)
                if event == GUI_TEST_SHOCK_80:
                    await run_task(ssi.toys.shock(2, 80, "random"), run_async=True)
                if event == GUI_TEST_SHOCK_100:
                    await run_task(ssi.toys.shock(2, 100, "random"), run_async=True)
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
                await run_task(ssi.execute(), run_async=True)
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
        toy_layout[0].append(sg.Text(toy, size=(15, 1), expand_x=True))
    i = 1
    last_origin = None
    for event in ssi.event_loader.events:
        if last_origin != event.origin:
            toy_layout.append([sg.HorizontalSeparator(), sg.Text(event.origin, expand_x=True), sg.HorizontalSeparator()])
            last_origin = event.origin
            i += 1
        toy_layout.append([sg.Text(event.shortname, size=(25, 1), expand_x=True)])
        for toy in ssi.toys.available_toys:
            toy_layout[i].append(sg.Checkbox("", size=(15, 1), expand_x=True, key="{}:{}".format(event.name, toy), default=toy in ssi.toys.toy_event_map[event.name]))
        i += 1
    toy_layout.append([sg.Button(GUI_CONFIG_SAVE), sg.Button(GUI_CONFIG_EXIT), sg.Button(GUI_CONFIG_ENABLE_ALL), sg.Button(GUI_CONFIG_DISABLE_ALL), sg.Button(GUI_CONFIG_DEFAULTS)])
    scrollable = False
    if len(ssi.event_loader.events) > 12:
        scrollable = True
    toy_window = sg.Window('GIFT Toy:Event Map Configuration', [[sg.Column(toy_layout, scrollable=scrollable, expand_y=True, expand_x=True)]], modal=True, resizable=True)
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
        if event == GUI_CONFIG_DEFAULTS:
            for event in ssi.event_loader.events:
                for toy, v in ssi.toys.available_toys.items():
                    # Xtoys provides both features. Check for this.
                    both_estim_and_vib = (v['interface'] in [x.properties['name'] for x in ssi.toys.vibrators] and v['interface'] in [x.properties['name'] for x in ssi.toys.estim])
                    if both_estim_and_vib:
                        # This is a hacky workaround. Fix this later.
                        if event.toy_class is not None and event.toy_class == "vibrator" and not 'Shock' in toy:
                            ssi.toys.toy_event_map[event.name].append(toy)
                        elif event.toy_class is not None and event.toy_class == "estim" and 'Shock' in toy:
                            ssi.toys.toy_event_map[event.name].append(toy)
                    else:
                        if event.toy_class is not None and event.toy_class == "vibrator" and v['interface'] in [x.properties['name'] for x in ssi.toys.vibrators]:
                            ssi.toys.toy_event_map[event.name].append(toy)
                        elif event.toy_class is not None and event.toy_class == "estim" and v['interface'] in [x.properties['name'] for x in ssi.toys.estim]:
                            ssi.toys.toy_event_map[event.name].append(toy)
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
        if v == 'ENABLED_INTERFACES':
            config_layout.append([sg.Text('Enabled Interfaces:'), sg.Radio(INTERFACE_LOG_READER, 'interfaces', key=INTERFACE_LOG_READER, default=INTERFACE_LOG_READER in settings.ENABLED_INTERFACES),
                                  sg.Radio(INTERFACE_SCREEN_READER, 'interfaces', key=INTERFACE_SCREEN_READER, default=INTERFACE_SCREEN_READER in settings.ENABLED_INTERFACES),
                                  sg.Radio(INTERFACE_MEMORY_READER, 'interfaces', key=INTERFACE_MEMORY_READER, default=INTERFACE_MEMORY_READER in settings.ENABLED_INTERFACES),
                                  ])
        elif v == 'LOG_PATH':
            config_layout.append([sg.Text('Path to Log File'), sg.FileBrowse('Select Log File', key=v)])
            config_layout.append([sg.Text('Old Log File Path: {}'.format(settings.LOG_PATH))])
        elif v == 'IS_WINDOWS':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.IS_WINDOWS)])
        elif v == 'CHASTER_ENABLED':
            config_layout.append([sg.Checkbox(k, key=v, default=settings.CHASTER_ENABLED)])
        elif v == 'TOY_TYPE':
            config_layout.append([sg.Text('Supported Toys:'), sg.Checkbox(TOY_LOVENSE, key=TOY_LOVENSE, default=TOY_LOVENSE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_XTOYS, key=TOY_XTOYS, default=TOY_XTOYS in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_BUTTPLUG, key=TOY_BUTTPLUG, default=TOY_BUTTPLUG in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_COYOTE, key=TOY_COYOTE, default=TOY_COYOTE in settings.TOY_TYPE),
                                  sg.Checkbox(TOY_XBOXCONTROLLER, key=TOY_XBOXCONTROLLER, default=TOY_XBOXCONTROLLER in settings.TOY_TYPE),
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
                    if values[TOY_XTOYS] == True:
                        toys += [TOY_XTOYS]
                    settings.TOY_TYPE = toys
                elif x == 'ENABLED_INTERFACES':
                    interfaces = []
                    if values[INTERFACE_LOG_READER] == True:
                        interfaces += [INTERFACE_LOG_READER]
                    elif values[INTERFACE_SCREEN_READER] == True:
                        interfaces += [INTERFACE_SCREEN_READER]
                    elif values[INTERFACE_MEMORY_READER] == True:
                        interfaces += [INTERFACE_MEMORY_READER]
                    settings.ENABLED_INTERFACES = interfaces
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
        for interface in settings.ENABLED_INTERFACES:
            if interface == INTERFACE_LOG_READER:
                ssi = LogReaderInterface(toy_type=settings.TOY_TYPE)
            elif interface == INTERFACE_SCREEN_READER:
                ssi = PixelReaderInterface(toy_type=settings.TOY_TYPE)
            elif interface == INTERFACE_MEMORY_READER:
                ssi = MemoryReaderInterface(toy_type=settings.TOY_TYPE)

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

    


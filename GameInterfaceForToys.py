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
import platform

from common.constants import *
from common.util import *
import settings
from toys.base import FEATURE_VIBRATOR, FEATURE_ESTIM
from events.eventloader import EventLoader
import toys.chastity.chaster.chaster
import FreeSimpleGUI as sg

from interfaces.log_reader import LogReaderInterface
if platform.system() == "Windows":  # Only import interfaces that are actually supported on this platform.
    from interfaces.memory_reader import MemoryReaderInterface
    from interfaces.pixel_reader import PixelReaderInterface

# Note, values are all PSG KEYS.
# Note: Entries appear in PSG in the order listed.
config_fields = {

    # Interfaces
    "interfaces": {
        'Enabled Interfaces': 'ENABLED_INTERFACES'
    },

    # Toys
    "toys": {
        'Toy Type': 'TOY_TYPE'
    },

    # Log reader interface settings
    "interface_log_reader": {
        'Log Path': 'LOG_PATH',
        'In-game character name (Skyrim, Fallout 4)': 'CHARACTER_NAME',
        'Devious Devices Vibration Multiplier (Skyrim, Fallout 4)': 'DD_VIB_MULT',
        'Print Log Lines': 'PRINT_LOG_LINES'
    },

    # Screen reader interface settings
    "interface_screen_reader": {
        'Target Monitor for Screen Capture': 'OUTPUT_IDX'
    },

    # Memory reader interface settings
    "interface_memory_reader": {

    },

    # Buttplug.io settings
    "buttplugio": {
        'Strength Max': 'BUTTPLUG_STRENGTH_MAX',
        'Server Address': 'BUTTPLUG_SERVER_ADDRESS'
    },

    # Chaster settings
    "chaster": {
        'Chaster Enabled': 'CHASTER_ENABLED',
        'Token': 'CHASTER_TOKEN',
        'Refresh Token': 'CHASTER_REFRESH_TOKEN',
        'Lock Name': 'LOCK_NAME',
        'Defeat Minimum Time to Add': 'CHASTER_DEFEAT_MIN',
        'Defeat Maximum Time to Add': 'CHASTER_DEFEAT_MAX',
        'Punish Event Minimum Time To Add': 'CHASTER_PUNISH_MIN',
        'Punish Event Maximum Time To Add': 'CHASTER_PUNISH_MAX'
    },

    # Coyote settings (deprecated)
    "coyote": {
        'UID': 'COYOTE_UID',
        'Multiplier': 'COYOTE_MULTIPLIER',
        'Default Channel': 'COYOTE_DEFAULT_CHANNEL',
        'Sex Multiplier': 'COYOTE_SEX_MULT',
        'Plug Multiplier': 'COYOTE_PLUG_MULT',
        'On-Hit Multiplier': 'COYOTE_ON_HIT_MULT',
        'Minimum Power (0-768)': 'COYOTE_MIN_POWER',
        'Maximum Power (0-768)': 'COYOTE_MAX_POWER'
    },

    # Lovense settings
    "lovense": {
        'Host': 'LOVENSE_HOST',
        'Strength Max': 'LOVENSE_STRENGTH_SCALE',
        'Use New API': 'LOVENSE_USE_NEW_API'
    },

    # XToys settings
    "xtoys": {
        'Webhook ID': 'XTOYS_WEBHOOK_ID',
        'Shock Min Strength %': 'XTOYS_SHOCK_MIN',
        'Shock Max Strength %': 'XTOYS_SHOCK_MAX'
    },

    # Edge-o-Matic settings
    "maustec": {
        "Host": "MAUSTEC_HOST"
    },

    # General settings
    "general": {
        'Warn On Stack Dump': 'WARN_ON_STACK_DUMP',
        'Warn On Stack Dump SOUND': 'WARN_ON_STACK_DUMP_SOUND',
        'UI Window Update Frequency': 'WINDOW_UPDATE_FREQUENCY'
    },

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
        # sg.theme("GrayGrayGray")
        # sg.theme("DarkAmber")
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
             sg.Column([[sg.Output(size=(120, 40), background_color='black', text_color='white', expand_x=True, expand_y=True)]], expand_x=True, expand_y=True)
        ]]
        window = sg.Window('Game Interface For Toys', layout, resizable=True)
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

    # fixme: Temporarily switch to default OS theme to make disabled text fields (always off-gray irrespective
    #  of theme) look less jarring. Default colour for disabled fields needs to be configured globally, but PSG
    #  doesn't support this yet.
    sg.theme("GrayGrayGray")

    # # Create individual clusters of related settings by iterating over grouped key/value pairs in config_fields.
    # Each cluster is finally encapsulated inside a separate sg.Frame().
    # Not very DRY.

    # Interface settings
    interface_frame = []

    # Iterate over interface settings, with special handling for fields that require it.
    for k, v in config_fields["interfaces"].items():
        match v:
            case "ENABLED_INTERFACES":
                field = [sg.Column(layout=[
                                            [sg.Radio(INTERFACE_LOG_READER + " " + "(Skyrim, Fallout 4, Mount & Blade: Bannerlords 2, Night of Revenge)", 'interfaces', key=INTERFACE_LOG_READER,
                                                     default=INTERFACE_LOG_READER in settings.ENABLED_INTERFACES, enable_events=True)],
                                            [sg.Radio(INTERFACE_SCREEN_READER + " " + "(Elden Ring)", 'interfaces', key=INTERFACE_SCREEN_READER,
                                                     default=INTERFACE_SCREEN_READER in settings.ENABLED_INTERFACES, enable_events=True)],
                                            [sg.Radio(INTERFACE_MEMORY_READER, 'interfaces', key=INTERFACE_MEMORY_READER,
                                                     default=INTERFACE_MEMORY_READER in settings.ENABLED_INTERFACES, enable_events=True)]
                                            ]
                                  )
                         ]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        interface_frame.append(field)

    # Toy settings
    toys_frame = []

    # Iterate over toy settings, with special handling for fields that require it.
    for k, v in config_fields["toys"].items():
        match v:
            case "TOY_TYPE":
                field = [sg.Column(layout=[
                                          [sg.Checkbox(TOY_XBOXCONTROLLER, key=TOY_XBOXCONTROLLER, default=TOY_XBOXCONTROLLER in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_LOVENSE, key=TOY_LOVENSE, default=TOY_LOVENSE in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_XTOYS, key=TOY_XTOYS, default=TOY_XTOYS in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_BUTTPLUG, key=TOY_BUTTPLUG, default=TOY_BUTTPLUG in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_COYOTE, key=TOY_COYOTE, default=TOY_COYOTE in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_KIZUNA, key=TOY_KIZUNA, default=TOY_KIZUNA in settings.TOY_TYPE, enable_events=True)],
                                          [sg.Checkbox(TOY_EDGEOMATIC, key=TOY_EDGEOMATIC, default=TOY_EDGEOMATIC in settings.TOY_TYPE, enable_events=True)],
                                          ]
                                    )
                        ]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        toys_frame.append(field)

    # General settings
    general_frame = []

    # Iterate over general settings, with special handling for fields that require it.
    for k, v in config_fields["general"].items():
        match v:
            case "WARN_ON_STACK_DUMP":
                field = [sg.Checkbox(k, key=v, default=settings.WARN_ON_STACK_DUMP, tooltip="This will let you know in-game if the script has crashed unexpectedly. Choose between an auditive cue or a distinct vibration pattern through your toys."),
                                sg.Radio("Play a sound","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=settings.WARN_ON_STACK_DUMP_SOUND),
                                sg.Radio("Vibe my toys","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=not settings.WARN_ON_STACK_DUMP_SOUND)
                         ]

            case "WARN_ON_STACK_DUMP_SOUND":
                field = []

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        general_frame.append(field)

    # Log reader settings
    log_reader_frame = []

    # Iterate over log reader settings, with special handling for fields that require it.
    for k, v in config_fields["interface_log_reader"].items():
        match v:
            case "LOG_PATH":
                field = [
                            sg.Column(layout=[
                            [sg.Text(text='Current log file: {}'.format(settings.LOG_PATH), tooltip="This lets you specify the log file required to interface with games including Skyrim, FO4 and M&B Bannerlords 2. The default value is ../Documents/My Games/Fallout4/Logs/Script/Papyrus.0.log", key="-LOG_PATH_TEXT-")],
                            [sg.FileBrowse('Select another log file', key=v, disabled=not INTERFACE_LOG_READER in settings.ENABLED_INTERFACES, enable_events=True)]])
                        ]

            case "PRINT_LOG_LINES":
                field = [sg.Checkbox(k, key=v, default=settings.PRINT_LOG_LINES, disabled=not INTERFACE_LOG_READER in settings.ENABLED_INTERFACES)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not INTERFACE_LOG_READER in settings.ENABLED_INTERFACES)]

        log_reader_frame.append(field)

    # Log reader settings
    screen_reader_frame = []

    # Iterate over screen reader settings. No special case handling necessary.
    for k, v in config_fields["interface_screen_reader"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not INTERFACE_SCREEN_READER in settings.ENABLED_INTERFACES)]

        screen_reader_frame.append(field)

    # Buttplug-io related settings
    buttplugio_frame = []

    # Iterate over buttplug.io related settings. No special case handling necessary.
    for k, v in config_fields["buttplugio"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not TOY_BUTTPLUG in settings.TOY_TYPE)]

        buttplugio_frame.append(field)

    # Chaster related settings
    chaster_frame = []

    # Iterate over Chaster related settings, with special handling for fields that require it.
    # fixme: This should probably be listed under toys/integrations, not a separate section.
    # todo: Add "Authenticate with Chaster" here.
    for k, v in config_fields["chaster"].items():
        match v:
            case "CHASTER_ENABLED":
                field = [sg.Checkbox(k, key=v, default=settings.CHASTER_ENABLED, enable_events=True)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not settings.CHASTER_ENABLED)]

        chaster_frame.append(field)

    # DG-Lab Coyote related settings
    coyote_frame = []

    # Iterate over DG-Lab Coyote related settings. No special case handling necessary.
    for k, v in config_fields["coyote"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not TOY_COYOTE in settings.TOY_TYPE)]

        coyote_frame.append(field)

    # Lovense related settings
    lovense_frame = []

    # Iterate over Lovense related settings, with special handling for fields that require it.
    for k, v in config_fields["lovense"].items():
        match v:
            case "LOVENSE_USE_NEW_API":
                field = [sg.Checkbox(k, key=v, default=settings.LOVENSE_USE_NEW_API, disabled=not TOY_LOVENSE in settings.TOY_TYPE)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not TOY_LOVENSE in settings.TOY_TYPE)]

        lovense_frame.append(field)

    # XToys related settings
    xtoys_frame = []

    # Iterate over XToys related settings. No special case handling necessary.
    for k, v in config_fields["xtoys"].items():
        match v:

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not TOY_XTOYS in settings.TOY_TYPE)]

        xtoys_frame.append(field)

    # Maustec related settings
    maustec_frame = []

    # Iterate over Maustec related settings. No special case handling necessary.
    for k, v in config_fields["maustec"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v, disabled=not TOY_EDGEOMATIC in settings.TOY_TYPE)]

        maustec_frame.append(field)

    config_layout = []

    config_layout.append(
        [
            sg.Column(vertical_alignment="top", expand_x=True, expand_y=True, layout=
                      [
                          [sg.Frame(title="Game interface ('Input')", expand_x=True, vertical_alignment="top", layout=interface_frame)],
                          [sg.Frame(title="Log reader settings", expand_x=True, layout=log_reader_frame)],
                          [sg.Frame(title="Screen reader settings", expand_x=True, layout=screen_reader_frame)],

                          [sg.VPush()],
                          [sg.HorizontalSeparator()],
                          [sg.VPush()],

                          [sg.Frame(title="Chaster settings", expand_x=True, layout=chaster_frame)],

                          [sg.VPush()],
                          [sg.HorizontalSeparator()],
                          [sg.VPush()],

                          [sg.Frame(title="General settings", expand_x=True, layout=general_frame)],

                          [sg.VPush()]

                      ]
            ),

            sg.Push(),
            sg.VerticalSeparator(),
            sg.Push(),

            sg.Column(vertical_alignment="top", expand_x=True, expand_y=True, layout=
                      [
                          [sg.Frame(title="Toy integrations ('Output')", expand_x=True, layout=toys_frame)],
                          [sg.Frame(title="Lovense settings", expand_x=True, layout=lovense_frame)],
                          [sg.Frame(title="Buttplug.io settings", expand_x=True, layout=buttplugio_frame)],
                          [sg.Frame(title="XToys settings", expand_x=True, layout=xtoys_frame)],
                          [sg.Frame(title="DG-Lab Coyote settings", expand_x=True, layout=coyote_frame)],
                          [sg.Frame(title="Maustec settings", expand_x=True, layout=maustec_frame)],
                      ]
            ),
        ]
    )

    config_layout.append([sg.HorizontalSeparator()])

    config_layout.append([sg.Button(GUI_CONFIG_SAVE, expand_x=True), sg.Button("Reset all settings", expand_x=True), sg.Button(GUI_CONFIG_EXIT, expand_x=True)])

    config_window = sg.Window('GIFT Configuration', [
        [sg.Column(config_layout, scrollable=False, expand_y=True, expand_x=True)]
    ], modal=True, resizable=True)

    while True:
        event, values = config_window.read()

        # info(f"Matching event: {event}")
        # info(f"Values: {values}")

        if event == GUI_CONFIG_EXIT or event == sg.WIN_CLOSED:
            info('Exited configuration menu without saving.')
            break

        # Reset settings confirmation modal notified this window that the user reset all settings.
        if event == GUI_CONFIG_RESET_SETTINGS:
            config_window.close()
            info("Exited configuration menu and reset all settings.")
            raise ReloadException()  # Reset/refresh the main window, e.g. if Chaster was enabled and now no longer is.

        ### This section handles instant GUI updates ###

        # Detect change to interface choice, grey out invalid options, allow relevant options.
        if event in [INTERFACE_LOG_READER, INTERFACE_MEMORY_READER, INTERFACE_SCREEN_READER]:
            if event == INTERFACE_LOG_READER:  # Switched to log reader
                for k, v in config_fields["interface_log_reader"].items():
                    config_window[v].update(disabled=False)

                for k, v in config_fields["interface_screen_reader"].items():
                    config_window[v].update(disabled=True)
                for k, v in config_fields["interface_memory_reader"].items():
                    config_window[v].update(disabled=True)

            if event == INTERFACE_MEMORY_READER:  # Switched to memory reader
                for k, v in config_fields["interface_memory_reader"].items():
                    config_window[v].update(disabled=False)

                for k, v in config_fields["interface_screen_reader"].items():
                    config_window[v].update(disabled=True)
                for k, v in config_fields["interface_log_reader"].items():
                    config_window[v].update(disabled=True)

            if event == INTERFACE_SCREEN_READER:  # Switched to screen reader
                for k, v in config_fields["interface_screen_reader"].items():
                    config_window[v].update(disabled=False)

                for k, v in config_fields["interface_memory_reader"].items():
                    config_window[v].update(disabled=True)
                for k, v in config_fields["interface_log_reader"].items():
                    config_window[v].update(disabled=True)

        # (Dis-)allow Chaster options based on toggle.
        if event == "CHASTER_ENABLED":
            # Avoid updating state of Chaster toggle itself. Work-around/fixme.
            temp_dict = copy.deepcopy(config_fields["chaster"])
            del temp_dict["Chaster Enabled"]

            if values["CHASTER_ENABLED"]:
                for k, v in temp_dict.items():
                    config_window[v].update(disabled=False)
            else:
                for k, v in temp_dict.items():
                    config_window[v].update(disabled=True)

        # Update shown Papyrus log path immediately when a new file has been chosen.
        if event == "LOG_PATH":
            config_window["-LOG_PATH_TEXT-"].update('Current log file: {}'.format(values["LOG_PATH"]))

        # (Dis-)allow toy settings based in their individual toggle
        if event in [TOY_LOVENSE, TOY_BUTTPLUG, TOY_COYOTE, TOY_KIZUNA, TOY_EDGEOMATIC, TOY_XBOXCONTROLLER, TOY_XTOYS]:

            # We don't need to handle each toy config section individually, just iterate through a zip list mapping config categories to toy IDs.
            toy_settings_mapping = zip(
                ["buttplugio", "lovense", "xtoys", "coyote", "maustec"],
                [TOY_BUTTPLUG, TOY_LOVENSE, TOY_XTOYS, TOY_COYOTE, TOY_EDGEOMATIC]
            )

            for settings_frame, toy_id in toy_settings_mapping:
                for _, v in config_fields[settings_frame].items():
                    config_window[v].update(disabled=not values[toy_id])

        # Let user reset all settings to default values with a modal popup
        if event == "Reset all settings":
            reset_confirmation_modal = sg.Window(title="Confirmation", modal=True, layout=[
                [sg.Text("Really reset all settings?\nThis resets everything in settings.yaml to their default values.\n"
                         "Note: This does NOT reset event-toy mappings made on the Event Map Configuration window (toy-event-map.yaml).")],

                [sg.Button("Yes, reset all settings.", enable_events=True, expand_x=True, key=GUI_CONFIG_RESET_SETTINGS),
                 sg.Button("Cancel", enable_events=True, expand_x=True, key=GUI_CONFIG_EXIT)]
            ])

            while True:
                event, values = reset_confirmation_modal.read()

                # Reset all settings, refresh settings.yaml with default values from settings.py, close settings window.
                if event == GUI_CONFIG_RESET_SETTINGS:
                    info("reset")
                    importlib.reload(settings)  # Reload settings module
                    save_config()  # Repopulate settings.yaml with default values from settings.py

                    config_window.write_event_value(GUI_CONFIG_RESET_SETTINGS, dict())  # Tell parent window that we reset all settings
                    reset_confirmation_modal.close()  # Close confirmation modal
                    break

                if event == GUI_CONFIG_EXIT or event == sg.WIN_CLOSED:
                    reset_confirmation_modal.close()
                    break

        ###

        if event == GUI_CONFIG_SAVE:
            for category in config_fields.keys():
                for x in config_fields[category].values():
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
        for v in config_fields.values():
            for k, x in v.items():
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

            for category in config_fields.keys():
                for x in config_fields[category].values():
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
            if platform.system() == "Windows":
                if interface == INTERFACE_SCREEN_READER:
                    ssi = PixelReaderInterface(toy_type=settings.TOY_TYPE)
                elif interface == INTERFACE_MEMORY_READER:
                    ssi = MemoryReaderInterface(toy_type=settings.TOY_TYPE)
                elif interface == INTERFACE_LOG_READER:
                    ssi = LogReaderInterface(toy_type=settings.TOY_TYPE)
            else:
                if interface == INTERFACE_LOG_READER:
                    ssi = LogReaderInterface(toy_type=settings.TOY_TYPE)
                else:
                    raise NotImplementedError(f"Interface {interface} is currently not supported on {platform.system()}. For now, please delete your settings.yaml and restart the program.")
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



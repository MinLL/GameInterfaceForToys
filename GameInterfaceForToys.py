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
from interfaces.log_reader import LogReaderInterface
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

    # Log reader interface
    "interface_log_reader": {
        'Log Path': 'LOG_PATH',
        'Print Log Lines': 'PRINT_LOG_LINES'
    },

    # Screen reader interface
    "interface_screen_reader": {
        'Target Monitor for Screen Capture': 'OUTPUT_IDX'
    },

    # Bethesda games
    "bethesda": {
        'Character Name': 'CHARACTER_NAME',
        'Devious Devices Vib Multiplier': 'DD_VIB_MULT'
    },

    # Buttplug.io
    "buttplugio": {
        'Buttplug.io Strength Max': 'BUTTPLUG_STRENGTH_MAX',
        'Buttplug.io Server Address': 'BUTTPLUG_SERVER_ADDRESS'
    },

    # Chaster
    "chaster": {
        'Chaster Enabled': 'CHASTER_ENABLED',
        'Chaster Token': 'CHASTER_TOKEN',
        'Chaster Refresh Token': 'CHASTER_REFRESH_TOKEN',
        'Chaster Lock Name': 'LOCK_NAME',
        'Chaster Defeat Minimum Time to Add': 'CHASTER_DEFEAT_MIN',
        'Chaster Defeat Maximum Time to Add': 'CHASTER_DEFEAT_MAX',
        'Chaster Punish Event Minimum Time To Add': 'CHASTER_PUNISH_MIN',
        'Chaster Punish Event Maximum Time To Add': 'CHASTER_PUNISH_MAX'
    },

    # Coyote (deprecated)
    "coyote": {
        'Coyote E-Stim UID': 'COYOTE_UID',
        'Coyote E-Stim Multiplier': 'COYOTE_MULTIPLIER',
        'Coyote E-Stim Default Channel': 'COYOTE_DEFAULT_CHANNEL',
        'Coyote Sex Multiplier': 'COYOTE_SEX_MULT',
        'Coyote Plug Multiplier': 'COYOTE_PLUG_MULT',
        'Coyote On-Hit Multiplier': 'COYOTE_ON_HIT_MULT',
        'Coyote Minimum Power (0-768)': 'COYOTE_MIN_POWER',
        'Coyote Maximum Power (0-768)': 'COYOTE_MAX_POWER'
    },

    # Lovense
    "lovense": {
        'Lovense Host': 'LOVENSE_HOST',
        'Lovense Strength Max': 'LOVENSE_STRENGTH_SCALE',
        'Lovense Use New API': 'LOVENSE_USE_NEW_API'
    },

    # XToys
    "xtoys": {
        'XToys Webhook ID': 'XTOYS_WEBHOOK_ID',
        'XToys Shock Min Strength %': 'XTOYS_SHOCK_MIN',
        'XToys Shock Max Strength %': 'XTOYS_SHOCK_MAX'
    },

    # Edge-o-Matic
    "maustec": {
        "Maustec host": "MAUSTEC_HOST"
    },

    # General
    "general": {
        'Is the OS Windows?': 'IS_WINDOWS',
        'Window Update Frequency': 'WINDOW_UPDATE_FREQUENCY',
        'Warn On Stack Dump': 'WARN_ON_STACK_DUMP',
        'Warn On Stack Dump SOUND': 'WARN_ON_STACK_DUMP_SOUND'
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

    # Create individual clusters of related settings by iterating over grouped key/value pairs from config_fields.
    # Each cluster is finally encapsulated inside a separate sg.Frame().
    # Not very DRY.

    # Interface settings
    interface_frame = []

    # Iterate over interface settings, with special handling for fields that require it.
    for k, v in config_fields["interfaces"].items():
        match v:
            case "ENABLED_INTERFACES":
                field = [sg.Column(layout=[
                                            [sg.Radio(INTERFACE_LOG_READER, 'interfaces', key=INTERFACE_LOG_READER,
                                                     default=INTERFACE_LOG_READER in settings.ENABLED_INTERFACES, enable_events=True)],
                                            [sg.Radio(INTERFACE_SCREEN_READER, 'interfaces', key=INTERFACE_SCREEN_READER,
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
                                          [sg.Checkbox(TOY_LOVENSE, key=TOY_LOVENSE, default=TOY_LOVENSE in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_XTOYS, key=TOY_XTOYS, default=TOY_XTOYS in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_BUTTPLUG, key=TOY_BUTTPLUG, default=TOY_BUTTPLUG in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_COYOTE, key=TOY_COYOTE, default=TOY_COYOTE in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_XBOXCONTROLLER, key=TOY_XBOXCONTROLLER, default=TOY_XBOXCONTROLLER in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_KIZUNA, key=TOY_KIZUNA, default=TOY_KIZUNA in settings.TOY_TYPE)],
                                          [sg.Checkbox(TOY_EDGEOMATIC, key=TOY_EDGEOMATIC, default=TOY_EDGEOMATIC in settings.TOY_TYPE)],
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

            case "IS_WINDOWS":
                field = [sg.Checkbox(k, key=v, default=settings.IS_WINDOWS, tooltip="Leave this on if you're running on Windows, otherwise the script will have issues traversing the filesystem. Default: enabled.")]

            case "WARN_ON_STACK_DUMP":
                field = [sg.Checkbox(k, key=v, default=settings.WARN_ON_STACK_DUMP),
                                sg.Radio("speaker","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=settings.WARN_ON_STACK_DUMP_SOUND),
                                sg.Radio("buzzer","WARN_ON_STACK_DUMP_SOUND", key="WARN_ON_STACK_DUMP_SOUND", default=not settings.WARN_ON_STACK_DUMP_SOUND)
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
                            [sg.Text('Current log file Path: {}'.format(settings.LOG_PATH))],
                            [sg.FileBrowse('Select new log file', key=v)]])
                        ]

            case "PRINT_LOG_LINES":
                field = [sg.Checkbox(k, key=v, default=settings.PRINT_LOG_LINES)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        log_reader_frame.append(field)

    # Log reader settings
    screen_reader_frame = []

    # Iterate over screen reader settings. No special case handling necessary.
    for k, v in config_fields["interface_screen_reader"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        screen_reader_frame.append(field)

    # Bethesda game related settings
    bethesda_frame = []

    # Iterate over bethesda game related settings. No special case handling necessary.
    for k, v in config_fields["bethesda"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        bethesda_frame.append(field)

    # Buttplug-io related settings
    buttplugio_frame = []

    # Iterate over buttplug.io related settings. No special case handling necessary.
    for k, v in config_fields["buttplugio"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        buttplugio_frame.append(field)

    # Chaster related settings
    chaster_frame = []

    # Iterate over Chaster related settings, with special handling for fields that require it.
    # fixme: This should be under toys/integrations, not a separate checkbox.
    for k, v in config_fields["chaster"].items():
        match v:
            case "CHASTER_ENABLED":
                field = [sg.Checkbox(k, key=v, default=settings.CHASTER_ENABLED)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        chaster_frame.append(field)

    # DG-Lab Coyote related settings
    coyote_frame = []

    # Iterate over DG-Lab Coyote related settings. No special case handling necessary.
    for k, v in config_fields["coyote"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        coyote_frame.append(field)

    # Lovense related settings
    lovense_frame = []

    # Iterate over Lovense related settings, with special handling for fields that require it.
    # fixme: This should be under toys/integrations, not a separate checkbox.
    for k, v in config_fields["lovense"].items():
        match v:
            case "LOVENSE_USE_NEW_API":
                field = [sg.Checkbox(k, key=v, default=settings.LOVENSE_USE_NEW_API)]

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        lovense_frame.append(field)

    # XToys related settings
    xtoys_frame = []

    # Iterate over XToys related settings, with special handling for fields that require it.
    # fixme: This should be under toys/integrations, not a separate checkbox.
    for k, v in config_fields["xtoys"].items():
        match v:

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        xtoys_frame.append(field)


    # XToys related settings
    xtoys_frame = []

    # Iterate over XToys related settings, with special handling for fields that require it.
    # fixme: This should be under toys/integrations, not a separate checkbox.
    for k, v in config_fields["xtoys"].items():
        match v:

            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        xtoys_frame.append(field)


    # # Maustec related settings
    maustec_frame = []

    # Iterate over Maustec related settings related settings. No special case handling necessary.
    for k, v in config_fields["maustec"].items():
        match v:
            case _:
                field = [sg.Text(k), sg.Push(), sg.Input(getattr(settings, v), key=v)]

        maustec_frame.append(field)


    config_layout = []

    # config_layout.append(
    #     [
    #         sg.Column(expand_x=True, vertical_alignment="top", layout=[[sg.Frame(title="Interface settings", layout=interface_frame, expand_x=True, expand_y=True)]]),
    #         sg.Column(expand_x=True, vertical_alignment="top", layout=[[sg.Frame(title="Toy settings", layout=toys_frame, expand_x=True, expand_y=True)]])
    #     ]
    # )

    config_layout.append(
        [
            sg.Column(vertical_alignment="top", expand_x=True, expand_y=True, layout=
                      [
                          [sg.Frame(title="Interface", expand_x=True, expand_y=True, vertical_alignment="top", layout=interface_frame),
                           sg.Column(expand_x=True, expand_y=True, layout=[[sg.Frame(title="Log reader settings", expand_x=True, layout=log_reader_frame)], [sg.Frame(title="Screen reader settings", expand_x=True, layout=screen_reader_frame)]])],
                          # [sg.Frame(title="Interface", layout=interface_frame)],
                          # [sg.Frame(title="Log reader settings", layout=log_reader_frame)],
                          # [sg.Frame(title="Screen reader settings", layout=screen_reader_frame)],
                          # [sg.VPush()],
                          [sg.HorizontalSeparator()],
                          [sg.Frame(title="Bethesda game settings", layout=bethesda_frame)],
                          # [sg.VPush()],
                          [sg.HorizontalSeparator()],
                          [sg.Frame(title="General settings", layout=general_frame)],
                          # [sg.VPush()],
                          [sg.HorizontalSeparator()],
                          [sg.Frame(title="Chaster settings", layout=chaster_frame)]


                      ]
            ),

            sg.VerticalSeparator(),
            # sg.VPush(),

            sg.Column(vertical_alignment="top", expand_x=True, expand_y=True, layout=
                      [
                          [sg.Frame(title="Toys", layout=toys_frame)],
                          [sg.Frame(title="Buttplug.io settings", layout=buttplugio_frame)],
                          [sg.Frame(title="DG-Lab Coyote settings", layout=coyote_frame)],
                          [sg.Frame(title="Lovense settings", layout=lovense_frame)],
                          [sg.Frame(title="XToys settings", layout=xtoys_frame)],
                          [sg.Frame(title="Maustec settings", layout=maustec_frame)],
                      ]
            ),

            # sg.VPush(),
            #
            # sg.Column(vertical_alignment="top", expand_x=True, expand_y=True, layout=
            # [
            #     [sg.Frame(title="Chaster settings", layout=chaster_frame)]
            # ]
            # ),

        ]
    )


    # config_layout.append([sg.Frame(title="Interface", layout=interface_frame)])
    # config_layout.append([sg.Frame(title="Toys", layout=toys_frame)])
    # config_layout.append([sg.Frame(title="Log reader settings", layout=log_reader_frame)])
    # config_layout.append([sg.Frame(title="General settings", layout=general_frame)])
    # # config_layout.append([sg.Frame(title="General settings", layout=general_frame, expand_x=True)])
    # config_layout.append([sg.Frame(title="Screen reader settings", layout=screen_reader_frame)])
    # config_layout.append([sg.Frame(title="Bethesda game settings", layout=bethesda_frame)])
    # config_layout.append([sg.Frame(title="Buttplug.io settings", layout=buttplugio_frame)])
    # config_layout.append([sg.Frame(title="Chaster settings", layout=chaster_frame)])
    # config_layout.append([sg.Frame(title="DG-Lab Coyote settings", layout=coyote_frame)])
    # config_layout.append([sg.Frame(title="Lovense settings", layout=lovense_frame)])
    # config_layout.append([sg.Frame(title="XToys settings", layout=xtoys_frame)])
    # config_layout.append([sg.Frame(title="Maustec settings", layout=maustec_frame)])

    config_layout.append([sg.HorizontalSeparator()])

    config_layout.append([sg.Button(GUI_CONFIG_SAVE), sg.Button(GUI_CONFIG_EXIT)])

    config_window = sg.Window('GIFT Configuration', [[sg.Column(config_layout, scrollable=False, expand_y=True, expand_x=True)]], modal=True, resizable=True)
    while True:
        event, values = config_window.read()
        if event == GUI_CONFIG_EXIT or event == sg.WIN_CLOSED:
            info('Exited configuration menu without saving.')
            break

        # On the fly GUI logic here

        # Detect change to interface
        if event in ["INTERFACE_LOG_READER", "INTERFACE_MEMORY_READER", "INTERFACE_SCREEN_READER"]:
            match event:
                case "INTERFACE_LOG_READER":  # Switched to log reader
                    # ENABLE/DISABLE FRAMES HERE
                    for k, v in config_fields["interface_log_reader"].items():
                        config_window[v].update(disabled=False)

                    for k, v in config_fields["interface_screen_reader"].items():
                        config_window[v].update(disabled=True)
                    for k, v in config_fields["interface_memory_reader"].items():
                        config_window[v].update(disabled=True)

                case "INTERFACE_MEMORY_READER":  # Switched to memory reader
                    for k, v in config_fields["interface_memory_reader"].items():
                        config_window[v].update(disabled=False)

                    for k, v in config_fields["interface_screen_reader"].items():
                        config_window[v].update(disabled=True)
                    for k, v in config_fields["interface_log_reader"].items():
                        config_window[v].update(disabled=True)

                case "INTERFACE_SCREEN_READER":  # Switched to screen reader
                    for k, v in config_fields["interface_screen_reader"].items():
                        config_window[v].update(disabled=False)

                    for k, v in config_fields["interface_memory_reader"].items():
                        config_window[v].update(disabled=True)
                    for k, v in config_fields["interface_log_reader"].items():
                        config_window[v].update(disabled=True)


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
        # breakpoint()
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
            for x in config_fields.values():
                safe_load_config(x)
            success('Done.')
    except FileNotFoundError:
        fail("Could not load configuration file - using defaults.")
        save_config()
#
#
# #####################
#
# def make_startup_window():
#     # Define the window's contents
#     layout = [[sg.Image(filename="media/coyote_egg.png", subsample=4)], [
#         sg.Button('Connect and play with DG-Lab Coyote', size=(40, 5), enable_events=True, bind_return_key=True,
#                   tooltip="Start local websockets server and connect with device from your machine."),
#         # sg.VerticalSeparator(),
#         sg.Button("Try out program\nwithout device", size=(20, 5),
#                   tooltip="Explore the program without connecting to a device."), sg.Button('Quit', size=(20, 5))]]
#
#     # Create the window
#     window = sg.Window('DG-Lab Coyote Control Application - Start', layout, element_justification="centered")
#     return window
#
#
# ## On-boarding flow
# def create_text_message(input_text="Hello world", font=None, color=None, bg_color=None):
#     return sg.Text(text=input_text, font=font,  # background_color="#43414e", text_color="#FFFFFF",
#                    text_color=color if color else None, background_color=bg_color if bg_color else None, expand_x=False,
#                    expand_y=True, pad=(0, 0))
#
#
# def ctm(input_text="Hello world", font="", color=None, bg_color=None):
#     return create_text_message(input_text=input_text, font=font, color=color, bg_color=bg_color)
#
#
# def make_flow_window_one():
#     text_messages = [ctm("Welcome to PyCoyote (working title)!", font="bold", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("* Talk natively over Bluetooth with the DG-Lab Coyote from"),
#                      # ctm("  your Windows, MacOS or Linux PC."),
#                      # ctm("* Try out stimulating default patterns, or"),
#                      # ctm("  setup custom patterns by hand or from imported audio files."),
#                      # ctm("* Automate increases and decreases in intensity, and more!"),
#                      ctm("", color=flow_text_color, bg_color=flow_background_color),  # <br>
#                      ctm("First, turn on your DG-Lab Coyote and click continue.", color=flow_text_color, bg_color=flow_background_color), ctm("", color=flow_text_color, bg_color=flow_background_color), ctm("", color=flow_text_color, bg_color=flow_background_color)]
#
#     # "\n\nE-stim safely.\nThe developers disavow any liability\nstemming"
#     #     " from the use of this software.\n\nNEVER E-STIM ABOVE THE CHEST.\nEtc.", "Turn on your Coyote",
#     #     "Connect to your Coyote via the bluetooth server. If you've already done so, skip to the next step.",
#     #     "Equip your electrodes."
#     #     "Done!"
#
#     # Create empty column layout list
#     column_layout = []
#
#     # Add the text lines individually as Text (labels)
#     for text in text_messages:
#         column_layout.append([text])
#
#     # Add buttons
#     column_layout.append([  # sg.Push(background_color="#43414e"),
#         sg.Button('Continue', bind_return_key=True, size=(None, 5), expand_x=True, expand_y=True),
#         # sg.Button('Cancel', size=(None, 2), expand_x=False)
#     ])
#
#     #
#     # # Add tick box to disable on-boarding for next time
#     # # todo: Add at the end!
#     # column_layout.append([
#     #     sg.CBox(text="Don't show guide next time.", text_color="#FFFFFF", checkbox_color="#43414e", background_color="#43414e")
#     # ])
#
#     # set column element size
#     width, height = 400, 550
#
#     # Set padding for column element
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = 150, 50
#
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = int(height/2), 50
#
#     pad_left, pad_right = 20, 20
#     pad_top, pad_bottom = 50, 20
#
#     column = sg.Column(layout=column_layout, pad=((pad_left, pad_right), (pad_top, pad_bottom)),
#                        vertical_alignment="bottom", expand_x=True, background_color=flow_background_color)
#
#     layout = [[sg.Image(filename="media/coyote_3.png", size=(width, height), subsample=4),  # background_color
#                column]]
#
#     # Create the window
#     window = sg.Window("DG-Lab Coyote Control Application - Flow 1", layout,  # background_color="#43414e",
#                        margins=(0, 0), element_padding=(0, 0), background_color=flow_background_color,
#                        no_titlebar=False)  # no_titlebar=True, size=(800, 550), margins=(50, 50)
#
#     return window
#
#
# def make_flow_window_two():
#     text_messages = [ctm("Start the DG-Lab Coyote intermediary server", font="bold", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("", font="bold", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("This program connects to the DG-Lab Coyote via an intermediary server program.\n\nMore specifically, the coyote communicates with the server via Bluetooth, and the\nserver communicates with user GUI (this program) via HTTP/Websocket.\n\nThe server needs to run on a computer with Bluetooth 4.2+ capability.\n\nIf this computer has Bluetooth capability and you intend to connect to the coyote\ndirectly from it, press the 'Start server locally (default)' button below and then click\n'continue'. This is the default use-case for most people.", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("If you are a power user and already running the server program on a different device,\nclick 'continue' instead. Be prepared to enter the relevant IP address and port.", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("If you have already started the server separately", color=flow_text_color, bg_color=flow_background_color),
#                      # ctm("(on another device, for example), press skip this step.", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("", color=flow_text_color, bg_color=flow_background_color)]
#
#     # "\n\nE-stim safely.\nThe developers disavow any liability\nstemming"
#     #     " from the use of this software.\n\nNEVER E-STIM ABOVE THE CHEST.\nEtc.", "Turn on your Coyote",
#     #     "Connect to your Coyote via the bluetooth server. If you've already done so, skip to the next step.",
#     #     "Equip your electrodes."
#     #     "Done!"
#
#     # Create empty column layout list
#     column_layout = []
#
#     # Add the text lines individually as Text (labels)
#     for text in text_messages:
#         column_layout.append([text])
#
#     # Add buttons
#     column_layout.append([  # sg.Push(background_color="#43414e"),
#         sg.Button('Start server locally (default)', bind_return_key=True, size=(None, 5), expand_x=True, expand_y=True),
#         sg.Button('(fixme:) Continue', bind_return_key=False, size=(None, 5), expand_x=True, expand_y=True),
#         # sg.Button('Cancel', size=(None, 2), expand_x=False)
#     ])
#
#     #
#     # # Add tick box to disable on-boarding for next time
#     # # todo: Add at the end!
#     # column_layout.append([
#     #     sg.CBox(text="Don't show guide next time.", text_color="#FFFFFF", checkbox_color="#43414e", background_color="#43414e")
#     # ])
#
#     # set column element size
#     width, height = 400, 550
#
#     # Set padding for column element
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = 150, 50
#
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = int(height/2), 50
#
#     pad_left, pad_right = 20, 20
#     pad_top, pad_bottom = 50, 20
#
#     column = sg.Column(layout=column_layout, pad=((pad_left, pad_right), (pad_top, pad_bottom)),
#                        vertical_alignment="bottom", expand_x=True, background_color=flow_background_color)
#
#     layout = [[sg.Image(filename="media/coyote_3.png", size=(width, height), subsample=4),
#                column]]  # background_color="#62697B"
#
#     # Create the window
#     window = sg.Window("DG-Lab Coyote Control Application - Flow 2", layout, margins=(0, 0), element_padding=(0, 0),
#                        background_color=flow_background_color,
#                        no_titlebar=False)  # no_titlebar=True, size=(800, 550), margins=(50, 50)
#
#     return window
#
#
# def make_flow_window_three():
#     text_messages = [ctm("Electrodes", font="bold", color=flow_text_color, bg_color=flow_background_color), ctm("Put on your e-stim electrodes and connect the cable to the device.", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("(Don't worry, this program won't zap you without your express permission.)", color=flow_text_color, bg_color=flow_background_color), ctm("", color=flow_text_color, bg_color=flow_background_color),
#                      ctm("Click continue to continue.", color=flow_text_color, bg_color=flow_background_color), ctm("", color=flow_text_color, bg_color=flow_background_color), ctm("", color=flow_text_color, bg_color=flow_background_color)]
#
#     # "\n\nE-stim safely.\nThe developers disavow any liability\nstemming"
#     #     " from the use of this software.\n\nNEVER E-STIM ABOVE THE CHEST.\nEtc.", "Turn on your Coyote",
#     #     "Connect to your Coyote via the bluetooth server. If you've already done so, skip to the next step.",
#     #     "Equip your electrodes."
#     #     "Done!"
#
#     # Create empty column layout list
#     column_layout = []
#
#     # Add the text lines individually as Text (labels)
#     for text in text_messages:
#         column_layout.append([text])
#
#     # Add buttons
#     column_layout.append([  # sg.Push(background_color="#43414e"),
#         sg.Button('Continue', bind_return_key=True, size=(None, 5), expand_x=True, expand_y=True),
#         # sg.Button('Skip', bind_return_key=False, size=(None, 5), expand_x=True, expand_y=True),
#         # sg.Button('Cancel', size=(None, 2), expand_x=False)
#     ])
#
#     #
#     # # Add tick box to disable on-boarding for next time
#     # # todo: Add at the end!
#     # column_layout.append([
#     #     sg.CBox(text="Don't show guide next time.", text_color="#FFFFFF", checkbox_color="#43414e", background_color="#43414e")
#     # ])
#
#     # set column element size
#     width, height = 400, 550
#
#     # Set padding for column element
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = 150, 50
#
#     # pad_left, pad_right = 50, 20
#     # pad_top, pad_bottom = int(height/2), 50
#
#     pad_left, pad_right = 20, 20
#     pad_top, pad_bottom = 50, 20
#
#     column = sg.Column(layout=column_layout, pad=((pad_left, pad_right), (pad_top, pad_bottom)),
#                        vertical_alignment="bottom", expand_x=True, background_color=flow_background_color)
#
#     layout = [[sg.Image(filename="media/eggplant.png", subsample=3, size=(width, height)),
#                column]]  # background_color="#62697B"
#
#     # Create the window
#     window = sg.Window("DG-Lab Coyote Control Application - Flow 3", layout, margins=(0, 0), element_padding=(0, 0),
#                        background_color=flow_background_color,
#                        no_titlebar=False)  # no_titlebar=True, size=(800, 550), margins=(50, 50)
#
#     return window
#
#
# def make_connect_window():
#     # Define the window's contents
#     layout = [
#
#         [sg.Image(filename="media/000232-bluetooth-logo.png", subsample=16, expand_x=True),
#          # sg.Text("Connection graphic arrows placeholder", expand_x=True),
#          sg.Image(filename="media/coyote_3.png", subsample=4, expand_x=True, key="-COYOTE_IMG-")],
#
#         # [
#         #     # todo: use sg.Output() instead
#         #     sg.Multiline(autoscroll=True, auto_refresh=True, expand_x=True,
#         #                  size=(None, 3), no_scrollbar=True, focus=False, disabled=True, background_color="tan")
#         # ],
#
#         [sg.HorizontalSeparator()],
#
#         [sg.Text("Turn on your Coyote and click Connect."), sg.Image(sg.EMOJI_BASE64_HAPPY_THUMBS_UP)],
#
#         [sg.Button("Connect automatically", size=(40, 2), bind_return_key=True, key="-CONNECT_BUTTON-"),
#          sg.Button("Connect manually\nvia UUID", size=(20, 2), bind_return_key=True, key="-CONNECT_MAN_BUTTON-"),
#          # todo: This really shouldn't be a separate button.
#          sg.Button("Continue", disabled=True, size=(20, 2), key="-CONNECT_CONTINUE_BUTTON-"),
#          sg.VerticalSeparator(pad=(20, 0)), sg.Button("Back", size=(20, 2))],
#
#     ]
#
#     window = sg.Window("DG-Lab Coyote Control Application - Connection Wizard", layout=layout,
#                        element_justification="left")
#     return window
#
#
# def make_adv_settings_window():
#     layout = [[sg.Text("Hey this is the advanced setup section. TODO.")], [sg.Button("Back", bind_return_key=True)]]
#
#     window = sg.Window("DG-Lab Coyote Control Application - Advanced Setup", layout=layout, size=(800, 600))
#
#     return window
#
#
# def make_main_window():
#     # layout = [[sg.Text("Hello there lol")],
#     #           [sg.Button("Back", bind_return_key=True)],
#     #           [sg.Button("Quit")]]
#
#     layout = [[sg.Slider(), sg.Slider()],
#
#               [sg.Button("STOP", size=(None, 5))],
#
#               [sg.Button("Load audio file (WAV)")],
#
#               [sg.Canvas(size=(200, 200))],
#
#               [sg.Listbox(values=["placeholder", "placeholder_2"])],
#
#               [sg.Button("Quit", size=(20, 2))]
#
#               ]
#
#     window = sg.Window("DG-Lab Coyote Control Application - Main", layout, size=(800, 600))
#     return window
#
#
#
# def onboard_main():
#     # Create startup window
#     window = make_startup_window()
#
#     # Display and interact with the Window using an Event Loop
#     # Main loop
#     # User switches windows by creating new window instances and closing the old ones.
#     while True:
#         event, values = window.read()  # timeout=1000
#         print(event, values)
#
#         # Global
#         # See if user wants to quit or window was closed. This triggers for all "Quit"-named buttons in the program.
#         if event == sg.WINDOW_CLOSED or event == 'Quit':  # "Quit" button alias just used directly here as command, lol.
#             # Breaking will end the program.
#             break
#
#         # Startup window
#         if window.Title == "DG-Lab Coyote Control Application - Start":
#             if event == "Connect and play with DG-Lab Coyote":
#                 window.close()
#                 # window = make_connect_window()
#                 window = make_flow_window_one()
#             if event == "Try out program\nwithout device":
#                 window.close()
#                 window = make_adv_settings_window()
#
#         if window.Title == "DG-Lab Coyote Control Application - Flow 1":
#             if event == "Continue":
#                 window.close()
#                 window = make_flow_window_two()
#
#         if window.Title == "DG-Lab Coyote Control Application - Flow 2":
#             if event == "(fixme:) Continue":
#                 window.close()
#                 window = make_flow_window_three()
#             if event == "Start server locally (default)":
#                 print("subprocess call to separate server executable here, please!")
#
#                 executable = ["python", "../server_gui/server_gui.py"]
#
#                 arguments = []
#
#                 # Execute the server cli
#                 pid = subprocess.Popen(executable + arguments, bufsize=1, env=os.environ.copy(),
#                                        shell=True, cwd="../server_gui/").pid  # for some reason, shell=False yields a modulenotfound error when running the script, probably because the virtual environment isn't being set correctly. Weird.
#
#
#                 # Give process time to start.
#                 # time.sleep(5)
#                 # Continue to next step
#                 # window.close()
#                 # window = make_flow_window_three()
#
#
#         if window.Title == "DG-Lab Coyote Control Application - Flow 3":
#             if event == "Continue":
#                 window.close()
#                 window = make_main_window()
#
#         # Main window  (After successful connection)
#         if window.Title == "DG-Lab Coyote Control Application - Main":
#             if event == "Back":
#                 window.close()
#                 window = make_startup_window()
#
#         # Advanced Setup window
#         if window.Title == "DG-Lab Coyote Control Application - Advanced Setup":
#             if event == "Back":
#                 window.close()
#                 window = make_startup_window()
#
#         # Connection wizard
#         if window.Title == "DG-Lab Coyote Control Application - Connection Wizard":
#             if event == "Back":
#                 window.close()
#                 window = make_startup_window()
#             if event == "-CONNECT_BUTTON-":
#                 window["-COYOTE_IMG-"].update(filename="media/coyote_3_white_2.png", subsample=4)
#                 # Set button to disabled after pressing once.
#                 window["-CONNECT_BUTTON-"].update(disabled=True)
#                 window["-CONNECT_MAN_BUTTON-"].update(disabled=True)
#
#                 window["-CONNECT_CONTINUE_BUTTON-"].update(disabled=False)
#
#             if event == "-CONNECT_CONTINUE_BUTTON-":
#                 window.close()
#                 window = make_main_window()
#
#     # Finish up by removing from the screen
#     window.close()
#
#
#
#
# #####################



if __name__ == "__main__":

    # flow_text_color = "#FFF"
    # flow_background_color = "#43414e"
    #
    # onboard_main()
    # raise Exception()

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

    


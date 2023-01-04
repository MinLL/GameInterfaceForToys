from pathlib import Path
import yaml
from common.util import *
from common.constants import EVENTS_YAML, EVENTS_PATH
import events.functions
import settings
from events.event import Event

class EventLoader:
    def _parse_arg(self, arg):
        arg = arg.replace('{GIFT_ACTOR_NAME}', settings.CHARACTER_NAME)
        arg = arg.replace('{CHASTER_DEFEAT_MIN}', str(settings.CHASTER_DEFEAT_MIN))
        arg = arg.replace('{CHASTER_DEFEAT_MAX}', str(settings.CHASTER_DEFEAT_MAX))
        return arg
    
    def _parse_event(self, event, path):
        path = path.replace("/","_")
        path = path.replace("\\", "_")
        name = list(event.keys())[0]
        name_key = "{}_{}".format(path, list(event.keys())[0])
        if not 'function' in event[name]:
            fail("    Could not load event {}: Missing function".format(name))
            return None
        function = event[name]['function']
        if not hasattr(self.interface, function):
            fail("    Function {} is not defined in interface.")
            return None
        function = getattr(self.interface, function)
        if not 'regex' in event[name]:
            fail("    Could not load event {}: Missing regex".format(name))
            return None
        regex = self._parse_arg(event[name]['regex'])
        group = 'group' in event[name] and event[name]['group'] or 'default'
        case_sensitive = 'case_sensitive' in event[name] and event[name]['case_sensitive'] or True
        params = 'params' in event[name] and event[name]['params'] or None
        origin = " ".join(path.split("_")[3:])
        shortname = list(event.keys())[0]
        return Event(name_key, regex, function, group, case_sensitive, params, origin, shortname)


    def _load_events(self, path):
        info("Loading {}".format(path))
        if not path in self.event_files:
            fail("  Could not find {}".format(path))
            return
        events = self.event_files[path]
        if events is None:
            fail("  {} is an empty file or otherwise could not be parsed.".format(path))
            return
        for event in events:
            event = self._parse_event(event, path)
            if event is not None:
                success("  Loaded event: {}".format(event.name))
                self.events.append(event)


    def __init__(self, interface):
        self.interface = interface
        self.event_files = {}
        self.events = []
        if settings.IS_WINDOWS:
            events_yaml_path = EVENTS_YAML.replace("/", "\\")
        else:
            events_yaml_path = EVENTS_YAML
        info("Discovering event yaml files...")
        for path in Path('data/events').rglob('*.yaml'):
            success("  Found: {}".format(str(path)))
            self.event_files[str(path)] = yaml.safe_load(path.read_text())
        if not events_yaml_path in self.event_files:
            fail("Could not find {} - Aborting event load".format(events_yaml_path))
            return
        self.mapping = self.event_files[events_yaml_path]
        if self.mapping is None:
            fail("{} is empty or otherwise could not be loaded.".format(events_yaml_path))
            return
        for game in  self.mapping['games']:
            for k, v in game.items():
                if v is None:
                    continue
                for event_file in v:
                    path = "{}/games/{}/{}".format(EVENTS_PATH, k, event_file)
                    if settings.IS_WINDOWS:
                        path = path.replace("/", "\\")
                    self._load_events(path)


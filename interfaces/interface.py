from interfaces.toy_interface import ToyInterface
import settings
from common.util import *
import io
import yaml
from events.eventloader import EventLoader

class Interface(object):
    def __init__(self, name, toy_type):
        self.name = name
        self.toys = ToyInterface(toy_type)

    def shutdown(self):
        return self.toys.shutdown()

    def setup(self):
        self.event_loader = EventLoader(self)
        if settings.CHASTER_ENABLED:
            from toys.chastity.chaster.chaster import ChasterInterface
            self.chaster = ChasterInterface(settings.LOCK_NAME, self.toys)
            self.chaster.setup()
        return self.load_toy_list()

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

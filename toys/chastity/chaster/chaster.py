import requests
from common.util import *
from common.constants import *
import random

class ChasterInterface(object):
    def __init__(self, lock_name, developer_token, toys):
        self.toys = toys
        self.lock_name = lock_name
        self.token = developer_token
        self.api_root = "https://api.chaster.app/"
        self.extensions = {}
        self.enabled = True
        self.random_toys = ["a plug", "clamps", "wrist cuffs"]
        self.wheel_hooks = {
            'slsi_shock1': self.slsi_shock1,
            'slsi_shock2': self.slsi_shock2,
            'slsi_dice': lambda: "Dice Game: {}".format(self.roll_dice()),
            'slsi_gear': lambda: "Gear Task: {}".format(self.assign_task("Match your characters bondage outfit for {} minutes.".format(random.choice([60, 120, 180])))),
            'slsi_plug': lambda: "Plug Task: {}".format(self.assign_task("Insert a plug and keep it there for at least {} minutes.".format(random.choice([60, 90, 120, 180])))),
            'slsi_clamps': lambda: "Clamp Task: {}".format(self.assign_task("Wear your clamps for at least {} minutes.".format(random.choice[15, 20, 25]))),
            'slsi_shibari': lambda: "Shibari Task: {}".format(self.assign_task("Wear a {} for the rest of the day.".format(random.choice(["body harness", "crotch rope", "chest harness"])))),
            'slsi_bodywriting': lambda: "Body Writing Task: {}".format(self.assign_task("....")),
            'slsi_ice': lambda: "Ice Task: {}".format(self.assign_task("Hold an icecube in or against your {} until it melts.".format(random.choice(["cage", "nipples", "mouth", "bellybutton"])))),
            'slsi_squats': lambda: "Squat Task: {}".format(self.assign_task("Do {} squats while wearing {}.".format(random.randint(20, 30), random.choice(self.random_toys)))),
            'slsi_situps': lambda: "Situp Task: {}".format(self.assign_task("Do {} situps while wearing {}.".format(random.randint(20, 30), random.choice(self.random_toys)))),
            'slsi_overstimulate': self.overstimulate,
            'slsi_tease': self.tease,
        }

    def slsi_shock1(self):
        return self.toys.shock(5, 80)

    def slsi_shock2(self):
        return self.toys.shock(10, 100)
    
    def overstimulate(self):
        return self.toys.vibrate_plus(random.randint(300, 600) , 100)

    def tease(self):
        return self.toys.vibrate(240, 5)
        

    def setup(self):
        try:
            self.select_lock(self.lock_name)
        except Exception as e:
            fail(str(e))
            fail("Failed to initialize chaster. Disabling for this run.")
            self.enabled = False
            return
        
    def _api(self, method, endpoint, data={}):
        if not self.enabled:
            raise Exception("Chaster is disabled.")
        headers = {
            "Authorization": "Bearer " + self.token,
            "accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "SkyrimToyInterface {}".format(VERSION)
        }
        if method == "GET":
            return requests.get(self.api_root + endpoint, headers=headers, timeout=10)
        elif method == "POST":
            return requests.post(self.api_root + endpoint, headers=headers, json=data, timeout=10)
        else:
            raise FatalException("Unsupported method type to ChasterInterface")


    def _get_locks(self):
        r = self._api("GET", "locks?status=active")
        try:
            if r.status_code == 401:
                fail("User is unauthorized to fetch list of locks (Is your token valid?)")
                raise FatalException("Invalid Chaster Token")
            if r.status_code != 200:
                fail("Failed to fetch lock status: " + str(r.json()))
                return
            return r.json()
        except Exception as e:
            fail(r.text)
            raise e
        
    def select_lock(self, lock_name):
        info("select_lock({})".format(lock_name))
        locks = self._get_locks()
        lock_found = False
        for lock in locks:
            if lock['title'] == lock_name:
                if (lock_found):
                    raise FatalException("Found more than one lock matching name. Archive unused locks!")
                lock_found = lock
        if not lock_found:
            raise FatalException("Failed to find lock matching name: " + str(lock_name))
        self.lock = lock_found
        success("  Found lock: " + lock_name)
        success("  Status: " + lock['status'])
        success("  Role: " + lock['role'])
        info("Processing extensions...")
        for extension in self.lock['extensions']:
            success("  Found [{}] extension".format(extension['slug']))
            self.extensions[extension['slug']] = extension
        return lock_found
    
    def update_time(self, duration):
        info("update_time({})".format(duration))
        r = self._api("POST", "locks/{}/update-time".format(self.lock["_id"]), {"duration": duration})
        if r.status_code != 204:
            fail("  Failed to update lock time: Status code {}: {}".format(r.status_code, str(r.json())))
            return
        success("  Updated lock duration by {} seconds.".format(duration))

    def _run_extension(self, extension, foo):
        try:
            payload = foo()
            url = "locks/{}/extensions/{}/action".format(self.lock['_id'], self.extensions[extension]['_id'])
            info("Running {} on extension {}".format(payload['action'], extension))
            r = self._api("POST", url, foo())
            if r.status_code == 201:
                success("  Extension executed successfully.")
            else:
                fail("  Failed to execute extension ({}): {}".format(r.status_code, r.text))
            return r
        except KeyError:
            fail("  Extension {} not enabled for lock {}".format(extension, self.lock['title']))
    
    def assign_task(self, task, points=0):
        beep()
        return self._run_extension(extension="tasks", foo=lambda: {
            'action': 'assignTask',
            'payload':{
                'task': {
                    'task': task,
                    'points': points
                }
            }
        })

    def roll_dice(self):
        r = self._run_extension(extension="dice", foo=lambda: {
            'action': 'submit',
            'payload': {}
        })
        success("    Outcome: Changed lock duration by {} minutes".format(str((int(r.json()['duration'])) / 60)))
        return r

    def spin_wheel(self):
        r = self._run_extension(extension="wheel-of-fortune", foo=lambda: {
            'action': 'submit',
            'payload': {}
        })
        response = r.json()['text']
        if response in self.wheel_hooks.keys():
            response = self.wheel_hooks[response]()
        success("    Outcome: {}".format(response))
        return response


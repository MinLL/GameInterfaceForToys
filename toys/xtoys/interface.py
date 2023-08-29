from toys.base import Toy, FEATURE_VIBRATOR, FEATURE_ESTIM
from common.util import *
import asyncio
import json
import random
import settings
import httpx

# Will move these to config later.
xtoys_base_url = "https://webhook.xtoys.app"

class XToysInterface(Toy):
    def __init__(self, tags=[]):
        self.patterns = self.load_patterns()
        self.client = httpx.AsyncClient()
        super().__init__("XToys Interface", [FEATURE_VIBRATOR, FEATURE_ESTIM] + tags)

    def load_patterns(self):
        with open("data/vibrators/pattern_dict.json") as pf:
            patterns = json.loads(pf.read())
        return patterns
    
    def action(self, params):
        pattern = ""
        if "pattern" in params:
            original_pattern = params['pattern'].split(";")
            pattern = original_pattern[0]
            if pattern == "random":
                pattern = random.choice([x for x in self.patterns.keys()])
                info("random - selected: {}".format(pattern))
            if pattern not in self.patterns:
                pattern = ""
            original_pattern[0] = pattern
            pattern = ";".join(original_pattern)
        if params['action'] == 'vibrate_plus':
            return self.vibrate_plus(params['duration'], params['strength'], pattern, params['toys'])
        elif params['action'] == 'vibrate':
            return self.vibrate(params['duration'], params['strength'], pattern, params['toys'])
        elif params['action'] == 'shock':
            return self.shock(params['duration'], params['strength'], pattern, params['toys'])

    async def vibrate(self, duration, strength, pattern="", toys=[]):
        if len(toys) == 0:
            action = 'vib_vaginal'
            return await self._invoke_webhook(settings.XTOYS_WEBHOOK_ID, action, {"time": duration, "intensity": strength, "pattern": pattern})
        ret = []
        for toy in toys:
            ret += [await self._invoke_webhook(settings.XTOYS_WEBHOOK_ID, toy['id'], {"time": duration, "intensity": strength, "pattern": pattern})]
        return ret

    async def vibrate_plus(self, duration, strength, pattern="", toys=[]):
        return await self.vibrate(duration, strength, pattern, toys)

    async def shock(self, duration, strength, pattern="", toys=[]):
        if len(toys) == 0:
            action = 'shock_a'
            return await self._invoke_webhook(settings.XTOYS_WEBHOOK_ID, action, {"time": duration, "intensity": strength, "pattern": pattern})
        ret = []
        for toy in toys:
            ret += [await self._invoke_webhook(settings.XTOYS_WEBHOOK_ID, toy['id'], {"time": duration, "intensity": strength, "pattern": pattern})]
        return ret

    async def _invoke_webhook(self, webhook, action, params):
        url = "{}?id={}&action={}".format(xtoys_base_url, webhook, action)
        for k, v in params.items():
            url += "&{}={}".format(k, v)
        info("Invoking webhook: {}".format(url))
        r = await self.client.get(url)
        if r.status_code != 200 or r.text != 'OK':
            fail(r.text)
            raise Exception("Call to XToys failed: Error code {}".format(r.status_code))
        success("Webhook invocation complete. Status code={}, response={}".format(r.status_code, r.text))
        return r
        
    async def stop(self):
        return await self._invoke_webhook(settings.XTOYS_WEBHOOK_ID, "stop", {})

    def get_toys(self):
        return {
            "Vib Vaginal": {
                'interface': self.properties['name'],
                'name': 'Vib Vaginal',
                'id': 'vib_vaginal',
                'battery': -1,
                'enabled': True
            },
            "Vib Anal": {
                'interface': self.properties['name'],
                'name': 'Vib Anal',
                'id': 'vib_anal',
                'battery': -1,
                'enabled': True
            },
            "Vib Clit": {
                'interface': self.properties['name'],
                'name': 'Vib Clit ',
                'id': 'vib_clit',
                'battery': -1,
                'enabled': True
            },
            "Vib Nipples": {
                'interface': self.properties['name'],
                'name': 'Vib Nipples',
                'id': 'vib_nipples',
                'battery': -1,
                'enabled': True
            },
            "Shock A": {
                'interface': self.properties['name'],
                'name': 'Shock A',
                'id': 'shock_a',
                'battery': -1,
                'enabled': True
            },
            "Shock B": {
                'interface': self.properties['name'],
                'name': 'Shock B',
                'id': 'shock_b',
                'battery': -1,
                'enabled': True
            }
        }

    def connect(self):
        return

    def check_in(self):
        return

    def shutdown(self):
        pass

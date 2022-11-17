from toys.base import Toy, FEATURE_VIBRATOR
import json
import io

class Vibrator(Toy):
    def __init__(self, name, tags=[]):
        self.patterns = self.load_patterns()
        super().__init__("Default Vibrator", [FEATURE_VIBRATOR] + tags)

    def load_patterns(self):
        with open("data/vibrators/pattern_dict.json") as pf:
            patterns = json.loads(pf.read())
        return patterns
    
    def action(self, params):
        pattern = ""
        if "pattern" in params:
            pattern = params['pattern']
            if pattern == "random":
                pattern = random.choice([x for x in self.patterns.keys()])
                info("random - selected: {}".format(pattern))
        if params['plus']:
            return self.vibrate_plus(params['duration'], params['strength'], pattern)
        else:
            return self.vibrate(params['duration'], params['strength'], pattern)

    def vibrate(self, duration, strength, pattern=""):
        pass

    def vibrate_plus(self, duration, strength, pattern=""):
        return self.vibrate(duration, strength, pattern)

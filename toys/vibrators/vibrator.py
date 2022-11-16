from toys.base import Toy, FEATURE_VIBRATOR
import json
import io

class Vibrator(Toy):
    def __init__(self, name):
        self.patterns = self.load_patterns()
        super().__init__("Default Vibrator", [FEATURE_VIBRATOR])

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
        return self.vibrate(params['duration'], params['strength'], pattern)

    def vibrate(self, duration, strength):
        pass

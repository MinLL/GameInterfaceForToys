from toys.base import Toy, FEATURE_ESTIM
import json
import io
import random
from common.util import *

class Estim(Toy):
    def load_patterns(self):
        with open("toys/estim/pattern_dict.json") as pf:
            patterns = json.loads(pf.read())
            for k, v in patterns.items():
                pattern_list = []
                for pattern in v:
                    with open("toys/estim/patterns/{}".format(pattern)) as psf:
                        pattern_list.append(json.loads(psf.read()))
                patterns[k] = pattern_list
        patterns[""] = [[[10, 90, 10]],  # Default pattern - simple, one-state pattern of 10 ms pulse, 90 ms pause, amplitude 10
                        [[5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20],
                         [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 95, 20],  [4, 86, 20], [4, 76, 20],
                         [4, 66, 20], [3, 57, 20], [3, 37, 20], [3, 37, 20], [2, 28, 20], [2, 18, 20], [1, 14, 20],
                         [1, 9, 20]]  # varied pattern of 20 states
                        ]
        return patterns
    
    def __init__(self, name):
        self.patterns = self.load_patterns()
        super().__init__("Default Estim", [FEATURE_ESTIM])

    def action(self, params):
        pattern = params['pattern']
        if pattern == "random":
            pattern = random.choice([x for x in self.patterns.keys()])
            info("random - selected: {}".format(pattern))
        return self.shock(params['duration'], params['strength'], pattern)

    def shock(self, duration, strength, pattern=""):
        pass

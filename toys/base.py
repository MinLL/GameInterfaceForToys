# 
# This module defines a common interface for toys. Some toy types will extend this.


FEATURE_VIBRATOR = "vibrator"
FEATURE_ESTIM = "estim"
FEATURE_CHASTITY = "chastity"
FEATURE_EDGE = "edge"

class Toy:
    def __init__(self, name, features=[], min_strength=0, max_strength=100):
        self.properties = {
            "name": name,
            "features": features, # List of types this toy supports.
            "min_strength": min_strength,
            "max_strength": max_strength,
        }

    def connect(self):
        pass

    def check_in(self):
        pass
    
    def action(self, parameters):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass

    def get_toys(self):
        pass

from toys.base import Toy, FEATURE_VIBRATOR

class Vibrator(Toy):
    def __init__(self, name):
        super().__init__("Default Vibrator", [FEATURE_VIBRATOR])

    def action(self, params):
        return self.vibrate(params['duration'], params['strength'])

    def vibrate(self, duration, strength):
        pass

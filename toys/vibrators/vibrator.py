from toys.base import Toy, FEATURE_VIBRATOR

class Vibrator(Toy):
    def __init__(self, name):
        super().__init__("Lovense", [FEATURE_VIBRATOR])

    def action(self, params):
        self.vibrate(params['duration'], params['strength'])

    def vibrate(self, duration, strength):
        pass

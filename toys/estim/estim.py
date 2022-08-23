from toys.base import Toy, FEATURE_ESTIM

class Estim(Toy):
    def __init__(self, name):
        super().__init__("Default Estim", [FEATURE_ESTIM])

    def action(self, params):
        return self.shock(params['duration'], params['strength'])

    def shock(self, duration, strength):
        pass

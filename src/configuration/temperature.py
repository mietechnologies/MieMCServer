from util.mielib import custominput as ci

class Temperature:
    data = {}
    elapsed = 0
    maximum = None
    minutes = None

    def __init__(self, data: dict) -> None:
        self.data = data
        self.elapsed = self.data.get('elapsed', 0)
        self.maximum = self.data.get('maximum', None)
        self.minutes = self.data.get('minutes', None)

    def build(self) -> dict:
        print('Because I\'m running on a Raspberry Pi, core temperature can be worrysome so I monitor my core temperature for you.')
        self.maximum = ci.int_input('So, how hot should I let myself get?', default=70)
        self.minutes = ci.int_input('And how many minutes should pass before I shut everything down?', default=3)
        return self.update()

    def exists(self):
        return self.data != {}

    def is_overheating(self, current_temp: float) -> bool:
        return current_temp >= self.maximum

    def update(self) -> dict:
        self.data['elapsed'] = self.elapsed
        self.data['maximum'] = self.maximum
        self.data['minutes'] = self.minutes
        return self.data


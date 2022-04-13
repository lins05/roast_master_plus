
names = {
    'Start': 'Start',
    'Yellowed': 'Yellow',
    'First crack': 'FC',
    'End': 'End',
}


class RoastEvent:
    def __init__(self, value):
        self.name = names.get(value, value)
        self.value = value

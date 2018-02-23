
class Event():
    EVENT_TIMER = 1
    EVENT_PACKET = 2

    def __init__(self, val_type, val_time, val_call):
        self.type = val_type
        self.time = val_time
        self.call = val_call

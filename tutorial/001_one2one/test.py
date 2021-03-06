from sender_terminal import SenderTerminal
from receiver_terminal import ReceiverTerminal
from radio import Radio
from event import Event
import copy
import unittest

import globals



class TestOne2one(unittest.TestCase):
    def test_normal(self):
        radio = Radio()
        t1 = SenderTerminal("t1", "00:00:00:00:00:01", "192.168.0.1", radio)
        t1.x = 100
        t1.y = 40
        radio.add_node(t1)

        t2 = ReceiverTerminal("t2", "00:00:00:00:00:02", "192.168.0.2", radio)
        t2.x = 100
        t2.y = -40
        radio.add_node(t2)

        globals.now = 0
        globals.events = sorted(globals.events, key=lambda x: x.time)

        while True:


            if len(globals.events) == 0:
                break

            globals.events = sorted(globals.events, key=lambda x:x.time)
            events_work = copy.copy(globals.events)
            event = globals.events[0]
            globals.now = event.time

            if globals.now > 10:
                break

                break

            for event in events_work:
                if event.time <= globals.now:
                    event.call()
                    globals.events.pop(0)
                else:
                    break

        self.assertEqual(250000, t2.total_received_byte * 8 / globals.now)


if __name__ == "__main__":
    unittest.main()


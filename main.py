from node import Node
from terminal import Terminal
from relay import Relay
from radio import Radio
from event import Event
import copy
import cfg

#initialize model
radio = Radio()
t1 = Terminal("t1", 100, 40, "00:00:00:00:00:01", "192.168.0.1", radio, 1, 2)
radio.add_node(t1)
t2 = Terminal("t2", 100, -40, "00:00:00:00:00:02", "192.168.0.2", radio, 1, 1)
radio.add_node(t2)
t3 = Terminal("t3", -100, 40, "00:00:00:00:00:03", "192.168.0.3", radio, 1, 1)
radio.add_node(t3)
t4 = Terminal("t4", -100, -40, "00:00:00:00:00:04", "192.168.0.4", radio, 1, 1)
radio.add_node(t4)

r1 = Relay("r1", 40, 0, "00:00:00:00:10:01", "192.168.10.1", radio, 1, 2)
radio.add_node(r1)
r1.add_entry_to_routing_table("192.168.0.1", "00:00:00:00:00:01")
r1.add_entry_to_routing_table("192.168.0.2", "00:00:00:00:00:02")
r1.add_entry_to_routing_table("192.168.0.3", "00:00:00:00:10:02")
r1.add_entry_to_routing_table("192.168.0.4", "00:00:00:00:10:02")

r2 = Relay("r2", -40, 0, "00:00:00:00:10:02", "192.168.10.2", radio, 1, 2)
radio.add_node(r2)
r2.add_entry_to_routing_table("192.168.0.1", "00:00:00:00:10:01")
r2.add_entry_to_routing_table("192.168.0.2", "00:00:00:00:10:02")
r2.add_entry_to_routing_table("192.168.0.3", "00:00:00:00:00:03")
r2.add_entry_to_routing_table("192.168.0.4", "00:00:00:00:00:04")

cfg.now = 0
cfg.events = sorted(cfg.events, key=lambda x: x.time)

while True:
    if len(cfg.events) == 0:
        break

    cfg.events = sorted(cfg.events, key=lambda x:x.time)
    events_work = copy.copy(cfg.events)

    for event in events_work:
        if event.time <= cfg.now:
            if event.type == Event.EVENT_TIMER:
                event.call()
            elif event.type == Event.EVENT_PACKET:
                pass

            cfg.events.pop(0)
        else:
            cfg.now = event.time
            break


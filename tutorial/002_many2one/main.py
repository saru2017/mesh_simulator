import copy

from sender_terminal import SenderTerminal
from receiver_terminal import ReceiverTerminal
from radio import Radio
from event import Event
import globals
import numpy.random

numpy.random.seed(0)


#initialize model
radio = Radio()

t1 = ReceiverTerminal("t1", "00:00:00:00:00:01", "192.168.0.1", radio)
t1.x = 0
t1.y = 0
radio.add_node(t1)

t2 = SenderTerminal("t2", "00:00:00:00:00:02", "192.168.0.2", radio)
t2.x = 350
t2.y = 0
t2.one_lambda = 0.01
radio.add_node(t2)

t3 = SenderTerminal("t3", "00:00:00:00:00:03", "192.168.0.3", radio)
t3.x = 350
t3.y = 0
t3.one_lambda = 0.01
radio.add_node(t3)

t4 = SenderTerminal("t4", "00:00:00:00:00:04", "192.168.0.4", radio)
t4.x = 350
t4.y = 0
t4.one_lambda = 0.01
radio.add_node(t4)

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
        break;

    for event in events_work:
        if event.time <= globals.now:
            event.call()
            globals.events.pop(0)
        else:
            break

throughput = t1.total_received_byte * 8 / globals.now / 10**6
print("throughput = %f Mbps" % (throughput))

for key, value in t1.throughputs.items():
    print("%s is %d bytes" % (key, value))


for key, value in t1.dictIpError.items():
    print("%s's packets are  %d/%d" % (key, value, t1.dictIpSeq[key]))
    print("%s's error rate is %f" % (key, value / t1.dictIpSeq[key]))

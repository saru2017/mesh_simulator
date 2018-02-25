from event import Event
from packet import Packet
from enum import auto
from numpy.random import *
import globals
import sys

class SenderTerminal():
    def __init__(self, val_id, val_mac, val_ip, val_radio):
        self.id = val_id
        self.mac = val_mac
        self.ip = val_ip
        self.radio = val_radio

        self.state = "STATE_LISTENING"
        self.interference = {}
        self.packet_queue = []
        self.one_lambda = 0.01 #packet sending interval
        self.target_mac = "00:00:00:00:00:02"
        self.target_ip  = "192.168.0.2"
        self.length = 1500
        self.phy_speed = 250 * 1000 # 250 kbps
        self.channel = 1 # for future purpose

        event = Event(self.one_lambda * rand(), self.on_generate_packet)
        globals.events.append(event)


    def send_packet(self, packet):
        #send to radio propagation model
        print("    send_packet")
        self.radio.input_to_radio(packet)



    def start_sending_packet(self, packet):
        packet.type = "TYPE_START"
        self.sending_packet = packet
        self.state = "STATE_SENDING"
        self.send_packet(packet)
        packet_time = packet.length * 8 / self.phy_speed
        event = Event(globals.now + packet_time, self.on_timer)
        globals.events.append(event)



    def on_timer(self):
        #timer is fired and do something
        print("%0.3f: node %s: on timer" % (globals.now, self.id))
        if self.state == "STATE_SENDING":
            str = "end packet from node %s" % (self.id)
            self.sending_packet.type = "TYPE_END"
            self.send_packet(self.sending_packet)
            if len(self.packet_queue) > 0:
                packet = self.packet_queue.pop(0)
                self.start_sending_packet(packet)
            else:
                self.state = "STATE_LISTENING"
        else:
            print("impossibl state = %s" % (self.state))
            sys.exit()


    def on_generate_packet(self):
        print("%0.3f: node %s: on generate_packet" % (globals.now, self.id))
        str = "original packet %s" % (self.id)
        dst_mac = self.target_mac = "00:00:00:00:00:02"
        dst_ip = "192.168.0.2"
        packet = Packet(self.id, 255, self.x, self.y,
                        dst_mac, dst_ip, self.mac, self.ip,
                        self.channel, 10, str, "TYPE_ORIGINAL")
        packet.length = 1500
        packet.phy_speed = 250 * 1000
        if len(self.packet_queue) < 10:
            self.packet_queue.append(packet)

        if self.state == "STATE_LISTENING":
            packet = self.packet_queue.pop(0)
            self.start_sending_packet(packet)
        elif self.state == "STATE_SENDING":
            pass
        else:
            print("not implemented state: %s" % self.state)
            sys.exit()

        event = Event(globals.now + self.one_lambda, self.on_generate_packet)
        globals.events.append(event)



    def on_receive_packet(self, packet, val_rssi):
        if packet.dst_mac == Packet.bcast_mac or packet.dst_mac == self.mac:
            print("        mac: on_receive_packet from %s" % (packet.dst_mac))
        else:
            print("        mac: this is not mine to %s" % (packet.dst_mac))

        if packet.dst_ip == self.ip:
            print("        net: on_receive_ip_packet from %s" % (packet.dst_ip))



    def on_receive_radio(self, packet, val_rssi):
        print("%0.3f: node %s: on_receive_signal at %0.3f [dBm]" % \
                  (globals.now, self.id, val_rssi))
        print("    ignore all signals.")

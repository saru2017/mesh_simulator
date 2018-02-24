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
        self.max_noise = {}
        self.packet_queue = []
        self.one_lambda = 1 #packet sending interval
        self.target_mac = "00:00:00:00:00:02"
        self.target_ip  = "192.168.0.2"
        self.length = 1500
        self.speed = 250 * 1000 # 250 kbps
        self.channel = 1 # for future purpose

        event = Event(self.one_lambda * rand(), self.on_generate_packet)
        globals.events.append(event)


    def send_packet(self, packet):
        #send to radio propagation model
        print("    send_packet")
        self.radio.input_to_radio(packet)

    def start_sending_packet(self, packet):
        self.sending_packet = packet
        self.state = "STATE_SENDING"
        self.send_packet(packet)
        packet_time = packet.length * 8 / self.speed
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
                start_send_packet(packet)
                self.state = "STATE_SENDING"
            else:
                self.state = "STATE_LISTENING"
        elif self.state == "STATE_RECEIVING":
            print("impossibl state = %s" % (self.state))
            sys.exit()
        elif self.state == "STATE_SENDING":
            print("impossibl state = %s" % (self.state))
            sys.exit()
        else:
            print("impossibl state = %s" % (self.state))
            sys.exit()


    def on_generate_packet(self):
        str = "original packet %s" % (self.id)
        dst_mac = self.target_mac = "00:00:00:00:00:02"
        dst_ip = "192.168.0.2"
        packet = Packet(self.id, 255, self.x, self.y,
                        dst_mac, dst_ip, self.mac, self.ip,
                        self.channel, 10, str, "TYPE_ORIGINAL")
        packet.length = 1500
        packet.phy_speed = 250 * 1000
        self.packet_queue.append(packet)
        if self.state == "STATE_LISTENING":
            packet = self.packet_queue.pop(0)
            packet.type = "TYPE_START"
            self.start_sending_packet(packet)
        elif self.state == "STATE_RECEIVING":
            pass
        elif self.state == "STATE_SENDING":
            pass

        event = Event(globals.now + self.one_lambda, self.on_generate_packet)
        print("event time = %f" % (event.time))
        print("state = %s" % (self.state))
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
        print("    packet is from %s: %s" % (packet.src_mac, packet.src_ip))
        print("    packet payload =  %s" % (packet.payload))
        print("    packet type = %s" % (packet.type))

        if packet.src_mac == self.mac:
            return # ignore self interference

        #interference calculation
        if packet.type == "TYPE_START":
            self.interference[packet.src_mac] = val_rssi
        elif packet.type == "TYPE_END":
            del self.interference[packet.src_mac]

        if self.state == "STATE_LISTENING":
            if packet.type == Packet.TYPE_PACKET_START and \
                    packet.dst_mac == self.mac:
                max_interference = -92 # -92 is noise floor
                for key, val in self.interference:
                    if key == packet.src_mac:
                        continue

                    if max_interference < val:
                        max_interference = val

                sinr = val_rssi - max_interference
                if sinr >= 20.2: #packet detection is succeeded.
                    self.state = RECEIVING
                    self.receiving_mac = packet.src_mac
                    self.max_receiving_interference = max_interference

        elif self.state == "STATE_RECEIVING":
            if packet.dst_mac == receiving_mac:
                sinr = val_rssi - self.max_receiving_interference
                print("        sinr = %f" % (sinr))
                if sinr >= 20.2:
                    self.on_receive_packet(packet, val_rssi)
                else:
                    print("        packet_drop")
                pass
            else:
                if self.max_receving_itnerference < val_rssi:
                    self.max_receiving_interference = val_rssi
        elif self.state == "STATE_SENDING":
            pass # ignore packet while sending
        else:
            print("not implemented %s %d" % (self.state, len(self.state)))
            sys.exit()

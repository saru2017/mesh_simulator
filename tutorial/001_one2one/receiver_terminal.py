from event import Event
from packet import Packet
import sys
import globals
from enum import auto

class ReceiverTerminal():
    def __init__(self, val_id, val_mac, val_ip, val_radio):
        self.id = val_id
        self.mac = val_mac
        self.ip = val_ip
        self.radio = val_radio
        self.state = "STATE_LISTENING"
        self.interference = {}
        self.max_receiving_interference = -92 #-92 is noise floor
        self.total_received_byte = 0
        self.channel = 1 # for future purpose
        self.receiving_mac = None



    def on_receive_packet(self, packet, val_rssi):
        if packet.dst_mac == Packet.bcast_mac or packet.dst_mac == self.mac:
            print("        mac: on_receive_packet from %s" % (packet.dst_mac))
        else:
            print("        mac: this is not mine to %s" % (packet.dst_mac))

        if packet.dst_ip == self.ip:
            print("        net: on_receive_ip_packet from %s" % (packet.dst_ip))
            self.total_received_byte += packet.length
            print("        net: total_received_byte is %d" % \
                      (self.total_received_byte))
            speed = self.total_received_byte * 8 / globals.now / 10**6
            print("        net: speed = %f Mbps" % (speed))



    def on_receive_radio(self, packet, val_rssi):
        print("    %0.3f: node %s: on_receive_signal at %0.3f [dBm]" % \
                  (globals.now, self.id, val_rssi))
        print("        packet is from %s: %s" % (packet.src_mac, packet.src_ip))
        print("        packet payload =  %s" % (packet.payload))

        if packet.src_mac == self.mac:
            return # ignore self interference

        #interference calculation
        if packet.type == "TYPE_START":
            self.interference[packet.src_mac] = val_rssi
        elif packet.type == "TYPE_END":
            del self.interference[packet.src_mac]

        print("state = %s" % (self.state))
        print("packet.dst_mac = %s" % (packet.dst_mac))
        print("packet.dst_ip = %s" % (packet.dst_ip))

        if self.state == "STATE_LISTENING":
            if packet.type == "TYPE_START" and packet.dst_mac == self.mac:
                max_interference = -92 # -92 is noise floor
                for key, val in self.interference.items():
                    if key == packet.src_mac:
                        continue

                    if max_interference < val:
                        max_interference = val

                sinr = val_rssi - max_interference
                if sinr >= 20.2: #packet detection is succeeded.
                    self.state = "STATE_RECEIVING"
                    self.receiving_mac = packet.src_mac
                    self.max_receiving_interference = max_interference

        elif self.state == "STATE_RECEIVING":
            if packet.src_mac == self.receiving_mac:
                sinr = val_rssi - self.max_receiving_interference
                print("        sinr = %f" % (sinr))
                if sinr >= 20.2:
                    self.on_receive_packet(packet, val_rssi)
                else:
                    print("        packet_drop")
                pass
            else:
                if self.max_receiving_interference < val_rssi:
                    self.max_receiving_interference = val_rssi
        else:
            print("not implemented %s " % (self.state))
            sys.exit()

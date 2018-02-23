from node import Node
from event import Event
from packet import Packet
import copy
import cfg

class Relay(Node):
    STATE_NORMAL = 1
    STATE_SENDING = 2

    def __init__(self, val_id, val_x, val_y, val_mac, val_ip,
                 val_radio, val_channel, t):
        super().__init__(val_id, val_x, val_y, val_mac, val_ip,
                         val_radio, val_channel)
#        event = Event(Event.EVENT_TIMER, t, self.on_timer)
#        cfg.events.append(event)
        self.state = Relay.STATE_NORMAL
        self.interference = {}
        self.max_noise = {}
        self.routing_table = {}



    def send_packet(self, packet):
        #send to radio propagation model
        print("    send_packet")
        self.radio.input_to_radio(packet)



    def on_timer(self):
        #timer is fired and do something
        print("%0.3f: node %s: on timer" % (cfg.now, self.id))
        if self.state == Relay.STATE_SENDING:
            self.sending_packet.type = Packet.TYPE_PACKET_END
            self.sending_packet.payload = "end packet from node %s" % (self.id)
            self.send_packet(self.sending_packet)


    def get_mac_from_routing_table(self, ip):
        return self.routing_table[ip]



    def add_entry_to_routing_table(self, ip, mac):
        self.routing_table[ip] = mac


    def on_receive_packet(self, packet, val_rssi):
        print("    on_receive_packet")
        if packet.dst_mac != self.mac:
            print("    drop the packet: mac is different")
            return

        dst_mac = self.get_mac_from_routing_table(packet.dst_ip)
        self.sending_packet = copy.copy(packet)
        self.sending_packet.dst_mac = dst_mac
        self.sending_packet.src = self.id
        self.sending_packet.src_mac = self.mac
        self.sending_packet.type = Packet.TYPE_PACKET_START
        self.sending_packet.payload = "start packet from node %s" % (self.id)
        self.send_packet(self.sending_packet)
        print("    sending: %s" % (self.sending_packet.payload))
        event = Event(Event.EVENT_TIMER, cfg.now + 0.1, self.on_timer)
        cfg.events.append(event)
        self.state = Relay.STATE_SENDING



    def on_receive_signal(self, packet, val_rssi):
        print("%0.3f: node %s: on_receive_signal at %0.3f [dBm]" % (cfg.now, self.id, val_rssi))
        print("    packet payload =  %s" % (packet.payload))
        if packet.src == self.id:
            #do nothing
            pass
        elif packet.dst == 255 or packet.dst == self.id:
            if packet.type == Packet.TYPE_PACKET_START:
                #do something
                self.interference[packet.src] = val_rssi
                for key in self.max_noise:
                    val = self.max_noise[key]
                    if val < val_rssi:
                        self.max_noise[key] = val_rssi

                self.max_noise[packet.src] = -92 #this is default noise floor
            elif packet.type == Packet.TYPE_PACKET_END:
                sinr = val_rssi - self.max_noise[packet.src]
                del self.interference[packet.src]
                del self.max_noise[packet.src]
                print("    sinr = %f" % (sinr))
                if sinr >= 20.2:
                    self.on_receive_packet(packet, val_rssi)
                else:
                    print("    packet_drop")

        print("    interference: %s" % (self.interference))


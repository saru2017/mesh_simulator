from node import Node
from event import Event
from packet import Packet
import cfg

class Terminal(Node):
    STATE_NORMAL = 1
    STATE_SENDING = 2

    def __init__(self, val_id, val_x, val_y, val_mac, val_ip,
                 val_radio, val_channel, t):
        super().__init__(val_id, val_x, val_y, val_mac, val_ip,
                         val_radio, val_channel)
        event = Event(Event.EVENT_TIMER, t, self.on_timer)
        cfg.events.append(event)
        self.state = Terminal.STATE_NORMAL
        self.interference = {}
        self.max_noise = {}



    def send_packet(self, packet):
        #send to radio propagation model
        print("    send_packet")
        self.radio.input_to_radio(packet)



    def on_timer(self):
        #timer is fired and do something
        print("%0.3f: node %s: on timer" % (cfg.now, self.id))
        if self.state == Terminal.STATE_NORMAL:
            str = "start packet from node %s" % (self.id)
            packet_type = Packet.TYPE_PACKET_START
            if self.id == "t4":
                dst_mac = "00:00:00:00:10:02"
                dst_ip = "192.168.0.1"

            if self.id == "t4":
                packet = Packet(self.id, 255, self.x, self.y,
                                dst_mac, dst_ip, self.mac, self.ip,
                                self.channel, 10, str, packet_type)
                self.send_packet(packet)

            event = Event(Event.EVENT_TIMER, cfg.now + 0.1, self.on_timer)
            cfg.events.append(event)
            self.state = Terminal.STATE_SENDING
        elif self.state == Terminal.STATE_SENDING:
            str = "end packet from node %s" % (self.id)
            packet_type = Packet.TYPE_PACKET_END
            if self.id == "t4":
                dst_mac = "00:00:00:00:10:02"
                dst_ip = "192.168.0.1"

            if self.id == "t4":
                packet = Packet(self.id, 255, self.x, self.y,
                                dst_mac, dst_ip, self.mac, self.ip,
                                self.channel, 10, str, packet_type)
                self.send_packet(packet)

            event = Event(Event.EVENT_TIMER, cfg.now + 0.3, self.on_timer)
            cfg.events.append(event)
            self.state = Terminal.STATE_NORMAL


    def on_receive_packet(self, packet, val_rssi):
        if packet.dst_mac == Packet.bcast_mac or packet.dst_mac == self.mac:
            print("    on_receive_packet")
        else:
            print("    this is not mine")

        if packet.dst_ip == self.ip:
            print("    on_receive_ip_packet")


    def on_receive_signal(self, packet, val_rssi):
        print("%0.3f: node %s: on_receive_signal at %0.3f [dBm]" % (cfg.now, self.id, val_rssi))
        print("    packet is from %s: %s" % (packet.src_mac, packet.src_ip))
        print("    packet payload =  %s" % (packet.payload))
        if packet.src == self.id:
            #do nothing
            pass
        else:
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


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
        self.one_lambda = 1.00 #packet sending interval
        self.target_mac = "00:00:00:00:00:01"
        self.target_ip  = "192.168.0.1"
        self.length = 1500
        self.phy_speed = 250 * 1000 # 250 kbps
        self.channel = 1 # for future purpose
        self.seq = 1

        event = Event(self.one_lambda * rand(), self.onGeneratePacket)
        globals.events.append(event)


    def sendPacket(self, packet):
        #send to radio propagation model
        print("    send %s packet to %s" % (packet.type, packet.dst_mac))
        self.radio.inputToRadio(packet)



    def startSending(self, packet):
        packet.type = "TYPE_START"
        self.sending_packet = packet
        self.state = "STATE_SENDING"
        self.sendPacket(packet)
        packet_time = packet.length * 8 / self.phy_speed
        event = Event(globals.now + packet_time, self.onTimer)
        globals.events.append(event)



    def onTimer(self):
        #timer is fired and do something
        print("%0.3f: node %s: on timer %s" % (globals.now, self.id, self.state))
        if self.state == "STATE_LISTENING":
            print("impossibl state = %s" % (self.state))
            sys.exit()
        elif self.state == "STATE_SENDING":
            self.onTimerSending()
        else:
            print("impossibl state = %s" % (self.state))
            sys.exit()




    def onTimerSending(self):
        str = "end packet from node %s" % (self.id)
        self.sending_packet.type = "TYPE_END"
        self.sendPacket(self.sending_packet)
        self.checkRemainingPacket()



    def checkRemainingPacket(self):
        if len(self.packet_queue) > 0:
            packet = self.packet_queue.pop(0)
            self.startSending(packet)
        else:
            self.state = "STATE_LISTENING"



    def onGeneratePacket(self):
        print("%0.3f: node %s: on generate_packet" % (globals.now, self.id))
        str = "original packet %s" % (self.id)
        dst_mac = self.target_mac
        dst_ip = self.target_ip
        packet = Packet(self.id, 255, self.x, self.y,
                        dst_mac, dst_ip, self.mac, self.ip,
                        self.channel, 10, str, "TYPE_ORIGINAL")
        packet.length = 1500
        packet.phy_speed = 250 * 1000
        packet.seq = self.seq
        self.seq += 1
        if len(self.packet_queue) < 10:
            self.packet_queue.append(packet)

        if self.state == "STATE_LISTENING":
            self.checkRemainingPacket()
        elif self.state == "STATE_SENDING":
            pass
        else:
            print("not implemented state: %s" % self.state)
            sys.exit()

        t = globals.now + self.one_lambda * rand() * 2
        event = Event(t, self.onGeneratePacket)
        globals.events.append(event)



    def onReceivePacket(self, packet, val_rssi):
        if packet.dst_mac == Packet.bcast_mac or packet.dst_mac == self.mac:
            print("        mac: onReceivePacket from %s" % (packet.dst_mac))
        else:
            print("        mac: this is not mine to %s" % (packet.dst_mac))

        if packet.dst_ip == self.ip:
            print("        net: on_receive_ip_packet from %s" % (packet.dst_ip))



    def onReceiveRadio(self, packet, val_rssi):
        print("    %0.3f: node %s: on_receive_signal at %0.3f [dBm]" % \
                  (globals.now, self.id, val_rssi))
        if packet.src_mac == self.mac:
            return # ignore self interference

        #interference calculation
        if packet.type == "TYPE_START":
            self.interference[packet.src_mac] = val_rssi
        elif packet.type == "TYPE_END":
            del self.interference[packet.src_mac]



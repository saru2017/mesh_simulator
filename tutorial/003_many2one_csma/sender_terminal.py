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

        # MAC parameters
        self.macMinBE = 3
        self.macMaxBE = 5
        self.macMaxFrameRetries = 3
        self.macMaxCSMABackoffs = 4
        self.aUnitBackoffPeriod = 20/250000
        self.CCA_THR = -72
        self.BE = self.macMinBE
        self.NB = 0

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



    def startBackoff(self, packet):
        self.sending_packet = packet
        self.state = "STATE_BACKOFF"
        self.backoff_counter = 2**self.BE - 1
        event = Event(globals.now + self.aUnitBackoffPeriod, self.onTimer)
        globals.events.append(event)



    def onTimer(self):
        #timer is fired and do something
        print("%0.3f: node %s: on timer %s" % (globals.now, self.id, self.state))
        if self.state == "STATE_LISTENING":
            print("impossibl state = %s" % (self.state))
            sys.exit()
        elif self.state == "STATE_BACKOFF":
            self.onTimerBackoff()
        elif self.state == "STATE_SENDING":
            self.onTimerSending()
        else:
            print("impossibl state = %s" % (self.state))
            sys.exit()



    def onTimerBackoff(self):
        # backoff_counter is remaining
        if self.backoff_counter > 0:
            self.backoff_counter -= 1
            event = Event(globals.now + self.aUnitBackoffPeriod, self.onTimer)
            globals.events.append(event)
            return

        # channel is clear. start to send a packet
        carrier = self.getSurroundingMaxRSSI()
        if carrier < self.CCA_THR:
            self.startSending(self.sending_packet)
            return

        # media busy
        self.NB += 1
        print("    media busy NB = %d" % (self.NB))

        # media busy continues a while, so drop the packet
        if self.NB > self.macMaxCSMABackoffs:
            print("    packet drop because of CCA failure")
            self.checkRemainingPacket()
            return

        # exponential backoff
        self.BE += 1
        if self.BE > self.macMaxBE:
            self.BE = self.macMaxBE
        self.backoff_counter = 2**self.BE - 1
        event = Event(globals.now + self.aUnitBackoffPeriod,
                      self.onTimer)
        globals.events.append(event)



    def onTimerSending(self):
        str = "end packet from node %s" % (self.id)
        self.sending_packet.type = "TYPE_END"
        self.sendPacket(self.sending_packet)
        self.checkRemainingPacket()



    def checkRemainingPacket(self):
        if len(self.packet_queue) > 0:
            packet = self.packet_queue.pop(0)
            self.BE = self.macMinBE
            self.NB = 0
            self.startBackoff(packet)
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
        elif self.state == "STATE_BACKOFF":
            pass
        elif self.state == "STATE_SENDING":
            pass
        elif self.state == "STATE_RECEIVING":
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


    def getSurroundingMaxRSSI(self):
        max_rssi = -92 # noise floor
        for val in self.interference.values():
            if val > max_rssi:
                max_rssi = val
        return max_rssi

from math import sqrt, log10

class Radio:
    def __init__(self):
        self.nodes = []


    def calcPropagation(self, val_power, d):
        # https://en.wikipedia.org/wiki/Log-distance_path_loss_model
        # gamma is 2 X_g is 0
        if d == 0:
            return val_power
        PL = 30 + 10 * 2 * log10(d) + 0
        return val_power - PL



    def inputToRadio(self, packet):
        # calc_radio_propagation
        # send to all node
        for node in self.nodes:
            if node.channel == packet.channel:
                d = sqrt((packet.x - node.x)**2 + (packet.y - node.y)**2)
                rssi = self.calcPropagation(packet.tx_power, d)
                node.onReceiveRadio(packet, rssi)



    def add_node(self, node):
        # add node with location (x, y)
        self.nodes.append(node)



class Node(object):
    def __init__(self, val_id, val_x, val_y, val_mac, val_ip,
                 val_radio, val_channel):
        self.id = val_id
        self.x = val_x
        self.y = val_y
        self.mac = val_mac
        self.ip = val_ip
        self.radio = val_radio
        self.channel = val_channel



    def on_receive_packet(self, packet):
        pass

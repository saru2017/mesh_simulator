class Packet:
    TYPE_PACKET_START = 1
    TYPE_PACKET_END = 2
    bcast_mac = "FF:FF:FF:FF:FF:FF"

    def __init__(self, val_src, val_dst, val_x, val_y,
                 val_dst_mac, val_dst_ip, val_src_mac, val_src_ip,
                 val_channel, val_tx_power, val_payload, val_type):
        self.src = val_src
        self.dst = val_dst
        self.x = val_x
        self.y = val_y
        self.dst_mac = val_dst_mac
        self.dst_ip = val_dst_ip
        self.src_mac = val_src_mac
        self.src_ip = val_src_ip
        self.channel = val_channel
        self.tx_power = val_tx_power
        self.payload = val_payload
        self.type = val_type

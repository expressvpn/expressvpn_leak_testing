# Packet format looks like this
# {
#     "DataType": 0,
#     "Raw": "",
#     "FirstSeen": "0001-01-01T00:00:00Z",
#     "LastSeen": "0001-01-01T00:00:00Z",
#     "TimeStamp": "2017-12-01T05:32:34.000806368Z",
#     "Iface": "6",
#     "Direction": "out",
#     "SourcePort": "65123",
#     "SourceIP": "172.16.49.173",
#     "DestPort": "53",
#     "DestIP": "27.50.70.139",
#     "Pname": "",
#     "Pid": ""
# }

class Packet:

    # pylint: disable=too-few-public-methods

    def __init__(self, packet):
        self._packet = packet

    def __str__(self):
        if not self._packet["Pname"]:
            self._packet["Pname"] = "Unknown"
        dst = "{DestIP}:{DestPort}".format(**self._packet)
        src = "{SourceIP}:{SourcePort}".format(**self._packet)
        if self._packet["Direction"] == "in":
            return "({src:20} <- {dst:>20}) Iface: {Iface}".format(src=src, dst=dst, **self._packet)
        return "({src:20} -> {dst:>20}) Iface: {Iface}, Pname: {Pname}".format(
            src=src, dst=dst, **self._packet)

class Packets:

    def __init__(self, packets):
        self._packets = packets

    def __str__(self):
        return self.str_no_dupes()

    def str_no_dupes(self):
        unique_packets = {}
        counts = {}

        match_keys = ['SourcePort', 'SourceIP', 'DestPort', 'DestIP']
        for packet in self._packets:
            hsh = ""
            for key in match_keys:
                if "IP" in key:
                    hsh += packet[key].exploded
                else:
                    hsh += packet[key]
            if hsh not in unique_packets:
                unique_packets[hsh] = packet
                counts[hsh] = 1
            else:
                counts[hsh] += 1

        ret = ""
        for hsh, packet in list(unique_packets.items()):
            ret += "{:5} Packet(s): {}\n".format(counts[hsh], Packet(packet))
        return ret

    def str_all(self):
        ret = ""
        for packet in self._packets:
            ret += str(Packet(packet))
        return ret

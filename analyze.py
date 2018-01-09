import json
import sys
import select
import socket
import math
from subprocess import Popen, PIPE
from collections import defaultdict

class location_server():
    WATCH_ADDR = 'cc:1c:60:a1:18:17'

    def __init__(self):
        self.northeast = None
        self.southeast = None
        self.southwest = None



    # only look for the watch right now
    def read_nodes(self):
        northeast = []
        southeast = []
        southwest = []

        for node, filename in zip([northeast, southeast, southwest], ['north.txt', 'south.txt', 'macbook.txt']):
            with open(filename) as f:
                for l in f.readlines():
                    try:
                        node.append(json.loads(l.strip()))
                    except:
                        continue

        return northeast, southeast, southwest

    def filter_by_addr(self, list, addr):
        return [x for x in list if x['packet']['AdvA']['addr'] == addr]

    def distance(self, rssi):
        n = 2.7
        return math.pow(10, (-40 - rssi)/(10*n))

    def start_listeners(self):
        #self.northeast = Popen("nc -l 8000", stdout=PIPE, shell=True)
        #self.southeast = Popen("nc -l 8001", stdout=PIPE, shell=True)
        #self.southwest = Popen("nc -l 8002", stdout=PIPE, shell=True)

        self.northeast2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.northeast2.setblocking(0)
        self.northeast2.bind(('', 8003))
        self.northeast2.listen(5)

    def keep_track(self):
        self.start_listeners()

        device_dict = defaultdict(dict)
        inputs = [self.northeast2]
        while inputs:
            readable, writable, exceptional = select.select(inputs, [], [])
            for s in readable:
                connection, addr = s.accept()
                line = connection.recv(1024).decode("ascii")
                if line:
                    print line
                    line = line.strip()
                    node = s.getsockname()[1]
                    try:
                        j = json.loads(line)
                    except:
                        continue
                    device_dict[j['packet']['AdvA']['addr']][node] = j['rssi']
                    print device_dict


serv = location_server()
serv.keep_track()


# ne, se, sw = read_nodes()

# for l in [ne, se, sw]:
#     for i in filter_by_addr(l, WATCH_ADDR):
#         # print i['systime'], i['packet']['type'], i['rssi']
#         print i['rssi'], distance(i['rssi'])
#     print ''



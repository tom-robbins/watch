import json
import sys
import math
from subprocess import Popen, PIPE
import fileinput

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
        self.northeast = Popen("nc -l 8000")
        self.southeast = Popen("nc -l 8001")
        self.southwest = Popen("nc -l 8002")

    def keep_track(self):
        self.start_listeners()
        device_dict = {}

        for line in fileinput.input(self.northeast.stdout, self.southeast.stdout, self.southwest.stdout):
            print line


serv = location_server()
serv.keep_track()


# ne, se, sw = read_nodes()

# for l in [ne, se, sw]:
#     for i in filter_by_addr(l, WATCH_ADDR):
#         # print i['systime'], i['packet']['type'], i['rssi']
#         print i['rssi'], distance(i['rssi'])
#     print ''



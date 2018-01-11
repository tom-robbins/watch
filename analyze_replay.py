import json
import sys
import math
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy


WATCH_ADDR = 'cc:1c:60:a1:18:17'
EQ_THRESHOLD = 0.000001
NODE_STRINGS = ['ne', 'se', 'sw']

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return 'Point: (%f, %f)' % (self.x, self.y)

class Circle:
    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r

    def __repr__(self):
        return 'Circle: center=(%f, %f) r=%f' % (self.x, self.y, self.r)

    def plot(self, ax, alpha=0.2, color='g'):
        ax.add_artist(plt.Circle((self.x, self.y), self.r, alpha=alpha, color=color))

NE = Point(1,2)
SE = Point(1,0)
SW = Point(0,0)

# only look for the watch right now
def read_nodes():
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

def filter_by_addr(list, addr):
    return [x for x in list if x['packet']['AdvA']['addr'] == addr]

def calc_distance_factor(rssi):
    n = 2.0
    return math.pow(10, (-60 - rssi)/(10*n))

def keep_track():
    self.start_listeners()

    device_dict = defaultdict(dict)
    inputs = [self.northeast2]
    while True:
        print inputs
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            if s == self.northeast2:
                # connection, addr = s.accept()
                line = receive(s)
                if line:
                    print line
                    line = line.strip()
                    node = s.getsockname()[1]
                    try:
                        j = json.loads(line)
                        device_dict[j['packet']['AdvA']['addr']][node] = j['rssi']
                        print device_dict
                    except:
                        pass

def peek_time(list):
    if len(list) > 0:
        return list[0]['systime']

def process():
    ne, se, sw = read_nodes()
    nodes = {'ne': ne, 'se': se, 'sw': sw}
    nodes = {s: filter_by_addr(nodes[s], WATCH_ADDR) for s in NODE_STRINGS}

    last_seen_dist = {'ne': 0, 'se': 0, 'sw': 0}

    timeseries = []
    t = min([peek_time(nodes[s]) for s in nodes])
    while any([nodes[s] for s in nodes]):
        for s in nodes:
            l = nodes[s]
            while len(nodes[s]) > 0 and peek_time(nodes[s]) <= t:
                i = nodes[s][0]
                nodes[s] = l[1:]
                if i['systime'] == t:
                    d = calc_distance_factor(i['rssi'])
                    last_seen_dist[s] = d
                    # print s, ": ", i['rssi'], d
        t += 1
        print last_seen_dist
        if not any([last_seen_dist[s] == 0 for s in NODE_STRINGS]):
            timeseries.append({k: last_seen_dist[k] for k in NODE_STRINGS})
    return timeseries

# return distance between 2 points
def distance(p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

# circles in form: (x - h)^2 + (y - k)^2 = r^2
# returns p1, p2 or False
# two intersection points of two circles, or False if they do not intersect
def two_circle_intersection(c1, c2):
    d = distance(Point(c1.x, c1.y), Point(c2.x, c2.y))

    if (((c1.r + c2.r) >= d) and (d >= abs(c1.r - c2.r))):
        # calculate area of (p1, p2, an intersection point)
        # herons formula
        a1 = d + c1.r + c2.r
        a2 = d + c1.r - c2.r
        a3 = d - c1.r + c2.r
        a4 = -d + c1.r + c2.r
        area = math.sqrt(a1 * a2 * a3 * a4) / 4

        # calculate intersection x values (ix)
        temp1 = (c1.x + c2.x) / 2 + (c2.x - c1.x) * (c1.r*c1.r - c2.r*c2.r) / (2*d*d)
        temp2 = 2 * (c1.y - c2.y) * area / (d*d);

        ix1 = temp1 + temp2
        ix2 = temp1 - temp2

        # calculate intersection y values (iy)
        temp1 = (c1.y + c2.y) / 2 + (c2.y - c1.y) * (c1.r*c1.r - c2.r*c2.r) / (2*d*d)
        temp2 = 2 * (c1.x - c2.x) * area / (d*d)

        iy1 = temp1 + temp2
        iy2 = temp1 - temp2

        # from http://www.ambrsoft.com/TrigoCalc/Circles2/circle2intersection/CircleCircleIntersection.htm
        # Because for every x we have two values of y, and the same thing for y,
        # we have to verify that the intersection points as chose are on the
        # circle otherwise we have to swap between the points
        test = abs((ix1 - c1.x) * (ix1 - ix1) + (iy1 - x1.y) * (iy1 - y1) - c1.r * c1.r)
        if (test > EQ_THRESHOLD):
            # point is not on the circle, swap between y1 and y2
            # the value of 0.0000001 is arbitrary chose, smaller values are also OK
            # do not use the value 0 because of computer rounding problems
            tmp = iy1
            iy1 = iy2
            iy2 = tmp

        # return the (x,y) coordinates for the two intersection points
        return Point(ix1, iy1), Point(ix2, iy2)
    else:
        # circles do not intersect
        return False

def two_circle_intersection2(c1, c2):
    dx = c2.x - c1.x
    dy = c2.y - c1.y

    d = distance(Point(c1.x, c1.y), Point(c2.x, c2.y))
    if d > (c1.r + c2.r):
        # no intersection case
        return False
    if d < abs(c1.r - c2.r):
        # super-circle case
        return False

    # p: point on line between centers and line between intersections
    # distance from center of c1 to p
    a = ((c1.r*c1.r) - (c2.r*c2.r) + (d*d)) / (2.0 * d)

    # trig
    px = c1.x + (dx * a/d)
    py = c1.y + (dy * a/d)

    # h: distance between intersections and p
    h = math.sqrt((c1.r*c1.r) - (a*a))

    # more trig
    rx = -1 * dy * (h / d)
    ry = dx * (h / d)

    # (barely) trig
    ix1 = px + rx
    ix2 = px - rx
    iy1 = py + ry
    iy2 = py - ry

    return Point(ix1, iy1), Point(ix2, iy2)

# circles in form: (x - h)^2 + (y - k)^2 = r^2
# returns intersection point
def three_circle_intersection(c1, c2, c3):
    # calculate intersection points of circles 1 and 2
    intersect_1, intersect_2 = two_circle_intersection2(c1, c2)
    # calculate distance to each intersection from circle 3's center
    c3_center = Point(c3.x, c3.y)
    d1 = distance(c3_center, intersect_1)
    d2 = distance(c3_center, intersect_2)

    if abs(d1 - c3.r) < EQ_THRESHOLD:
        return intersect_1
    elif abs(d2 - c3.r) < EQ_THRESHOLD:
        return intersect_2
    else:
        return False


# (x - h)^2 + (y - k)^2 = r^2
# returns Circle of center/radius form (above) of the circle
# formed by all points p s.t. dist(a, p) = dist1/dist2 * dist(b, p)
#
# note that dist1,2 are RELATIVE distances from the device to the antennas.
def k_ratio_circle(p1, dist1, p2, dist2):
    k = dist2 / dist1
    # translate p2's coordinates.  p1's coordinates are now (0,0)
    p2_t = Point(p2.x - p1.x, p2.y - p1.y)
    # we assume that antenna b is at (0,0) for simplicity
    # adding back the coordinates later to transform
    constant_c = (2*p2_t.x) / (1 - (k*k))
    constant_d = (2*p2_t.y) / (1 - (k*k))
    constant_e = (p2_t.x*p2_t.x + p2_t.y*p2_t.y) / (1 - (k*k))
    constant_r2 = ((constant_c*constant_c) / 4) + ((constant_d*constant_d) / 4) - constant_e
    # form: (x - h)^2 + (y - k)^2 = r^2

    # print k, constant_c, constant_d, constant_e, constant_r2

    # add back the translation to the 'real' coords of antenna b and sqrt(r^2)
    return Circle((constant_c / 2) + p1.x, (constant_d / 2) + p1.y, math.sqrt(constant_r2))

def get_circles(dist_ne, dist_se, dist_sw):
    ne_se_k_circle = k_ratio_circle(NE, dist_ne, SE, dist_se)
    se_sw_k_circle = k_ratio_circle(SE, dist_se, SW, dist_sw)
    sw_ne_k_circle = k_ratio_circle(SW, dist_sw, NE, dist_ne)
    print ne_se_k_circle, se_sw_k_circle, sw_ne_k_circle
    return ne_se_k_circle, se_sw_k_circle, sw_ne_k_circle

def find_point(dist_ne, dist_se, dist_sw):
    # find ratios of linear "distance"
    ne_se_k_circle = k_ratio_circle(NE, dist_ne, SE, dist_se)
    se_sw_k_circle = k_ratio_circle(SE, dist_se, SW, dist_sw)
    sw_ne_k_circle = k_ratio_circle(SW, dist_sw, NE, dist_ne)
    intersection_point = three_circle_intersection(
         ne_se_k_circle, se_sw_k_circle, sw_ne_k_circle
    )
    return intersection_point, ne_se_k_circle, se_sw_k_circle, sw_ne_k_circle

def save_plot(filename):
    plt.xlim([-2,2])
    plt.ylim([-1,3])
    fig.savefig(filename + '.png')
    plt.cla()

# scipy cookbook https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
def smooth(x, window_len=10, window='hanning'):
    x = numpy.array(x)
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s = numpy.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

# test circle intersection code
# print three_circle_intersection(
#     -2.0, 0.0, 2.0,
#     1.0, 0.0, 1.0,
#     0.0, 4.0, 4.0
# )

# plotting setup code
fig, ax = plt.subplots()

# analyzing code
points = []
ts_dicts = process()
ts_lists = [[ts_dicts[i][s] for i in range(len(ts_dicts))] for s in NODE_STRINGS]
ts_lists = [smooth(l, window_len=5) for l in ts_lists]
for i in ts_lists:
    print i
l = len(ts_lists)
for i in range(len(ts_lists[0])):
    cur_signals = [ts_lists[j][i] for j in range(l)]
    print 'VALUES: '+ ' '.join([str(x) for x in cur_signals])
    try:
        p, c1, c2, c3 = find_point(*cur_signals)
    except:
        pass
    else:
        for c in get_circles(*cur_signals):
            c.plot(ax)
        points.append(p)
        plt.plot([(p.x, p.y)], color='r', alpha=1)
        save_plot('plots/plot_%d' % i)

# for t in ts_dicts:
#     print t

for p in points:
    print p

plt.scatter(*zip(*[(p.x, p.y) for p in points]), color='r', alpha=1)
save_plot('plots/0')











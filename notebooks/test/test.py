import functools
import heapq
import random
from typing import List

from sortedcontainers import SortedSet

class Point:

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self.x = x
        self.y = y

    def add_intersecting_lines(self, line1:'Line', line2:'Line'):
        self.line1=line1
        self.line2=line2

    def get_y(self, x):
        return self.y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return self.x.__hash__()*self.y.__hash__()

    def __gt__(self, other):
        return isinstance(other, Point) and self.x > other.x

    def __ge__(self, other):
        return isinstance(other, Point) and self.x >= other.x

    def __le__(self, other):
        return isinstance(other, Point) and self.x <= other.x

    def __lt__(self, other):
        return isinstance(other, Point) and self.x < other.x

    def to_tuple(self):
        return self.x, self.y


def det_3x3(a: Point, b: Point, c: Point):
    a = (a.x, a.y, 1)
    b = (b.x, b.y, 1)
    c = (c.x, c.y, 1)
    return a[0] * b[1] * c[2] + a[1] * b[2] * c[0] + a[2] * b[0] * c[1] - a[2] * b[1] * c[0] - a[1] * b[0] * c[2] - a[
        0] * b[2] * c[1]


def orient(a: Point, b: Point, c: Point, epsilon=10e-10):
    det = det_3x3(a, b, c)
    if det > epsilon:
        return 1
    if det < -epsilon:
        return -1
    else:
        return det


class Line:

    def __init__(self, p0: Point, p1: Point) -> None:
        super().__init__()
        if p0.x < p1.x:
            self.p0 = p0
            self.p1 = p1
        else:
            self.p0 = p1
            self.p1 = p0

    def get_left(self):
        return self.p0

    def get_right(self):
        return self.p1

    def get_slope(self):
        return (self.p1.y - self.p0.y) / (self.p1.x - self.p0.x)

    def get_b(self):
        return self.p1.y - self.get_slope() * self.p1.x

    def get_y(self, x: float):
        return self.get_slope() * x + self.get_b()

    def check_colinearity(self, line: 'Line'):
        a1 = self.get_slope()
        b1 = self.get_b()
        a2 = line.get_slope()
        b2 = line.get_b()
        return a1 != a2 and b1 != b2

    def to_tuple(self):
        return self.get_left().to_tuple(), self.get_right().to_tuple()


def generate_lines(lower_left: Point = Point(0, 0), upper_right: Point = Point(10, 10), amount=10):
    lines = []
    for i in range(0, amount):
        p0 = Point(random.uniform(lower_left.x, upper_right.x), random.uniform(lower_left.y, upper_right.y))
        p1 = Point(random.uniform(lower_left.x, upper_right.x), random.uniform(lower_left.y, upper_right.y))
        if p0.y == p1.y:
            i = i - 1
            continue
        lines.append(Line(p0, p1))
    lines.sort(key=lambda l: l.get_slope())
    lines_distinct = [lines[0]]
    for i in range(1, len(lines)):
        if lines[i - 1].check_colinearity(lines[i]):
            lines_distinct.append(lines[i])
    return lines_distinct


def line_intersection(line1: Line, line2: Line):
    xdiff = line1.get_left().x - line1.get_right().x, line2.get_left().x - line2.get_right().x
    ydiff = line1.get_left().y - line1.get_right().y, line2.get_left().y - line2.get_right().y

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1.to_tuple()), det(*line2.to_tuple()))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    if line1.get_left().x < x < line1.get_right().x and \
            line2.get_left().x < x < line2.get_right().x:
        point = Point(x,y)
        point.add_intersecting_lines(line1, line2)
        return point
    return None


class SweepLineStatus:
    def __init__(self):
        super().__init__()
        self.lines:SortedSet = None
        self.events: List[Point] = []
        self.scenes = scenes
        self.dataset = {}
        self.results = set([])

    def comparator(self, line1: Line, line2:Line):
        result = line1.get_y(self.x) - line2.get_y(self.x)
        if abs(result) < 0.001:
            result = line1.get_slope() - line2.get_slope()
            if abs(result) < 0.001:
                return 0
            elif result < 0:
                return -1
            else:
                return 1
        elif result < 0:
            return -1
        else:
            return 1

    def run(self, dataset: List[Line]):
        for l in dataset:
            self.dataset[l.get_left()] = l
            self.dataset[l.get_right()] = l
            self.events.append((l.get_left()))
            self.events.append((l.get_right()))
        heapq.heapify(self.events)
        self.x = self.events[0].x
        self.lines = SortedSet(key=functools.cmp_to_key(self.comparator))
        while self.events:
            event = heapq.heappop(self.events)
            self.event_happened(event)
        return self.results

    def find_intersection(self, line1: Line, line2: Line):
        return line_intersection(line1, line2)

    def insert_line(self, line: Line):
        self.lines.add(line)
        i = self.lines.index(line)

        if i - 1 >= 0 and i + 1 < len(self.lines):
            intersection = self.find_intersection(self.lines[i - 1], self.lines[i + 1])
            if intersection is not None and intersection in self.events:
                self.events.remove(intersection)
                heapq.heapify(self.events)
        if i - 1 >= 0:
            intersection = self.find_intersection(self.lines[i - 1], line)
            if intersection is not None and intersection not in self.results:
                heapq.heappush(self.events, intersection)
        if i + 1 < len(self.lines):
            intersection = self.find_intersection(line, self.lines[i + 1])
            if intersection is not None and intersection not in self.results:
                heapq.heappush(self.events, intersection)

    def remove_line(self, line: Line):
        i = self.lines.bisect_left(line)
        j = self.lines.bisect_right(line)
        i = self.lines.index(line)
        if i - 1 >= 0 and i + 1 < len(self.lines):
            intersection = self.find_intersection(self.lines[i - 1], self.lines[i + 1])
            if intersection is not None and intersection not in self.results:
                heapq.heappush(self.events, intersection)
        self.lines.remove(line)

    def intersection_event(self, intersection: Point):
        self.results.add(intersection)
        line1 = intersection.line1
        line2 = intersection.line2

        self.remove_line(line1)
        self.remove_line(line2)

        self.x = intersection.x+0.01

        self.insert_line(line1)
        self.insert_line(line2)
        print(intersection.to_tuple())

    def event_happened(self, event: Point):
        if event in self.dataset:
            line = self.dataset[event]
            if event == line.get_left():
                self.x = event.x
                self.insert_line(line)
            else:
                self.remove_line(line)
        else:
            self.intersection_event(event)



scenes = []
sweep = SweepLineStatus()
dataset = generate_lines()
result = sweep.run(dataset)
dataset_array = list(map(lambda l: l.to_tuple(), dataset))
result_array = list(map(lambda p: p.to_tuple(), result))

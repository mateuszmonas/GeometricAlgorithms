import functools
import functools
import random
from cmath import acos
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
from matplotlib.widgets import Button
import json as js


def generate_on_square(amount_on_sides=25, amount_on_diagonal=20, lower_left=(0, 0), upper_right=(10, 10)):
    points = []
    l = upper_right[0] - lower_left[0]
    for i in range(0, amount_on_sides):
        p = random.uniform(0, l)
        x = lower_left[0]
        y = lower_left[1] + p
        points.append((x, y))
    for i in range(0, amount_on_sides):
        p = random.uniform(0, l)
        x = lower_left[0] + p
        y = lower_left[1]
        points.append((x, y))
    for i in range(0, amount_on_diagonal):
        p = random.uniform(lower_left[0], upper_right[0])
        points.append((p, p))
    for i in range(0, amount_on_diagonal):
        p = random.uniform(lower_left[0], upper_right[0])
        x = lower_left[0]
        points.append((upper_right[0] - lower_left[0] - p, p))
    return points


def filter_lowest_y_x(a, b):
    if a[1] < b[1]:
        return a
    if a[1] > b[1]:
        return b
    if a[0] < b[0]:
        return a
    return b


def det_2x2(v1, v2):
    return v1[0] * v2[1] - v2[0] * v1[1]


def orient(a, b, c):
    z = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    # left turn
    if z > 0:
        return 1
    # right turn
    if z < 0:
        return -1
    return 0


def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def length(v):
    return np.sqrt(dot_product(v, v))


def cosinus(v1, v2):
    if length(v1) == 0 or length(v2) == 0:
        return 2
    return np.arccos(dot_product(v1, v2) / (length(v1) * length(v2)))


def get_vector(a, b):
    return b[0] - a[0], b[1] - a[1]

def angle_comparator(a, b, c):
    if a == b:
        return -1
    if a == c:
        return 1
    det1 = det_3x3(a, b, c, pow(10, -10))
    det2 = det_3x3(a, c, b, pow(10, -10))
    if det1 == det2:
        if length(get_vector(a, b)) > length(get_vector(a, c)):
            return -1
        else:
            return 1
    if det1 > 0:
        return -1
    return 1

def graham(dataset):
    P = functools.reduce(lambda a, b: filter_lowest_y_x(a, b), dataset)
    temp = sorted(dataset, key=functools.cmp_to_key(lambda a, b: angle_comparator(P, a, b)))
    dataset_distinct = [temp[0], temp[1]]
    for i in range(2, len(temp)):
        det1 = det_3x3(P, temp[i-1], temp[i], pow(10, -10))
        det2 = det_3x3(P, temp[i], temp[i-1], pow(10, -10))
        if det1!=det2:
            dataset_distinct.append(temp[i])

    stack = []
    stack.append(dataset_distinct[0])
    stack.append(dataset_distinct[1])
    stack.append(dataset_distinct[2])
    i = 3
    t = 2
    while i < len(dataset_distinct):
        if det_3x3(stack[t - 1], stack[t], dataset_distinct[i], pow(10, -10)) > 0:
            stack.append(dataset_distinct[i])
            t += 1
            i += 1
        else:
            stack.pop()
            t -= 1
    return stack


def det_3x3(a, b, c, epsilon=0):
    ca = (c[0] - a[0], c[1] - a[1])
    cb = (c[0] - b[0], c[1] - b[1])
    det = ca[0] * cb[1] - ca[1] * cb[0]
    if det > epsilon:
        return 1
    if det < -epsilon:
        return -1
    else:
        return det



def find_min_angle(a, b, c):
    det1 = det_3x3(a, b, c, pow(10, -10))
    det2 = det_3x3(a, c, b, pow(10, -10))
    if det1 == det2:
        if length(get_vector(a, b)) > length(get_vector(a, c)):
            return b
        else:
            return c
    if det1 > 0:
        return b
    return c


def jarvis(dataset):
    P = functools.reduce(lambda a, b: filter_lowest_y_x(a, b), dataset)
    P0 = P
    stack = []
    stack.append(P)
    while True:
        P1 = functools.reduce(lambda a, b: find_min_angle(P0, a, b), dataset)
        P0 = P1
        stack.append(P1)
        if P1 == P:
            break
    return stack


dataset = generate_on_square()
plt.plot(*zip(*dataset), 'ro')
plt.show()
asd = graham(dataset)
plt.plot(*zip(*asd), 'ro')
plt.show()
print(asd)

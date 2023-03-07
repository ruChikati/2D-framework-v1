
import random

import pygame

from general_funcs import Vector2, magnitude, normalize_list, read_json


def load(filename):
    data = read_json(filename)
    return data['points'], data['sticks']


class ClothPoint:

    def __init__(self, pos, prev_pos, locked):
        self.pos = Vector2(pos)
        self.prev_pos = Vector2(prev_pos)
        self.locked = locked


class ClothStick:

    def __init__(self, index1, index2, length):
        self.index1 = index1
        self.index2 = index2
        self.length = length


class Cloth2:

    def __init__(self, points, sticks):
        self.points = points  # list([[int, int], [int, int], bool])
        for i, p in enumerate(self.points):
            self.points[i] = ClothPoint(*p)
        self.sticks = sticks  # list([int, int, float]) where int is an index in points
        for i, s in enumerate(self.sticks):
            self.sticks[i] = ClothStick(*s)
        self.paused = False

    def render(self, surf, point_radius, stick_width, colour=(0, 0, 0)):
        points = self.points
        random.shuffle(points)
        for point, stick in zip(points, self.sticks):
            pygame.draw.circle(surf, colour, point.pos, point_radius)
            pygame.draw.line(surf, colour, self.points[stick.index1].pos, self.points[stick.index2].pos, stick_width)

    def run(self, surf, dt, g=9.81):
        if not self.paused:
            points = self.points
            random.shuffle(points)
            # TODO: redo cloth sim with Vector2
        self.render(surf, 5, 3)

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False


class Cable2:

    def __init__(self, points):
        self.points = points  # list([int, int])

    def move(self, points, target):
        # uses FABRIK algorithm
        origin = points[0]
        segment_lengths = []

        for i in range(len(points) - 1):
            segment_lengths.append(magnitude([points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]]))

        for i in range(100):
            forwards = i % 2
            points.reverse()
            segment_lengths.reverse()
            points[0] = target if forwards else origin

            for o in range(len(points)):
                dir = normalize_list([points[o + 1][0] - points[o][0], points[o + 1][1] - points[o][1]])
                seg_dir = [dir[0] * segment_lengths[o], dir[1] * segment_lengths[o]]
                points[o + 1] = [points[o][0] + seg_dir[0], points[o][1] + seg_dir[1]]

            if not forwards and magnitude([points[-1][0] - target[0], points[-1][1] - target[1]]) <= .01:
                self.points = points
                return points

        return points

    def render(self, surf, circle_radius, line_width, colour=(255, 255, 255)):
        for i, point in enumerate(self.points):
            pygame.draw.circle(surf, colour, point, circle_radius)
            pygame.draw.line(surf, colour, point, self.points[i - 1] if i else point, line_width)

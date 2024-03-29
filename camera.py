
import os

import general_funcs as funcs
import pygame


def _bezier_curve_point(point_list, t, x_or_y):
    if len(point_list) == 1:
        return point_list[0][x_or_y]
    return round(_bezier_curve_point(point_list[:-1], t, x_or_y) * (1 - t) + _bezier_curve_point(point_list[1:], t, x_or_y) * t, 5)


def bezier_curve(def_points, speed=0.01):
    points = []
    for t in [_ * speed for _ in range(int((1 + speed * 2) // speed))]:
        points.append([_bezier_curve_point(def_points, t, 0), _bezier_curve_point(def_points, t, 1)])
    return points


class CameraCutscene:

    def __init__(self, path):
        self.path = path
        self.name = path.split(os.sep)[-1].split('.')[0]
        with open(self.path, 'r') as data:
            self.points = [float(num) for num in data.read().split(';')[0].split(',')]
            self.curve = bezier_curve(self.points, float(data.read().split(';')[-1]))


class Camera:

    def __init__(self, w, h, game, cutscene_path, bg_colour=(0, 0, 0)):
        self.display = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.screen = pygame.Surface((w, h))
        self.scroll = [0, 0]
        self.game = game
        self.bgc = bg_colour
        self.cutscene_path = cutscene_path
        self._locked = False
        self._to_blit = []
        self.cutscenes = {}
        self.zoom = 1.0
        self.current_points = None

        for file in os.listdir(self.cutscene_path):
            if file[0] != '.':
                cutscene = CameraCutscene(file)
                self.cutscenes[cutscene.name] = cutscene

    def update(self):
        if self.current_points is not None:
            try:
                self.scroll = next(self.current_points)
            except StopIteration:
                self.unlock()
                self.current_points = None
        self.display.fill(self.bgc)
        self.screen.fill(self.bgc)
        for surf_pos in self._to_blit:
            self.screen.blit(surf_pos[0], (surf_pos[1][0] + self.scroll[0], surf_pos[1][1] + self.scroll[1]))
        self._to_blit *= 0
        self.display.blit(pygame.transform.scale(self.screen, (self.screen.get_width() * self.zoom, self.screen.get_height() * self.zoom)), (0, 0))
        pygame.display.flip()

    def play_cutscene(self, name):
        points = self.cutscenes[name].curve
        for i, point in enumerate(points):
            points[i] = [funcs.normalize(points[0][0], point[0]), funcs.normalize(points[0][1], point[1])]

        return_points = []
        last_point = self.scroll
        for point in points:
            last_point[0] += point[0]
            last_point[1] += point[1]
            return_points.append(last_point)

        self.current_points = iter(return_points)
        self.lock()
        return return_points

    def render(self, surf, pos):
        self._to_blit.append((surf, pos))

    def zoom(self, flt):
        if not self._locked:
            if not (flt < 0 and self.zoom <= .1):
                self.zoom += flt

    def move_by(self, pos):
        if not self._locked:
            self.scroll[0] += pos[0]
            self.scroll[1] += pos[1]

    def move_to(self, pos):
        if not self._locked:
            self.scroll = pos[:2]

    def center(self, pos):
        if not self._locked:
            self.scroll = [self.screen.get_width() // 2 - pos[0], self.screen.get_height() // 2 - pos[1]]

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

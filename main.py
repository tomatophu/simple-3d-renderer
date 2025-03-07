import sys
import math
import time
from typing import Self

import pygame as pg

from classes import Camera
from classes import Map


WHITE = pg.Color('white')
BLACK = pg.Color('black')


MAP = Map(
    (-0.5, -0.5, 1),
    (0.5, -0.5, 1),
    (-0.5, -0.5, 2),
    (0.5, -0.5, 2),
    (-0.5, 0.5, 1),
    (0.5, 0.5, 1),
    (-0.5, 0.5, 2),
    (0.5, 0.5, 2),

    (1.5, 0, 1.5),
    (2.5, 0, 1.5),
    (2, 0, 2),
    (2, 0, 1),
    (2, -0.5, 1.5),
    (2, 0.5, 1.5),

    (-2.5, -0.5, 1),
    (-1.5, -0.5, 1),
    (-2.5, -0.5, 2),
    (-1.5, -0.5, 2),
    (-2, 0.5, 1.5),

    connections=[
        (0, 2),
        (1, 3),
        (2, 3),
        (0, 1),
        (4, 6),
        (5, 7),
        (6, 7),
        (4, 5),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),

        (8, 9),
        (10, 11),
        (12, 13),

        (14, 18),
        (15, 18),
        (16, 18),
        (17, 18),
        (14, 16),
        (15, 17),
        (14, 15),
        (17, 16),
    ]
)


class Game(object):
    def __init__(self: Self, point_map: Map):
        pg.init()
        self._screen_size = (1280, 720)

        self._running = 0
        self._game_speed = 60
        self._screen = pg.display.set_mode(self._screen_size,
                                           flags=pg.RESIZABLE | pg.SCALED,
                                           vsync=1)
        pg.display.set_caption('3D Renderer')
        self._font_size = int(self._screen_size[1] / 36)
        self._font = pg.font.SysFont('helvetica', self._font_size)
        self._clock = pg.time.Clock()

        self._map = point_map
        self._camera = Camera(point_map)

    def run(self: Self):
        self._running = 1
        start_time = time.time() 
        while self._running:
            
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = delta_time * self._game_speed

            keys = pg.key.get_pressed()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                    if keys[pg.K_LMETA] or keys[pg.K_RMETA]:
                        self._camera.pos = [0, 0, 0]
                    self._camera.dir = [0, 0, 0]

            mvt = (keys[pg.K_w] - keys[pg.K_s],
                   keys[pg.K_SPACE] - keys[pg.K_LSHIFT],
                   keys[pg.K_a] - keys[pg.K_d],
                   keys[pg.K_LEFT] - keys[pg.K_RIGHT],
                   keys[pg.K_UP] - keys[pg.K_DOWN],
                   keys[pg.K_RETURN] - keys[pg.K_QUOTE])

            self._camera.y += mvt[1] * 0.025 * rel_game_speed
            
            trig = (math.cos(self._camera.dir[0] - math.pi / 2), 
                    math.sin(self._camera.dir[0] - math.pi / 2))
            self._camera.x -= mvt[0] * trig[0] * 0.025 * rel_game_speed
            self._camera.z -= mvt[0] * trig[1] * 0.025 * rel_game_speed
            self._camera.x -= mvt[2] * -trig[1] * 0.025 * rel_game_speed
            self._camera.z -= mvt[2] * trig[0] * 0.025 * rel_game_speed
            # remember: cosine is an odd function, sine is an even function

            self._camera.yaw += math.radians(mvt[3]) * rel_game_speed
            self._camera.pitch += math.radians(mvt[4]) * rel_game_speed
            self._camera.roll += math.radians(mvt[5]) * rel_game_speed
 
            self._screen.fill(BLACK)
            self._camera.render(self._screen, 2)
            
            text = [
                f'x: {self._camera.x}',
                f'y: {self._camera.y}',
                f'z: {self._camera.z}',
                f'Yaw: {self._camera.yaw} rad',
                f'Pitch: {self._camera.pitch} rad',
                f'Roll: {self._camera.roll} rad',
            ]

            for dex, line in enumerate(text):
                pos = (self._font_size / 2, self._font_size / 2)
                pos[1] += dex * self._font_size * 1.25
                self._screen.blit(self._font.render(line, 1, WHITE), pos)

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game(MAP).run()

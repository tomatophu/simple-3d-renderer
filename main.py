import sys
import math
import time
from typing import Self

import pygame as pg

from classes import Camera
from classes import Map


WHITE = pg.Color('white')
BLACK = pg.Color('black')


# get map
from maps.teapot import MAP


class Game(object):
    def __init__(self: Self, point_map: Map):
        pg.init()
        # KEYDOWN events are not used for movement, so this is fine
        pg.key.set_repeat(400, 60)

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

        antialiasing = 0
        point_radius = 1
        line_thickness = 2

        while self._running:
            
            delta_time = time.time() - start_time
            start_time = time.time()

            fps = 1 / delta_time if delta_time else 'infinity'

            rel_game_speed = delta_time * self._game_speed

            keys = pg.key.get_pressed()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        if keys[pg.K_LMETA] or keys[pg.K_RMETA]:
                            self._camera.x = 0
                            self._camera.y = 0
                            self._camera.z = 0
                        self._camera.yaw = 0
                        self._camera.pitch = 0
                        self._camera.roll = 0
                    elif event.key == pg.K_RSHIFT:
                        antialiasing = not antialiasing
                    elif event.key == pg.K_COMMA:
                        if keys[pg.K_LMETA] or keys[pg.K_RMETA]:
                            line_thickness = max(line_thickness - 1, 1)
                        else:
                            point_radius = max(point_radius - 1, 1)
                    elif event.key == pg.K_PERIOD:
                        if keys[pg.K_LMETA] or keys[pg.K_RMETA]:
                            line_thickness += 1
                        else:
                            point_radius += 1

            mvt = (keys[pg.K_w] - keys[pg.K_s], # forward and backward
                   keys[pg.K_SPACE] - keys[pg.K_LSHIFT], # up and down
                   keys[pg.K_a] - keys[pg.K_d], # left and right
                   keys[pg.K_LEFT] - keys[pg.K_RIGHT], # changing yaw
                   keys[pg.K_UP] - keys[pg.K_DOWN], # changing pitch
                   keys[pg.K_RETURN] - keys[pg.K_QUOTE]) # changing roll

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
            self._camera.render(
                self._screen,
                point_radius,
                line_thickness,
                antialiasing=antialiasing
            )
            
            text = [
                f'x: {self._camera.x}',
                f'y: {self._camera.y}',
                f'z: {self._camera.z}',
                f'Yaw: {self._camera.yaw} rad',
                f'Pitch: {self._camera.pitch} rad',
                f'Roll: {self._camera.roll} rad',
                f'Antialiasing: {'On' if antialiasing else 'Off'}',
                f'Point Radius: {point_radius}',
                f'Line Thickness: {line_thickness}',
                f'FPS: {round(fps, 2) if delta_time else fps}',
            ]

            for dex, line in enumerate(text):
                pos = [self._font_size / 2, self._font_size / 2]
                pos[1] += dex * self._font_size * 1.25
                self._screen.blit(self._font.render(line, 1, WHITE), pos)

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    try:
        MAP
    except NameError:
        raise ValueError('Set a value to the MAP global variable.')

    Game(MAP).run()

import math
from typing import Self
from numbers import Real
from collections.abc import Sequence

import pygame as pg


class Map(object):
    def __init__(self: Self,
                 *points: Sequence[Sequence[Real]],
                 connections: Sequence[Sequence[int]]=[]):

        self._points = points
        self._connections = connections

    @property
    def connections(self: Self):
        return self._connections

    @connections.setter
    def connections(self: Self, value: Sequence[Sequence[int]]):
        self._connections = value
    
    @property
    def points(self: Self):
        return self._points

    @points.setter
    def points(self: Self, value: Sequence[Sequence[Real]]):
        self._points = value


class Camera(object):
    def __init__(self: Self):
        # x, y, z
        self._pos = [0, 0, 0]
        # yaw, pitch, roll (radians)
        self._dir = [0, 0, 0]
    
    @property
    def pos(self: Self):
        return self._pos

    @pos.setter
    def pos(self: Self, value: list[Real]):
        self._pos = value

    @property
    def dir(self: Self):
        return self._dir

    @dir.setter
    def dir(self: Self, value: list[Real]):
        self._dir = value
    
    def render(self: Self,
               surf: pg.Surface,
               points: Map,
               radius: Real=4,
               color: pg.Color=pg.Color('white'),
               fov: Real=90):
        surf_size = surf.get_size()
        surf_rect = surf.get_rect()
        semisize = (surf_size[0] / 2, surf_size[1] / 2)
        rot_points = []
        proj_points = []
        
        # fov is up and down (you can see more side-to-side)
        fov_mult = 1 / math.sin(math.radians(fov / 2))

        for point in points.points:
            rel_vector = pg.math.Vector3(point[0] - self._pos[0],
                                         point[1] - self._pos[1],
                                         point[2] - self._pos[2])
            
            # rotation
            rel_vector.rotate_y_rad_ip(self._dir[0])
            rel_vector.rotate_x_rad_ip(self._dir[1])
            rel_vector.rotate_z_rad_ip(self._dir[2])

            # Rotataion by Matrix Multiplication (manual) (yaw & pitch only)
            """
            # Around y-axis
            trig = (math.cos(self._dir[0]), math.sin(self._dir[0]))
            vector_old = rel_vector.copy()
            rel_vector[0] = trig[0] * vector_old[0] + trig[1] * vector_old[2]
            rel_vector[2] = -trig[1] * vector_old[0] + trig[0] * vector_old[2]
            
            # Around x-axis
            trig = (math.cos(self._dir[1]), math.sin(self._dir[1]))
            vector_old = rel_vector.copy()
            rel_vector[1] = trig[0] * vector_old[1] - trig[1] * vector_old[2]
            rel_vector[2] = trig[1] * vector_old[1] + trig[0] * vector_old[2]
            """
            
            # rot_points is used when calculating wheter to draw lines
            rot_points.append(list(rel_vector))
            
            # ratio of x:z / y:z used for projection
            ratios = [100, 100]
            if rel_vector[2]: # avoid zero-division
                ratios = (rel_vector[0] / rel_vector[2],
                          rel_vector[1] / rel_vector[2])
            
            # final projection
            proj_point = (ratios[0] * fov_mult * semisize[1] + semisize[0],
                          -ratios[1] * fov_mult * semisize[1] + semisize[1])
            proj_points.append(proj_point)

            # draw points
            if rel_vector[2] > 0:
                pg.draw.aacircle(surf, color, proj_points[-1], radius)
        
        # draw lines
        for connection in points.connections:
            if (rot_points[connection[0]][2] > 0
                and rot_points[connection[1]][2] > 0):
                pg.draw.aaline(surf, color,
                               proj_points[connection[0]],
                               proj_points[connection[1]])


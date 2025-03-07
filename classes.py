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
        return tuple(self._connections)

    @connections.setter
    def connections(self: Self, value: Sequence[Sequence[int]]):
        self._connections = list(value)

    def add_connection(self: Self, connection: Sequence[int]):
        if connection in self._connection:
            raise ValueError('connection already in map')
        self._connections.append(connection)

    def remove_connection(self: Self, connection: Sequence[int]):
        self._connection.remove(point)

    @property
    def points(self: Self):
        return tuple(self._points)

    @points.setter
    def points(self: Self, value: Sequence[Sequence[Real]]):
        self._points = list(value)

    def add_point(self: Self, point: Sequence[Real]):
        if point in self._points:
            raise ValueError('point already in map')
        self._points.append(point)

    def remove_point(self: Self, point: Sequence[Real]):
        self._points.remove(point)


class Camera(object):
    def __init__(self: Self, point_map: Map, fov: Real=90):
        # x, y, z
        self._pos = [0, 0, 0]
        # yaw, pitch, roll (radians)
        self._dir = [0, 0, 0]

        self._map = point_map
        self._fov = fov
        # fov is up and down (you can see more side-to-side)
        self._fov_mult = 1 / math.sin(math.radians(fov / 2))

    @property
    def pos(self: Self):
        return tuple(self._pos)

    @property
    def x(self: Self):
        return self._pos[0]

    @x.setter
    def x(self: Self, value: Real):
        self._pos[0] = value

    @property
    def y(self: Self):
        return self._pos[1]

    @y.setter
    def y(self: Self, value: Real):
        self._pos[1] = value

    @property
    def z(self: Self):
        return self._pos[2]

    @z.setter
    def z(self: Self, value: Real):
        self._pos[2] = value
    
    @property
    def dir(self: Self):
        return tuple(self._dir)

    @property
    def yaw(self: Self):
        return self._dir[0]

    @yaw.setter
    def yaw(self: Self, value: Real):
        self._dir[0] = value
    
    @property
    def pitch(self: Self):
        return self._dir[1]

    @pitch.setter
    def pitch(self: Self, value: Real):
        self._dir[1] = value

    @property
    def roll(self: Self):
        return self._dir[2]

    @roll.setter
    def roll(self: Self, value: Real):
        self._dir[2] = value
    
    @property
    def map(self: Self):
        return self._map

    @map.setter
    def map(self: Self, value: Map):
        self._map = value

    @property
    def fov(self: Self):
        return self._fov

    @fov.setter
    def fov(self: Self, value: Real):
        self._fov = value
    
    def render(self: Self,
               surf: pg.Surface, 
               radius: Real=4,
               color: pg.Color=pg.Color('white')):
        surf_size = surf.get_size()
        surf_rect = surf.get_rect()
        semisize = (surf_size[0] / 2, surf_size[1] / 2)
        rot_points = []
        proj_points = []
        
        for point in self._map.points:
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
            proj_points.append((ratios[0] * self._fov_mult
                                * semisize[1] + semisize[0],
                                -ratios[1] * self._fov_mult
                                * semisize[1] + semisize[1]))

            # draw points
            if rel_vector[2] > 0:
                pg.draw.aacircle(surf, color, proj_points[-1], radius)
        
        # draw lines
        for connection in self._map.connections:
            if (rot_points[connection[0]][2] > 0
                and rot_points[connection[1]][2] > 0):
                pg.draw.aaline(surf, color,
                               proj_points[connection[0]],
                               proj_points[connection[1]])


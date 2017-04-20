# -*- coding: utf-8 -*-

import pygame


class NPC:
    """ Base class for NPC """

    def __init__(self, pos_x, pos_y, size, radius, screen_width, screen_height,
                 speed=None, bullets=None, num=None):
        self.rect = pygame.Rect(pos_x, pos_y, size, size)
        self.size = size
        self.radius = radius
        self.screen_width = screen_width
        self.screen_height = screen_height

        if speed is not None:
            self.speed = speed
        if bullets is not None:
            self.bullets = []
        if num is not None:
            self.num = num

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def move(self, x_step=0, y_step=0):

        if self.x < 0 or self.x >= self.screen_width - self.size - self.speed:
            x_step = 0
        if self.y < 0 or self.y >= self.screen_height - self.size - self.speed:
            y_step = 0

        self.rect = self.rect.move(x_step, y_step)


class Hero(NPC):
    """ NPC teached by user """

    def process(self, doc):

        for item in doc['cmd_lst']:
            if item['cmd'] == 'move':
                x_step = y_step = 0

                if item['xd'] == 1:
                    x_step = self.speed
                elif item['xd'] == -1:
                    x_step = -self.speed
                else:
                    x_step = 0

                if item['yd'] == 1:
                    y_step = self.speed
                elif item['yd'] == -1:
                    y_step = -self.speed
                else:
                    y_step = 0

                self.move(x_step, y_step)

    def shoot(self, x, y):
        pass


class Enemy(NPC):
    """ Base class for npc enemy """

    def process(self, hero_x, hero_y):
        x, y = self.rect.center
        x_step = y_step = 0

        if hero_x > x:
            x_step = self.speed
        elif hero_x < x:
            x_step = -self.speed
        else:
            x_step = 0

        if hero_y > y:
            y_step = self.speed
        elif hero_y < y:
            y_step = -self.speed
        else:
            y_step = 0

        self.move(x_step, y_step)


class EnemyGreen(Enemy):
    """ Easy enemy """

    enemy_class = 'green'
    color = (51, 222, 32)
    power = 5
    speed = 1

# -*- coding: utf-8 -*-

import pygame


class NPC:
    """ Base class for NPC """

    def __init__(self, pos_x, pos_y, size, screen_width, screen_height,
                 speed=None, bullets=None, num=None):
        self.rect = pygame.Rect(pos_x, pos_y, size, size)
        self.size = size
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

    def move(self, x=0, y=0):

        if self.x < 0 or self.x >= self.screen_width - self.size - self.speed:
            x = 0
        if self.y < 0 or self.y >= self.screen_height - self.size - self.speed:
            y = 0

        self.rect = self.rect.move(x, y)


class Hero(NPC):
    """ NPC teached by user """

    def process(self, doc):

        for item in doc['cmd_lst']:
            if item['cmd'] == 'move':
                x = y = 0

                if item['x'] == 1:
                    x = self.speed
                elif item['x'] == -1:
                    x = -self.speed

                if item['y'] == 1:
                    y = self.speed
                elif item['y'] == -1:
                    y = -self.speed

                self.move(x, y)


class Enemy(NPC):
    """ Base class for npc enemy """

    pass


class EnemyGreen(Enemy):
    """ Easy enemy """

    enemy_class = 'green'
    color = (51, 222, 32)
    power = 5
    speed = 1

    def process(self, hero_x, hero_y):
        x = y = 0

        if hero_x > self.x:
            x = self.speed
        elif hero_x < self.x:
            x = -self.speed

        if hero_y > self.y:
            y = self.speed
        elif hero_y < self.y:
            y = -self.speed

        self.move(x, y)

# -*- coding: utf-8 -*-

import pygame
import numpy as np


class NPC:
    """ Base class for NPC """

    def __init__(self, pos_x, pos_y, size, radius, screen_width, screen_height,
                 speed=None, bullets=None, num=None, bullet_size=None,
                 bullet_radius=None, bullet_speed=None,
                 x_step=None, y_step=None):
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
        if bullet_size is not None:
            self.bullet_size = bullet_size
        if bullet_radius is not None:
            self.bullet_radius = bullet_radius
        if bullet_speed is not None:
            self.bullet_speed = bullet_speed
        if x_step is not None:
            self.x_step = x_step
        if y_step is not None:
            self.y_step = y_step

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def move(self, x_step=0, y_step=0, borders=True):

        if borders:
            if self.x < 0 or self.x >= self.screen_width-self.size-self.speed:
                x_step = 0
            if self.y < 0 or self.y >= self.screen_height-self.size-self.speed:
                y_step = 0

        self.rect = self.rect.move(x_step, y_step)


class Hero(NPC):
    """ NPC teached by user """

    bullets_created = 0
    bullets = []

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

            elif item['cmd'] == 'shoot':
                self.shoot(item['x'], item['y'])

    def shoot(self, x_target, y_target):

        x, y = self.rect.center

        dt = np.sqrt((x_target - x)**2 + (y_target - y)**2)
        steps = dt / self.bullet_speed
        x_step = (x_target - x) / steps
        y_step = (y_target - y) / steps

        bullet = HeroBullet(x, y, self.bullet_size, self.bullet_radius,
                            self.screen_width, self.screen_height,
                            self.bullet_speed, num=self.bullets_created,
                            x_step=x_step, y_step=y_step)
        self.bullets_created += 1
        self.bullets.append(bullet)


class HeroBullet(NPC):
    """ Bullet created by Hero """

    def process(self):
        self.move(self.x_step, self.y_step, borders=False)


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

# -*- coding: utf-8 -*-

import json
from random import randint
from concurrent.futures import ThreadPoolExecutor

import pygame
import numpy as np

import tornado.web
import tornado.gen
import tornado.websocket
from tornado.queues import Queue
from tornado.concurrent import run_on_executor

from .npc import Hero, EnemyGreen


class BotServerApp(tornado.web.Application):

    fps = 30
    screen_width = 1024
    screen_height = 768

    hero_radius = 15
    hero_size = hero_radius * 2
    hero_color = (255, 255, 255)
    hero_speed = 3.5
    hero_hp_full = 100

    hero_bullet_radius = 3
    hero_bullet_size = hero_bullet_radius * 2
    hero_bullet_color = (239, 0, 255)
    hero_bullet_speed = 6

    enemy_radius = 10
    enemy_size = enemy_radius * 2

    def __init__(self):
        handlers = [
            (r'/', GameHandler)
        ]

        settings = {'debug': True}

        self.executor = ThreadPoolExecutor(4)
        self.client = None

        self.queue = Queue()

        print('bot app __init__')
        super(BotServerApp, self).__init__(handlers, **settings)

    @tornado.gen.coroutine
    def start_game(self):
        self.gameover = False
        self.init_world()
        yield self.run_pygame_loop()

    @run_on_executor
    @tornado.gen.coroutine
    def run_pygame_loop(self):
        """ pygame event loop, game runs while self.gameover == False """

        self.hero = Hero(
            int(self.screen_width / 2) - int(self.hero_size / 2),
            int(self.screen_height / 2) - int(self.hero_size / 2),
            self.hero_size,
            self.hero_radius,
            self.screen_width,
            self.screen_height,
            self.hero_speed,
            bullets=True,
            bullet_size=self.hero_bullet_size,
            bullet_radius=self.hero_bullet_radius,
            bullet_speed=self.hero_bullet_speed
        )

        self.hero_hp = self.hero_hp_full
        hero_x, hero_y = self.hero.rect.center
        hero_died = False

        # TODO: enemy spawn at iterator steps
        enemies = []
        for i in range(3):

            x = randint(0, self.screen_width-10)
            y = randint(0, self.screen_height-10)
            dt = np.sqrt((x - hero_x)**2 + (y - hero_y)**2)

            # Don't spawn enemies near to hero
            while dt <= self.hero_radius*5:
                x = randint(0, self.screen_width-10)
                y = randint(0, self.screen_height-10)
                dt = np.sqrt((x - hero_x)**2 + (y - hero_y)**2)

            enemies.append(
                EnemyGreen(
                    randint(0, self.screen_width-10),  # x
                    randint(0, self.screen_height-10),  # y
                    self.enemy_size,
                    self.enemy_radius,
                    self.screen_width,
                    self.screen_height,
                    num=i  # enemy num (like id)
                )
            )

        self.client.write_message(json.dumps({'status': 1}))

        while not self.gameover:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

            self.screen.fill((0, 0, 0))

            # Get instructions from queue and move hero
            if not self.queue.empty():
                doc = yield self.queue.get()
                self.hero.process(doc)

            # Draw hero
            pygame.draw.circle(self.screen, self.hero_color,
                               self.hero.rect.center, self.hero.radius)
            hero_x, hero_y = self.hero.rect.center

            # Bullets fly and collision
            bullet_rm_set = set()
            enemies_rm_set = set()
            for bullet in self.hero.bullets:
                bullet.process()
                pygame.draw.circle(self.screen, self.hero_bullet_color,
                                   bullet.rect.center, bullet.radius)

                bullet_x, bullet_y = bullet.rect.center
                enemy_killed = False
                for enemy in enemies:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy_x, enemy_y = enemy.rect.center
                        need_dt = self.hero_bullet_radius + self.enemy_radius
                        dt = np.sqrt(
                            (enemy_x - bullet_x)**2 + (enemy_y - bullet_y)**2
                        )

                        if dt <= need_dt:
                            enemies_rm_set.add(enemy)
                            bullet_rm_set.add(bullet)
                            enemy_killed = True
                            break

                if enemy_killed:
                    continue

                # Delete bullets if they escape screen
                bx, by = bullet.rect.x, bullet.rect.y
                if bx < -bullet.size or bx >= self.screen_width+bullet.size:
                    bullet_rm_set.add(bullet)
                elif by < -bullet.size or by >= self.screen_height+bullet.size:
                    bullet_rm_set.add(bullet)

            for bullet in bullet_rm_set:
                self.hero.bullets.remove(bullet)
            for enemy in enemies_rm_set:
                enemies.remove(enemy)

            del bullet_rm_set
            del enemies_rm_set

            objects_list = []
            for enemy in enemies:
                # Move and draw enemy
                enemy.process(hero_x, hero_y)
                pygame.draw.circle(self.screen, enemy.color, enemy.rect.center,
                                   enemy.radius)
                enemy_x, enemy_y = enemy.rect.center

                # Check for collision
                if self.hero.rect.colliderect(enemy.rect):
                    # Colliderect check squares collision but for
                    # real circles collision distantion between centers
                    # of circles must be <= radiuses sum
                    need_dt = self.hero_radius + self.enemy_radius
                    dt = np.sqrt((enemy_x - hero_x)**2 + (enemy_y - hero_y)**2)

                    if dt <= need_dt:
                        self.hero_hp -= enemy.power

                # Does enemy kills hero
                if self.hero_hp <= 0:
                    hero_died = True
                    break

                # Enemy description
                enemy_info = {
                    # cords for !center! of enemy circle
                    'x': enemy_x,
                    'y': enemy_y,
                    'enemy_class': enemy.enemy_class,
                    'num': enemy.num
                    # TODO: enemy bullets
                }
                objects_list.append(enemy_info)

            # If hero is dead - gameover >_<
            if hero_died:
                self.client.write_message(json.dumps({'status': 0}))
                self.gameover = True
                continue

            # Send info about objects on screen to client
            self.client.write_message(
                json.dumps(
                    # cords for !center! of hero circle
                    {'objects': objects_list, 'hp': self.hero_hp, 'status': 1,
                     'x': hero_x, 'y': hero_y}
                )
            )

            pygame.display.flip()
            self.clock.tick(self.fps)

    def init_world(self):
        """ Create new game world """

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        self.clock = pygame.time.Clock()
        pygame.init()
        pygame.display.init()
        self.game_matrix = np.zeros((self.screen_width, self.screen_height))

    def destroy_world(self):
        self.screen.fill((0, 0, 0))
        self.screen = None
        self.game_matrix = None
        pygame.display.quit()
        pygame.quit()


class GameHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print('ws client connected', self.application.client)
        if self.application.client is None:
            self.application.client = self
        else:
            self.write_message('server already used')
            self.close()
            return

        self.application.start_game()

    def on_message(self, msg):
        self.application.queue.put(json.loads(msg))

    def on_close(self):
        self.application.gameover = True
        self.application.client = None
        self.application.destroy_world()

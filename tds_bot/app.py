# -*- coding: utf-8 -*-

import json
from random import randint
from concurrent.futures import ThreadPoolExecutor

import pygame

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

    hero_size = 30
    hero_color = (255, 255, 255)
    hero_speed = 3
    hero_hp_full = 100

    enemy_size = 20

    def __init__(self):
        handlers = [
            (r'/', GameHandler)
        ]

        settings = dict(
            debug=True,
        )

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

        self.hero_hp = self.hero_hp_full
        # TODO: enemy spawn at iterator steps
        enemies = [
            EnemyGreen(
                randint(0, self.screen_width-10),  # x
                randint(0, self.screen_height-10),  # y
                20,  # size
                self.screen_width,
                self.screen_height,
                num=0  # enemy num (like id)
            )
        ]

        hero_died = False
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
            pygame.draw.rect(self.screen, self.hero_color, self.hero.rect)

            objects_list = []
            for enemy in enemies:
                # Move and draw enemy
                enemy.process(self.hero.x, self.hero.y)
                pygame.draw.rect(self.screen, enemy.color, enemy.rect)

                # Check for collision
                if self.hero.rect.colliderect(enemy.rect):
                    self.hero_hp -= enemy.power

                # Does enemy kills hero
                if self.hero_hp <= 0:
                    hero_died = True
                    break

                # Enemy description
                enemy_info = {
                    'x': enemy.x,
                    'y': enemy.y,
                    'enemy_class': enemy.enemy_class,
                    'num': enemy.num,
                    # TODO: enemy bullets
                }
                objects_list.append(enemy_info)

            # If hero is dead - gameover =)
            if hero_died:
                self.client.write_message(json.dumps({'status': 0}))
                self.gameover = True
                continue

            # Send info about objects on screen to client
            self.client.write_message(
                json.dumps(
                    {'objects': objects_list, 'hp': self.hero_hp, 'status': 1,
                     'x': self.hero.x, 'y': self.hero.y}
                )
            )

#            pygame.draw.rect(self.screen, self.hero_color, self.hero.rect)

#            for enemy in enemies:
#                enemy.process()
#                pygame.draw.rect(self.screen, enemy.color, enemy.rect)

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

        self.hero = Hero(
            int(self.screen_width / 2),
            int(self.screen_height / 2),
            self.hero_size,
            self.screen_width,
            self.screen_height,
            self.hero_speed,
            True
        )

    def destroy_world(self):
        self.screen.fill((0, 0, 0))
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

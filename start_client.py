#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from tds_bot.client import WebsocketClient


class Client(WebsocketClient):

    def process(self, server_info):

        if 'objects' not in server_info:
            return

        print(server_info)

        # Hero cordinates
        x, y = server_info['x'], server_info['y']

        # Distances to enemies
        distances = []
        for e in server_info['objects']:
            t = (np.sqrt((e['x'] - x)**2 + (e['y'] - y)**2), e['num'])
            distances.append(t)

        nearest_enemy = sorted(distances)[0][1]

        for e in server_info['objects']:
            if e['num'] == nearest_enemy:
                enemy_x = e['x']
                enemy_y = e['y']

        # Move into reversed direction from nearest enemy
        # xd - x direction, yd - y direction
        if enemy_x > x:
            xd = -1
        elif enemy_x < x:
            xd = 1
        else:
            xd = 0

        if enemy_y > y:
            yd = -1
        elif enemy_y < y:
            yd = 1
        else:
            yd = 0

        hero_cmds = {
            'cmd_lst': [{'cmd': 'move', 'xd': xd, 'yd': yd}]
        }
        self.write(hero_cmds)


if __name__ == '__main__':
    c = Client('ws://127.0.0.1:13228')
    c.run()

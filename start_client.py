#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

import numpy as np

from tds_bot.client import WebsocketClient


class Client(WebsocketClient):

    def process(self, server_info):

        if 'objects' not in server_info or not server_info['objects']:
            return

        # Here will be saved instructions
        hero_cmds = {
            'cmd_lst': []
        }

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

        # Shoot to nearest enemy
        # After one shot realoading will be continious on
        # next 5 iterations that mean on next 5 iterations shoot
        # cmd will be ignored
        hero_cmds['cmd_lst'].append(
                {'cmd': 'shoot', 'x': enemy_x, 'y': enemy_y}
        )

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

        hero_cmds['cmd_lst'].append({'cmd': 'move', 'xd': xd, 'yd': yd})
        self.write(hero_cmds)


def main():
    parser = argparse.ArgumentParser(prog='pygame tornado bot client')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=7691)
    args = parser.parse_args()

    url = 'ws://%s:%d' % (args.host, args.port)
    c = Client(url)
    c.run()


if __name__ == '__main__':
    main()

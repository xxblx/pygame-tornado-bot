#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

import tornado.ioloop
import tornado.httpserver

from tds_bot.app import BotServerApp


def main():
    parser = argparse.ArgumentParser(prog='pygame tornado bot server')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=7691)
    args = parser.parse_args()

    app = BotServerApp()
    http_server = tornado.httpserver.HTTPServer(app)

    try:
        http_server.listen(args.port, args.host)
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.start()
    except KeyboardInterrupt:
        app.gameover = True
    finally:
        ioloop.stop()


if __name__ == '__main__':
    main()

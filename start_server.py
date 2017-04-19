#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.httpserver

from tds_bot.app import BotServerApp


def main():
    app = BotServerApp()
    http_server = tornado.httpserver.HTTPServer(app)

    try:
        http_server.listen(13228, '127.0.0.1')
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.start()
    except KeyboardInterrupt:
        app.gameover = True
    finally:
        ioloop.stop()


if __name__ == '__main__':
    main()

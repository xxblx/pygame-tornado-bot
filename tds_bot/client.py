# -*- coding: utf-8 -*-

import json

import tornado.gen
import tornado.ioloop
from tornado.websocket import websocket_connect


class WebsocketClient:

    def __init__(self, url):
        self.url = url
        self.ioloop = tornado.ioloop.IOLoop.current()

    def process(self, doc):
        raise NotImplementedError

    def write(self, doc):
        self.connect.write_message(json.dumps(doc))

    @tornado.gen.coroutine
    def start_chat(self):
        self.connect = yield websocket_connect(self.url)

        while True:
            msg = yield self.connect.read_message()
            if msg is None:
                self.connect.close()
                break

            doc = json.loads(msg)
            if doc['status'] != 0:
                self.process(doc)
            else:
                print('You dided')
                self.connect.close()
                break

    def run(self):
        self.ioloop.run_sync(lambda: self.start_chat())

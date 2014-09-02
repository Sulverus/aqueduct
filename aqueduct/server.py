#encoding: utf8
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import json
from tornado.options import define, options
from aqueduct.listener import Listener
from aqueduct.storages.basic import MemoryStorage
from tornado import httpclient
from aqueduct.log import logger
from tornado.httpclient import HTTPError as HTTPClientError
from socket import error as socket_error
from tornado import gen

SECOND = 1000
MINUTE = SECOND * 60

define("port", default=8888, help="Run service on this port", type=int)
define("interval", default=5 * MINUTE, help="Queue check interval", type=int)
define("config", default='../conf/config.json', help="Configuration file", type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/pool", Listener),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        config_file = open(options.config, 'r')
        self.config = json.load(config_file)

        self.storage = self.get_storage()
        self.waiting_check = False

    def get_storage(self):
        """
        Function to configure the storage, currently used only MemoryStorage
        """
        storage_dict = {
            'memory': MemoryStorage
        }
        storage_type = self.config.get('storage', 'memory')
        obj = storage_dict[storage_type]

        logger.info('Storage initialization done. Using %s mode' % storage_type)
        return obj(self.config)

    @staticmethod
    @gen.coroutine
    def transport(client, key, data):
        """
        The general method of async data transfer over http protocol
        """
        http_client = httpclient.AsyncHTTPClient()
        try:
            response = yield http_client.fetch(
                '%s?api_key=%s' % (client, key),
                method='POST', body=json.dumps(data)
            )
            status_code = response.code
        except HTTPClientError, e:
            status_code = e.code
        except socket_error:
            status_code = -1
        http_client.close()
        raise gen.Return(status_code)

    @gen.coroutine
    def process_channel(self, client, channel, messages):
        """
        Send lost messages to the client in a given channel
        """
        api_key = self.storage.get_client_key(client, channel)
        for i, message in enumerate(messages):
            status_code = yield self.transport(client, api_key, message[0])
            if status_code != 200:
                break
            self.storage.drop_message(client, channel, i)

    def send_waiting(self):
        """
        Task to handle all unsent messages: at any time may be running only one task
        """
        if self.waiting_check:
            return
        self.waiting_check = True
        for client in self.storage.waiting_clients():
            service_channels = self.storage.waiting_messages(client)
            for channel, messages in service_channels.iteritems():
                self.process_channel(client, channel, messages)
        self.waiting_check = False


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Aqueduct 0.1.5")


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    logger.info('Starting Aqueduct on %d port' % options.port)
    tornado.ioloop.PeriodicCallback(app.send_waiting, options.interval).start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

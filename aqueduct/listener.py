#encoding: utf8
from tornado.web import HTTPError, RequestHandler
from tornado import gen
from aqueduct.log import logger
import json


class Listener(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self.set_header('Content-Type', 'application/json; charset="utf-8"')

    def broadcast(self, channel, data):
        """
        Function to send data to the services:
        send out a message to all who subscribed to the channel. If the service
        is not able to receive messages save it to deliver later
        """
        for client, key in self.application.storage.get_clients(channel):
            # if service has undelivered messages
            # put them in a queue - message will be sent in the order first in first out
            if self.application.storage.messages_in_channel(client, channel):
                self.application.storage.push(client, channel, data, None)
                continue
            # Else send a message
            status_code = self.application.transport(client, key, data)
            if status_code == 200:
                continue

            # If an error occurs writing to the queue
            logger.error('[%s] Transport failed for service %s' % (channel, client))
            self.application.storage.push(client, channel, data, status_code)

    @gen.coroutine
    def post(self):
        """
        Get the data from the client and send it out. Give response about getting
        the data immediately, messages are sent asynchronously
        """
        # check api key
        api_key = self.get_argument('api_key', None)
        if api_key not in self.application.storage.api_keys:
            raise HTTPError(403, 'Access denied')

        # get the channel and message
        try:
            data = json.loads(self.request.body)
        except:
            raise HTTPError(400, 'Wrong json data')
        channel = data.get('channel', None)
        data = data.get('data', None)

        if channel is None:
            raise HTTPError(400, 'No channel specified')
        if data is None:
            raise HTTPError(400, 'No data specified')

        # send out data
        self.application.executor.submit(self.broadcast, channel, data)
        logger.info(
            '[%s] New message from %s' % (channel, self.request.remote_ip)
        )

        # return json response
        self.write('{"status": "accepted"}')
        self.finish()

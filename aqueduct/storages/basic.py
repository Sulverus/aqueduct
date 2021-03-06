#encoding: utf8
class MemoryStorage(object):
    """
    Simple(dummy) in-memory storage
    In production better to use some database. Written to describe the api and testing
    """
    def __init__(self, config):
        # configuration of channels and services provided by application
        self.config = config

        # Storage of undelivered messages
        self.storage = dict()

        # Dict with services and subscriptions
        self.clients = dict()
        self.load_clients()

        # The list of keys to interact with the application
        self.api_keys = list()
        self.load_api_keys()

    def load_clients(self):
        """
        Loading services and key data from config
        """
        channel_dict = self.config.get('channels', {})
        for channel in channel_dict:
            self.add_channel(channel)
            for user_data in channel_dict.get(channel, []):
                self.subscribe(user_data['url'], user_data['key'], channel)

    def load_api_keys(self):
        """
        Loading keys to store messages
        """
        self.api_keys = self.config.get('keys', [])

    def push(self, client, channel, data, status_code):
        """
        Adding the undeliverable message in the storage
        """
        if client not in self.storage:
            self.storage[client] = {}
        if channel not in self.storage[client]:
            self.storage[client][channel] = []
        self.storage[client][channel].append((data, status_code))

    def waiting_clients(self):
        """
        Returns the services that have undelivered messages
        """
        return self.storage.iterkeys()

    def waiting_messages(self, client):
        """
        Returns a dict with the channels in which there are unsent messages
        for a given service
        """
        return self.storage.get(client, None)

    def get_client_key(self, client, channel):
        """
        Returns the key to send the data to the client in a given channel
        """
        result = None
        if channel in self.clients:
            for service in self.clients[channel]:
                if service[0] != client:
                    continue
                result = service[1]
        return result

    def get_clients(self, channel):
        """
        Returns a list of services subscribed to the channel
        """
        if channel not in self.clients.keys():
            return []
        return self.clients[channel]

    def drop_message(self, client, channel, i):
        """
        Deletes the message from storage
        """
        del self.storage[client][channel][i]

    def messages_in_channel(self, client, channel):
        """
        Returns the number of unsent messages for service in a given channel
        """
        result = None
        if client not in self.storage:
            return result
        if channel not in self.storage[client]:
            return result
        result = len(self.storage[client][channel])
        return result

    def __repr__(self):
        """
        In print we trust
        """
        return repr(self.storage)

    def add_channel(self, channel):
        """
        Try to create a channel in the storage
        """
        if channel in self.clients:
            return False
        self.clients[channel] = []
        return True

    def subscribe(self, client, api_key, channel):
        """
        Subscribe client to the channel
        """
        if channel not in self.clients:
            return False
        pair = (client, api_key)
        if pair in self.clients[channel]:
            return False

        self.clients[channel].append(pair)
        return True

    def unsubscribe(self, client, channel):
        """
        Unsubscribe client from the channel
        N.B. we must drop all messages in queue for this client
        """
        clients = self.clients.get(channel)
        if clients is None:
            return False
        index = None
        for i, pair in enumerate(clients):
            if pair[0] != client:
                continue
            index = i
            break
        if index is not None:
            del self.clients[channel][index]
        return True

    def drop_channel(self, channel):
        """
        Drop channel with all messages and clients
        """
        return self.clients.pop(channel, None)

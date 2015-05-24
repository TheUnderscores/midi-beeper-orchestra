class Event:
    def __init__(self, delay, hz):
        self.delay = delay
        self.hz = hz

class Layer:
    def __init__(self):
        self.events = []

    def addEvent(self, e):
        self.events.append(e)

class Client:
    def __init__(self, connection):
        self.connection = connection

class Manager:
    def __init__(self, clients):
        self.layers = []
        # Connected clients
        self.clients = clients

    def updLyrDist(self):
        """
        Updates layer distribution.
        In other words, which client is playing which channel.
        """
        if len(self.clients) <= len(self.layers):
            for c_i, c in enumerate(self.clients):
                c.layer = c_i
        else:
            perLayer = int(len(self.clients) / len(self.layers))
            pos = 0
            for l_i in range(len(self.layers)):
                for c_i in range(pos, pos + perLayer):
                    self.clients[c_i].layer = l_i
                pos += perLayer
            if pos < len(self.clients):
                # Assign leftover clients to different layers, starting
                # with layer 0
                leftOver = len(self.clients) - pos
                for l_i in range(0, leftOver):
                    self.clients[pos+l_i].layer = l_i

    def addLayer(self):
        self.layers.append(Layer())
        self.updLyrDist()

    def rmvLayer(self, c_i):
        self.layers.pop(c_i)
        self.updLyrDist()

    def update(dt):
        """
        Updates the manage
        dt is delta-time in milliseconds
        """
        pass
        # TODO


# TEST
clients = []
for c_i in range(10):
    clients.append(Client('foo'))
man = Manager(clients)
for l_i in range(6):
    man.addLayer()
for c_i, c in enumerate(man.clients):
    print(c.layer)
# EOF TEST

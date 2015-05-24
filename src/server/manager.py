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
        self.curHz = 0

    def doEvent(self, event):
        """
        Tell client to beep based on event frequency.
        The client will ONLY recieve the frequency to beep at.
        """
        self.curHz = event.hz
        print("HZ:\t" + str(event.hz))
        # TODO: Send packet with event.hz as the frequency

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

    def update(self, dt):
        """
        Updates the manage
        dt is delta-time in milliseconds (integer, not float)
        """
        # Decrease delay on events
        for l_i, l in enumerate(self.layers):
            decr = dt
            events = self.layers[l_i].events
            # Decrease delays of as many events as delta-time encompasses
            while decr > 0:
                oldDelay = events[0].delay
                if decr <= oldDelay:
                    events[0].delay -= decr
                else:
                    events.pop(0)
                decr -= oldDelay

        # Send events to clients
        for c_i, c in enumerate(self.clients):
            event = self.layers[c.layer].events[0]
            # Only update the client's beeper frequency if it needs changing
            if c.curHz != self.layers[c.layer].events[0].hz:
                c.doEvent(event)


# TEST
# EOF TEST

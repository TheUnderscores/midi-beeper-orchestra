# TODO: Account for empty layer
# TODO: Add copyright header

class Event:
    def __init__(self, delay, hz):
        self.delay = delay
        self.hz = hz

class Layer:
    def __init__(self):
        self.events = []
        self.curEvent = Event(0, 0)

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
        print("HZ: \t{}\tLAYER: \t{}".format(event.hz, self.layer))
        # TODO: Send packet with self.curHz as the frequency

class Manager:
    def __init__(self, clients):
        self.layers = []
        self.layers_active = []
        self.numActiveLayers = 0
        # Connected clients
        self.clients = clients

    def _updLyrDist(self):
        """
        Updates layer distribution.
        In other words, which client is playing which channel.
        Return True if there are active layers
        Return False if there are no active layers
        """
        self._updActLyrNum()

        if self.numActiveLayers == 0:
            # No layers are active
            # No use assigning layers
            # Set all client frequencies to 0
            for c in self.clients:
                c.curHz = 0
            return False

        if len(self.clients) <= self.numActiveLayers: # FIX THIS
            # Lack of client. More layers than clients.
            c_i = 0
            for l_i in range(len(self.layers)):
                if self.layers_active[l_i]:
                    self.clients[c_i].layer = l_i
                    c_i += 1
                    if c_i >= len(self.clients):
                        break
        else:
            # Excess of clients. More clients than layers.
            perLayer = int(len(self.clients) / self.numActiveLayers)
            pos = 0
            for l_i in range(len(self.layers)):
                # Do not assign an inactive layer to a client
                if not self.layers_active[l_i]:
                    continue

                for c_i in range(pos, pos + perLayer):
                    self.clients[c_i].layer = l_i
                pos += perLayer
            if pos < len(self.clients):
                # Assign leftover clients to different layers, starting
                # with layers at beginning of stack.
                #leftOver = len(self.clients) - pos
                for l_i in range(len(self.layers)):
                    if not self.layers_active[l_i]:
                        continue
                    self.clients[pos].layer = l_i
                    pos += 1
                    if pos >= len(self.clients):
                        # All leftover clients given a layer
                        break

        # There are active layers
        return True

    def addLayer(self, layer=None):
        """Adds a layer to manager's layer stack"""
        if layer == None:
            layer = Layer()
        self.layers.append(layer)
        self.layers_active.append(None)
        active = self._checkLayerActive(len(self.layers)-1)

    def rmvLayer(self, l_i):
        """Removes layer l_i from manager's layer stack"""
        self.layers.pop(l_i)
        self.layers_active.pop(l_i)

    def _checkLayerActive(self, l_i):
        """
        Check if layer l_i is frequency is 0 or not.
        If its frequency is 0, the layer is not active.
        Returns True if the layer is active.
        Returns False if the layer is inactive.
        """
        if self.layers[l_i].curEvent.hz == 0:
            active = False
        else:
            active = True
        self.layers_active[l_i] = active

        return active

    def _updActLyrNum(self):
        """Update number of active layers"""
        self.numActiveLayers = 0
        for l_i, active in enumerate(self.layers_active):
            if active:
                self.numActiveLayers += 1 # YOU WHERE HERE

    def addToLayer(self, l_i, event):
        """Adds given event to layer of specified index l_i"""
        self.layers[l_i].events.append(event)

    def update(self, dt):
        """
        Updates the manage
        dt is delta-time in milliseconds (integer, not float)
        """
        if dt == 0:
            for l_i, l in enumerate(self.layers):
                events = self.layers[l_i].events
                if events[0].delay <= 0:
                    self.layers[l_i].curEvent = events[0]
                    events.pop(0)
                    self._checkLayerActive(l_i)
            return

        # Decrease delay on events
        for l_i, l in enumerate(self.layers):
            decr = dt
            events = self.layers[l_i].events
            # Decrease delays of as many events as delta-time encompasses
            while decr > 0:
                oldDelay = events[0].delay
                if decr < oldDelay:
                    events[0].delay -= decr
                else:
                    self.layers[l_i].curEvent = events[0]
                    events.pop(0)
                    self._checkLayerActive(l_i)
                decr -= oldDelay

        if not self._updLyrDist():
            # No layers are active
            # Nothing to do
            return

        # Send events to clients
        for c_i, c in enumerate(self.clients):
            curEvent = self.layers[c.layer].curEvent
            # Only update the client's beeper frequency if it needs changing
            if c.curHz != curEvent.hz:
                c.doEvent(curEvent)


# TEST
clients = []
for c_i in range(5):
    clients.append(Client("<PUT CONNECTION HERE>"))
man = Manager(clients)
for l_i in range(3):
    man.addLayer()

events = ((0, 1337), (64, 0), (64, 1), (64, 0), (64, 1), (64, 0), (64, 0), (64, 0))
for e in events:
    man.addToLayer(0, Event(*e))
events2 = ((0, 1), (64, 0), (64, 1), (64, 0), (64, 0), (64, 2), (64, 0), (64, 0))
for e in events2:
    man.addToLayer(1, Event(*e))
events3 = ((0, 50), (64, 0), (64, 1), (64, 0), (64, 0), (64, 0), (64, 20), (64, 0))
for e in events3:
    man.addToLayer(2, Event(*e))

for l in man.layers:
    print(l)

from time import sleep
print("ACTIVE: \t{}".format(man.numActiveLayers))
man.update(0)
print("ACTIVE: \t{}".format(man.numActiveLayers))
for i in range(14):
    print("ITERATION #{}".format(i))
    sleep(0.5)
    man.update(32)
    print("ACTIVE: \t{}".format(man.numActiveLayers))
# EXPECTED OUTPUT: 3, 0, 3, 2, 1, 1, 2
# EOF TEST

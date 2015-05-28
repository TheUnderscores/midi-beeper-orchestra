# midi-beeper-orchestra - program to create an orchestra from PC speakers
# Copyright (C) 2015 The Underscores

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Add ./.. to the module search path
import sys
sys.path.append("..")

import common.network

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

class Client():
    def __init__(self, host=None):
        self.host = host
        self.curHz = 0

    def doEvent(self, event):
        """
        Tell client to beep based on event frequency.
        The client will ONLY receive the frequency to beep at.
        """
        self.curHz = event.hz
        common.network.send("freq", self.curHz, self.host)

class Manager:
    def __init__(self, clients):
        self.layers = []
        self.layers_active = []
        self.layers_done = []
        self.numActiveLayers = 0
        # Connected clients
        self.clients = clients

    def _updateLayerDistribution(self):
        """
        Updates layer distribution.
        In other words, which client is playing which channel.
        Return True if there are active layers
        Return False if there are no active layers
        """
        self._updateNumberOfActiveLayers()

        if self.numActiveLayers == 0:
            # No layers are active
            # No use assigning layers
            # Set all client frequencies to 0
            for c in self.clients:
                c.layer = 0
            return False

        if len(self.clients) <= self.numActiveLayers:
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
        self._checkLayerActive(len(self.layers)-1)
        self.layers_done.append(False)

    def rmvLayer(self, l_i):
        """Removes layer l_i from manager's layer stack"""
        self.layers.pop(l_i)
        self.layers_active.pop(l_i)
        self.layers_done.pop(l_i)

    def _popFromLayer(self, l_i):
        """Pops first event in layer l_i if layer is not empty"""
        events = self.layers[l_i].events
        self.layers[l_i].curEvent = events[0]
        events.pop(0)
        if len(events) == 0:
            # Fill layer with a dummy event
            events.append(Event(1024, 0))
            # We'll assume that this layer is done giving events
            self.layers_done[l_i] = True
        self._checkLayerActive(l_i)

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

    def _updateNumberOfActiveLayers(self):
        """Update number of active layers"""
        self.numActiveLayers = 0
        for l_i, active in enumerate(self.layers_active):
            if active:
                self.numActiveLayers += 1

    def addToLayer(self, l_i, event):
        """Adds given event to layer of specified index l_i"""
        self.layers[l_i].events.append(event)

    def isDone(self):
        for done in self.layers_done:
            if done == False:
                return False
        return True

    def update(self, dt):
        """
        Updates the manager.
        dt is delta-time in milliseconds (integer, not float).
        Setting dt to 0 causes function to effectively acts as
        a primer/initializer.
        """
        if dt == 0:
            # This effectively acts as a primer
            for l_i, l in enumerate(self.layers):
                events = self.layers[l_i].events
                if events[0].delay <= 0:
                    self._popFromLayer(l_i)

        else:
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
                        self._popFromLayer(l_i)
                        decr -= oldDelay

        self._updateLayerDistribution()

        # Send events to clients
        for c_i, c in enumerate(self.clients):
            curEvent = self.layers[c.layer].curEvent
            # Only update the client's beeper frequency if it needs changing
            if c.curHz != curEvent.hz:
                c.doEvent(curEvent)

#!/usr/bin/env python3

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

import datetime
import sys
sys.path.append("..")

import common.network
import manager
import midiparser

if not common.network.createServer(12002):
    print("ACK! Could not create server socket!")
    sys.exit(-1)

total_clients = int(sys.argv[1]) or 1

# Wait for all clients to connect
while len(common.network.getClients()) < total_clients:
    data, host = common.network.receive()
    print("{} from {}".format(data, host))
    if data["type"] == "discover":
        common.network.addClient(manager.Client(host=host))

server_manager = manager.Manager(common.network.getClients())
print("clients: \t{}".format(len(server_manager.clients)))

##################################
midi_file = sys.argv[2]
layers = midiparser.process(open(midi_file,'rb').read(),total_clients)
for layer in layers:
    if len(layer.events) !=0:
        server_manager.addLayer(layer=layer)

# Start server main loop

first = datetime.datetime.now()
server_manager.update(0)
last = datetime.datetime.now()

iter = 0
while True:
    first = datetime.datetime.now()
    #print(int((first - last).microseconds))
    server_manager.update(int((first - last).microseconds))
    last = datetime.datetime.now()
    iter+=1
    if server_manager.isDone(): break

print("iters: {}".format(iter))
sys.exit(0)

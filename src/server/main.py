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

# TESTING
notes = {
    'A4' :440,
    'B4f':466,
    'B4' :494,
    'C5' :523,
    'D5f':554,
    'D5' :587,
    'E5f':622,
    'E5' :659,
    'F5' :698,
    'G5f':740,
    'G5' :784,
    'A5f':831,
    'A5' :880,
    'B5f':932,
    'B5' :988,
    'C6' :1047,
    'D6f':1109,
    'D6' :1175,
    'E6f':1245,
    'F6' :1318,
    'G6f':1480,
    'A6' :1760,
    'B6f':1865,
    'C7' :2093
}

server_manager.addLayer()
# Quarter note length
tick = 512
events1 = (
    # Wait a little before starting
    (tick, 0),

    # VERSE #1

    # There are no strangers to love
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/4, notes['B6']),
    (tick/4, 0),
    (tick/2, notes['B6']),
    (tick/2, notes['D6f']),
    (tick*0.75, notes['B6f']),
    (tick/4, notes['A6f']),
    (tick*1.5, notes['G5f']),

    (tick*2.5, 0),

    # You know the rules, and so do I
    (tick/4, notes['A6f']),
    (tick/4, 0),
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/2, notes['B6']),
    (tick/4, notes['A6f']),
    (tick*0.75, 0),
    (tick/4, notes['G5f']),
    (tick/4, 0),
    (tick/2, notes['G6f']),
    (tick/2, 0),
    (tick/2, notes['G6f']),
    (tick/2, 0),
    (tick*1.5, notes['D6f']),

    (tick*1.5, 0),

    # Something something something... thinking of
    (tick/4, notes['A6f']),
    (tick/4, 0),
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/2, notes['B6']),
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/4, notes['D6f']),
    (tick*0.75, 0),
    (tick/2, notes['B6f']),
    (tick/2, notes['A6f']),
    (tick/4, notes['B6f']),
    (tick/4, notes['A6f']),
    (tick, notes['G5f']),

    (tick*1.5, 0),

    # You wouldn't get this from, any other guy
    (tick/4, notes['A6f']),
    (tick/4, 0),
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/2, notes['B6']),
    (tick/2, notes['A6f']),
    (tick, notes['G5f']),
    (tick/4, notes['D6f']),
    (tick/4, 0),
    (tick/4, notes['D6f']),
    (tick/4, 0),
    (tick/2, notes['D6f']),
    (tick/2, notes['E6f']),
    (tick, notes['D6f']),

    (tick, 0),

    # I just wanna tell you how I'm feeling
    (tick*2.5, notes['B6']),
    (tick/2, notes['D6f']),
    (tick/2, notes['E6']),
    (tick*0.75, notes['D6f']),
    (tick/4, 0),
    (tick/4, notes['D6f']),
    (tick/4, 0),
    (tick/2, notes['D6f']),
    (tick/2, notes['E6f']),
    (tick/2, notes['D6f']),
    (tick/4, notes['G5f']),
    (tick/4, 0),
    (tick, notes['G5f']),

    (tick*1.5, 0),

    # I wanna make you understand
    (tick/2, notes['G5f']),
    (tick/2, notes['A6f']),
    (tick/2, notes['B6f']),
    (tick/2, notes['B6']),
    (tick, notes['A6']),
    (tick/2, notes['D6f']),
    (tick/2, notes['E6f']),
    (tick, notes['D6f']),

    (tick/2, 0)
    
    # CHORUS

    # Never ganna give you up
    (tick/4, notes['G5f']),
    (tick/4, notes['A6f']),
    (tick/4, notes['B6']),
    (tick/4, notes['A6f']),
    (tick/2, notes['E6f']),
    (tick/4, 0),
    (tick*0.75, notes['E6f']),
    (tick*1.5, notes['D6f']),

    # Never ganna let you down
    (tick/4, notes['G5f']),
    (tick/4, notes['A6f']),
    (tick/4, notes['B6']),
    (tick/4, notes['A6f'])
)
for e in events1:
    server_manager.addToLayer(0, manager.Event(*e))
# EOF TESTING

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

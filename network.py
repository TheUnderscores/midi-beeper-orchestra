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

import socket
import json

global sock
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def createServer(port):
    sock.bind(('', port))

def send(type, value, client):
    sock.sendto(json.dumps({"type": type, "val": value}).encode(), client)

def receive():
    data, client = sock.recvfrom(1024)
    return json.loads(data.decode()), client


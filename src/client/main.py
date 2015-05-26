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

import sys
sys.path.append("..")
import common.network
import beep

common.network.send("discover", 1, ("192.168.129.88", 12002))

beep.init()

while True:
    data, client = common.network.receive()
    print("Received:", data)

    if data["type"] == "freq":
        beep.beep(data["val"])
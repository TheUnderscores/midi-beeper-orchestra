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

# TODO : figure out how we're going to work the imports.
# Our current system will *not* work with the files spread out like this.

# Add ./.. to the module search path
import sys
sys.path.append("..")

import common.network

class Client():
    def __init__(self, host=None):
        self.host = host
        self.frequency = 0

    def setFrequency(self, freq):
        common.network.send("freq", freq, self.host)

# midi-beeper-orchestra - program to create an orchestra from PC speakers
# Copyright (C) 2015 The Underscores
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import math

def MIDItoHz(MIDIval):
    """
    Converts a MIDI note, MIDIval, value to the equivalent hertz value
    """
    return (2**((MIDIval-69)/12))*440

def hzToMIDI(hz):
    """
    Converts hertz, hz, to MIDI note equivalent
    """
    midi = 2**((hz-69)/12) * 440
    return int(midi + 0.5)

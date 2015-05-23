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

# With guidance from from code at http://www.johnath.com/beep/beep.c

import fcntl
import os
from sys import stdout
from ctypes import c_int

# Linux kernel ioctl request number for the PC speaker
KIOCSOUND = int(0x0004B2F)

# From the afforementioned source file :
#
# This number represents the fixed frequency of the original PC XT's
# timer chip (the 8254 AFAIR), which is approximately 1.193 MHz. This
# number is divided with the desired frequency to obtain a counter value,
# that is subsequently fed into the timer chip, tied to the PC speaker.
# The chip decreases this counter at every tick (1.193 MHz) and when it
# reaches zero, it toggles the state of the speaker (on/off, or in/out),
# resets the counter to the original value, and starts over. The end
# result of this is a tone at approximately the desired frequency. :)

clock_tick_rate = 1193180

def init():
    """
    Initialize beep module. Will fall back to using '\a' if
    /dev/console is unable to be opened for whatever reason.
    """
    global consolefd

    consolefd = os.open("/dev/console", os.O_WRONLY)

    if consolefd is None:
        print("Couldn't open /dev/console for writing")
        print("Falling back to using '\a' for beeps")
        return

def beep(freq):
    """
    Beep using the specified frequency. Will fall back to using '\a'
    if the ioctl() interface is unusable for whatever reason.
    """
    if consolefd is None:
        stdout.write('\a')

    # Special case for frequency of 0
    # Not bothering to check because chances are that if one is sending
    # frequency 0, they were able to get it to make sound in the first
    # place. Plus, it makes no sound anyways.
    if freq == 0:
        fcntl.ioctl(consolefd, KIOCSOUND, 0)
        return

    if fcntl.ioctl(consolefd, KIOCSOUND, int(clock_tick_rate/freq)) < 0:
        print("Unable to use the ioctl() interface to control beeps")
        print("Falling back to using '\a' for beeps")
        stdout.write('\a')

#   Copyright (C) 2018 Chris Billington
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
from select import select
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import evdev
import evdev.ecodes as ev

from .xbmcclient import PacketACTION, ACTION_BUTTON, PacketHELO, ICON_PNG


# Kodi eventserver details:
HOST = 'localhost'
PORT = 9777

# Mapping of keys to kodi actions:
MEDIA_KEYS = {ev.KEY_MUTE: "Mute",
              ev.KEY_VOLUMEDOWN: "VolumeDown",
              ev.KEY_VOLUMEUP: "VolumeUp",
              ev.KEY_PLAY: "Play",
              ev.KEY_PAUSE: "Pause",
              ev.KEY_PLAYPAUSE: "PlayPause",
              ev.KEY_STOP: "Stop",
              ev.KEY_NEXTSONG: "SkipNext",
              ev.KEY_PREVIOUSSONG: "SkipPrevious",
              ev.KEY_REWIND: "Rewind",
              ev.KEY_FASTFORWARD: "FastForward"}

# Key events:
PRESS = evdev.events.KeyEvent.key_down
RELEASE = evdev.events.KeyEvent.key_up
HOLD = evdev.events.KeyEvent.key_hold


class KodiClient(object):
    def __init__(self, host, port):
        self.addr = (host, port)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.have_said_hello = False

    def send_action(self, action):
        packet = PacketACTION(actionmessage=action, actiontype=ACTION_BUTTON)
        packet.send(self.sock, self.addr)

    def handle_event(self, event):
        """Check if this is an event we are interested in, and handle it
        appropriately. Return True if we handled it and False if we did not."""
        if event.type == ev.EV_KEY:
            key = event.code
            if key in MEDIA_KEYS:
                if event.value in [PRESS, HOLD]:
                    self.send_action(MEDIA_KEYS[key])
                return True
        return False


def get_mediakey_devices():
    """Find all input devices that have any of given media keys."""
    devices = []
    for device_file in evdev.list_devices():
        device = evdev.InputDevice(device_file)
        keys = set(device.capabilities().get(ev.EV_KEY, []))
        if keys.intersection(MEDIA_KEYS):
            devices.append(device)
    return devices


class grab_all(object):
    """Context manager to grab all input from the devices, preventing other
    applications from getting events."""
    def __init__(self, devices):
        self.devices = devices
        self.grabbed = []

    def __enter__(self):
        for dev in self.devices:
            dev.grab()
            self.grabbed.append(dev)

    def __exit__(self, *args):
        while self.grabbed:
            dev = self.grabbed.pop()
            dev.ungrab()


class KeyRedirection(object):
    def __init__(self):
        self.thread = None
        self.stop_fd_reader = None
        self.stop_fd_writer = None
        self.running = False

    def start(self):
        self.stop_fd_reader, self.stop_fd_writer = os.pipe()
        self.thread = Thread(target=self.mainloop)
        self.thread.start()
        self.running = True

    def stop(self):
        os.write(self.stop_fd_writer, b'stop')
        os.close(self.stop_fd_writer)
        self.stop_fd_writer = None
        self.thread.join()
        self.thread = None
        self.running = False

    def mainloop(self):
        kodi_client = KodiClient(HOST, PORT)
        devices = get_mediakey_devices()
        with grab_all(devices):
            with evdev.UInput.from_device(*devices) as ui:
                for event in self.read_events(devices):
                    if not kodi_client.handle_event(event):
                        ui.write_event(event)
                        ui.syn()

    def read_events(self, devices):
        """Generator yielding event objects from device files. Raises StopIteration
        if there is data available for read on stop_fd"""
        devices_by_fd = {device.fd:  device for device in devices}
        fds = list(devices_by_fd) + [self.stop_fd_reader]
        while True:
            r, _, _ = select(fds, [], [], 1.0)
            if self.stop_fd_reader in r:
                os.read(self.stop_fd_reader, 1024)
                os.close(self.stop_fd_reader)
                self.stop_fd_reader = None
                raise StopIteration
            for fd in r:
                for event in devices_by_fd[fd].read():
                    yield event
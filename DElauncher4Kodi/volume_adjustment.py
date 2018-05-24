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

from subprocess import check_output, check_call
import pulsectl
from threading import Thread
import time

NULL_SINK_NAME = "DElauncher4Kodi.nullsink"
CLIENT_NAME = 'DElauncher4Kodi'


def make_null_sink(name):
    output = check_output(
        ['pactl', 'load-module', 'module-null-sink',
         f'sink_name={name}"',
         f'sink_properties=device.description={name}'])
    module_id = int(output.strip())
    return module_id


def unload_module(module):
    check_call(['pactl', 'unload-module', str(module)])


def default_sink_info(pulse):
    """Return the default sink, its volume, and mute state"""
    print('  Getting current default sink info:')
    default_sink_name = pulse.server_info().default_sink_name
    for sink in pulse.sink_list():
        if sink.name == default_sink_name:
            volume = sink.volume.value_flat
            mute = sink.mute
            print(f'    name: {sink.name}')
            print(f'    volume: {volume*100:.00f} %')
            print(f'    mute: {bool(mute)}')
            return sink, volume, mute
    raise RuntimeError("Couldn't find default sink")
    

def set_null_sink_default(pulse):
    print('  Creating null sink as default sink:')
    null_sink_module = make_null_sink(NULL_SINK_NAME)
    for sink in pulse.sink_list():
        if sink.owner_module == null_sink_module:
            pulse.default_set(sink)
            print(f'    name: {sink.name}')
            print(f'    module #: {null_sink_module}')
            return sink, null_sink_module
    raise RuntimeError("Could not set null sink default")


def move_all_streams_to_sink(pulse, target_sink):
    print('  Moving exising audio streams to null sink:')
    orig_sinks = {}
    for stream in pulse.sink_input_list():
        orig_sinks[stream] = stream.sink
        try:
            pulse.sink_input_move(stream.index, target_sink.index)
            print(f'    {stream.name}')
        except pulsectl.PulseOperationFailed:
            # Stream probably doesn't exist anymore
            del orig_sinks[stream]
    if not orig_sinks:
        print('    <no streams found>')
    return orig_sinks


def restore_streams(pulse, orig_sinks):
    print('  Moving streams back to default sink:')
    for stream, sink in orig_sinks.items():
        try:
            pulse.sink_input_move(stream.index, sink)
            print(f'    {stream.name}')
        except pulsectl.PulseOperationFailed:
            print(f'    [IGNORED] {stream.name} (no longer present)')
    if not orig_sinks:
        print('    <no streams to restore>')


class VolumeAdjustment(object):
    def __init__(self):
        self.running = False
        self.sink = None
        self.volume = None
        self.mute = None
        self.null_sink = None
        self.null_sink_module = None
        self.orig_streams = None
        self.thread = None
        self.stopping = False

    def start(self):
        print('Initiating audio reconfiguration')
        with pulsectl.Pulse(CLIENT_NAME) as pulse:
            self.sink, self.volume, self.mute = default_sink_info(pulse)
            self.null_sink, self.null_sink_module = set_null_sink_default(pulse)
            self.orig_streams = move_all_streams_to_sink(pulse, self.null_sink)
            print(r'  Setting original default sink to 100 % volume')
            pulse.volume_set_all_chans(self.sink, 1.0)
            pulse.mute(self.sink, 0)
        self.thread = Thread(target=self.wait_thread)
        self.thread.start()
        self.running = True
        print('Audio reconfiguration complete pending kodi startup\n')

    def wait_for_kodi(self, pulse):
        while not self.stopping:
            time.sleep(0.1)
            for stream in pulse.sink_input_list():
                if 'kodi' in stream.name.lower():
                    return stream
        return None

    def wait_thread(self):
        with pulsectl.Pulse(CLIENT_NAME) as pulse:
            print('Waiting for kodi audio stream to appear')
            stream = self.wait_for_kodi(pulse)
            if stream is not None:
                print('  Audio stream has appeared')
                try:
                    print('  moving kodi audio stream to original default sink')
                    pulse.sink_input_move(stream.index, self.sink.index)
                except pulsectl.PulseOperationFailed:
                    pass

    def stop(self):
        print('Restoring audio configuration')
        self.stopping = True
        self.thread.join()
        with pulsectl.Pulse(CLIENT_NAME) as pulse:
            # Volume to zero, then move streams, then restore actual volume. This
            # helps prevents clicks and pops when moving streams
            print('  Setting original default sink to 0 % volume')
            pulse.volume_set_all_chans(self.sink, 0.000)
            pulse.mute(self.sink, self.mute)
            print('  Restoring original default sink')
            pulse.default_set(self.sink)
            restore_streams(pulse, self.orig_streams)
            print('  Unloading null sink module')
            unload_module(self.null_sink_module)
            time.sleep(0.1)
            print('  Restoring original volume')
            pulse.volume_set_all_chans(self.sink, self.volume)
            print('Audio configuration restored\n')
        self.sink = None
        self.volume = None
        self.mute = None
        self.null_sink = None
        self.orig_streams = None
        self.thread = None
        self.running = False
        self.null_sink_module = None
        self.stopping = False

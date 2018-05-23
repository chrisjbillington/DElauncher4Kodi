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

import sys
import os
from contextlib import contextmanager
from .key_redirection import KeyRedirection
from .volume_adjustment import VolumeAdjustment
import subprocess

# # FIFO used to control this program while its running:
# FIFO_NAME = '/tmp/kodi-de-diplomat.fifo'

# def getcommand():
#     """Read one command from the FIFO and return it as a bytestring"""
#     command = b''
#     control_fd = os.open(FIFO_NAME, os.O_RDONLY)
#     while True:
#         data = os.read(control_fd, 1024)
#         command += data
#         if not data:
#             os.close(control_fd)
#             return command

# def mainloop():

#     key_redirector = KeyRedirection()
#     volume_adjuster = VolumeAdjustment()
#     try:
#         while True:
#             command = getcommand()
#             if command == b'start\n' and not key_redirector.running:
#                 key_redirector.start()
#                 volume_adjuster.start()
#             elif command == b'stop\n' and key_redirector.running:
#                 key_redirector.stop()
#                 volume_adjuster.stop()
#             elif command == b'shutdown\n':
#                 break
#     except KeyboardInterrupt:
#         if key_redirector.running:
#             key_redirector.stop()
#             volume_adjuster.stop()

# @contextmanager
# def umask(new_mask):
#     cur_mask = os.umask(new_mask)
#     yield
#     os.umask(cur_mask)


# def main():
#     if os.path.exists(FIFO_NAME):
#         os.unlink(FIFO_NAME)
#     try:
#         with umask(0o000):
#             os.mkfifo(FIFO_NAME, 0o622)
#         mainloop()
#     finally:
#         os.unlink(FIFO_NAME)

def main():

    key_redirector = KeyRedirection()
    volume_adjuster = VolumeAdjustment()

    try:
        key_redirector.start()
        volume_adjuster.start()
        subprocess.call(sys.argv[1:])
    finally:
        key_redirector.stop()
        volume_adjuster.stop()

if __name__ == '__main__':
    main()
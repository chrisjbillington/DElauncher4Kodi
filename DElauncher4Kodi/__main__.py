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
import subprocess
from contextlib import contextmanager
from .key_redirection import KeyRedirection
from .volume_adjustment import VolumeAdjustment
from . import __version__

LOCKFILE = '/tmp/DElauncher4Kodi.lock'
errmsg = ('DElauncher4Kodi already running, or did not close correctly. ' +
          f'If the latter, remove the lock file {LOCKFILE} ' + 
           '(or reboot) and try again.')

@contextmanager
def lockfile(path, errmsg):
    try:
        os.open(path, os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        sys.stderr.write(errmsg + '\n')
        sys.exit(1)
    try:
        yield
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def main():
    key_redirector = KeyRedirection()
    volume_adjuster = VolumeAdjustment()
    with lockfile(LOCKFILE, errmsg):
        print(f'This is DElauncher4Kodi version {__version__}.')
        print('Please report bugs to ' +
              'github.com/chrisjbillington/DElauncher4Kodi/\n')
        try:
            key_redirector.start()
            volume_adjuster.start()
            print('Starting kodi...')
            try:
                subprocess.call(sys.argv[1:])
            except KeyboardInterrupt:
                sys.stderr.write('Interrupted\n')
            else:
                print('Kodi exited\n')
        finally:
            key_redirector.stop()
            volume_adjuster.stop()
            print('Done')
if __name__ == '__main__':
    main()
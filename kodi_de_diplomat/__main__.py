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
from .key_redirection import KeyRedirection
from .volume_adjustment import VolumeAdjustment
import subprocess

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
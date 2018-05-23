# To upload a version to PyPI, run:
#
#    python3 setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python3 setup.py register

import sys
import os
from setuptools import setup
from setuptools.command.install import install

VERSION = '1.0.0'

# Auto generate a __version__ package for the package to import
with open(os.path.join('kodi_de_diplomat', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n"%VERSION)


def checkrun(cmd):
    rc = os.system(cmd)
    if rc:
        sys.exit(rc)


class PostInstallCommand(install):
    def run(self):
        # Add udev group, add user to the group, and add udev rule to allow the
        # group to write to /dev/uinput
        try:
            checkrun(f'getent group uinput > /dev/null || groupadd uinput')
            checkrun(f'adduser $SUDO_USER uinput')
            checkrun('udevadm control --reload-rules && sudo udevadm trigger')
        except SystemExit:
            msg = "Setting uinput permissions failed, did you run with sudo?\n"
            sys.stderr.write(msg)
            raise
        install.run(self)


setup(name='kodi_de_diplomat',
      version=VERSION,
      description="Kodi launcher grabbing media keys and adjusting system volume.",
      author='Chris Billington',
      author_email='chrisjbillington@gmail.com',
      url='https://bitbucket.org/cbillington/kodi_de_diplomat/',
      license="GPL2",
      packages=['kodi_de_diplomat'],
      data_files = [
                    ('share/applications', ['data/org.kodi_de_diplomat.desktop']),
                    ('/etc/udev/rules.d', ['data/99-uinput-group-access.rules'])
                   ],
      install_requires=['evdev', 'pulsectl'],
      cmdclass={'install': PostInstallCommand},
     )


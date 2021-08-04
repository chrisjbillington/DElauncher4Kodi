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

VERSION = '1.2.3'

# Auto generate a __version__ package for the package to import
with open(os.path.join('DElauncher4Kodi', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n"%VERSION)


def checkrun(cmd):
    rc = os.system(cmd)
    if rc:
        sys.exit(rc)

def post_install():
    # Add udev group, add user to the group, and add udev rule to allow the
    # group to write to /dev/uinput, ensure uinput module is loaded
    try:
        checkrun(f'getent group uinput > /dev/null || groupadd uinput')
        checkrun(f'usermod -a -G uinput $SUDO_USER')
        checkrun(f'usermod -a -G input $SUDO_USER')
        checkrun(f'udevadm control --reload-rules && udevadm trigger')
        checkrun(f'modprobe uinput')
    except SystemExit:
        msg = "Adding uinput group failed, did you run with sudo?\n"
        sys.stderr.write(msg)
        raise

class Install(install):
    def run(self):
        install.run(self)
        post_install()

setup(
    name='DElauncher4Kodi',
    version=VERSION,
    description="Kodi launcher grabbing media keys and adjusting system volume.",
    author='Chris Billington',
    author_email='chrisjbillington@gmail.com',
    url='https://github.com/chrisjbillington/DElauncher4Kodi/',
    license="GPL2",
    packages=['DElauncher4Kodi'],
    data_files=[
        ('share/applications', ['data/org.DElauncher4Kodi.desktop']),
        ('/etc/udev/rules.d', ['data/99-DElauncher4Kodi-uinput-group-access.rules']),
        ('/etc/modules-load.d', ['data/DElauncher4Kodi.conf']),
    ],
    install_requires=['evdev', 'pulsectl'],
    cmdclass={'install': Install},
)


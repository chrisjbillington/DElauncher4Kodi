DElauncher4Kodi 1.2
====================

[View on PyPI](http://pypi.python.org/pypi/DElauncher4Kodi)
| [View on Github](https://github.com/chrisjbillington/DElauncher4Kodi/)

# Table of Contents
1. [Introduction](#Introduction)
2. [Installation](#Installation)
3. [Ear safety warning](#Ear-safety-warning)
4. [Implementation details](#Implementation-details)
5. [Uninstalling](#Uninstalling)
5. [Troubleshooting](#Troubleshooting)

## Introduction

Running `kodi` as well as a desktop environment (DE) such as `gnome-shell` on the
same computer requires a bit of...cooperation...between the two. The following two
problems exist for anyone trying to do this:

* When running `kodi` from within gnome-shell, the media keys may be handled by the
  desktop environment instead of by `kodi`. That means the play/pause/rewind/etc
  media keys on a remote or keyboard don't work, and the volume up/down keys, which
  modify the system volume rather than `kodi`'s volume, work but show an obnoxious
  popup and make an annoying sound (the same as when you change the volume in
  `gnome-shell` normally).

* When running `kodi` as a separate session (as in, selecting it from the login
  screen), the media keys work, but the volume keys control the `kodi` app volume.
  This is nice, except that the maximum volume is limited to the system volume
  setting, which is left at whatever it was last set to by the user in `gnome-
  shell`, and is now not adjustable within `kodi`. Also, running `kodi` as a separate
  desktop session is a pain in the neck if you actually want to switch between `kodi`
  and `gnome-shell` (to watch netflix in chrome or whatever), since typing
  passwords on tiny keyboards on HTPC remotes is annoying, and enabling
  passwordless login is bad security practice (and annoying to set up). Also media
  computers are often slow for things that are not GPU accelerated, so logging out
  and in again can be pretty slow.

`DElauncher4Kodi` solves both problems by setting the system volume to 100% before
launching `kodi`, and grabbing all keyboard input and forwarding media keys as
commands to `kodi` directly.

It should work on all desktop environments, not just `gnome-shell`. It only assumes
you are running linux and PulseAudio.

## Installation

To install, run:

```bash
sudo pip3 install DElauncher4Kodi
```

and then reboot.

(replace `pip3` with `pip` if that is what the pip binary for Python 3 is called on
your computer. Python 3.6+ required)

A new launcher should appear in your DE's menu/launcher called "DE launcher for Kodi". Running that instead of the ordinary `kodi` launcher will turn on the
volume change and media key redirection, run `kodi`, then restore things to normal
once `kodi` exits. You can continue to use your DE while `kodi` is running, on a
separate monitor, by switching workspaces, or pressing, alt-tab or whatever, but
there will be no audio other than `kodi` and media keys will not have any effect on
any programs other than `kodi`.

to uninstall, run:
```bash
sudo pip3 uninstall DElauncher4Kodi
```

## Ear safety warning
Because `DElauncher4Kodi` sets the system volume to 100%, either a bug in my
program or deliberate modification of PulseAudio settings by the user whilst kodi
is running has the potential to allow other running applications to output audio at
100% volume. For the safety of your ears should this occur, do not use
`DElauncher4Kodi` with headphones. You have been warned.

## Implementation details

### Media key forwarding
`DElauncher4Kodi` uses the linux kernel's `evdev` library to capture all key
events from devices that have media keys. If an event corresponds to one of the
media keys `DElauncher4Kodi` knows about, it sends the appropriate command to
`kodi` over its UDP interface on `localhost:9777`. Otherwise, it forwards the event
to a `uinput` device (using the kernel's `uinput` library) such that it appears to
the system as an ordinary keypress, which the window manager will receive as
normal. This latter forwarding of events back to the system requires
`DElauncher4Kodi` either run as root, or have permission to write to
`/dev/uinput`. The installer configures a `udev` rule to allow the `uinput` group
to write to `/dev/uinput` and adds the user to that group. `DElauncher4Kodi` will
therefore only be able to forward media keys when run as that user - other users
need to be added to the `uinput` group in order for it to work for them too.

### Audio levels
`DElauncher4Kodi` performs the following actions before starting kodi using the `pulseaudio` library:

* Notes the current volume and mute state of the current output

* Sets a 'null sink' as the default output so that any new applications will not
  output any audio

* Moves any existing audio output to the null sink to stop them producing audio

* Sets the real output to 100% volume and unmuted

Once `kodi` starts, its audio output is moved to the real output (as it is
initially set to the null sink, since the null sink was default). Then, once `kodi`
exits, `DElauncher4Kodi`

* Restores the volume and mute state of the output

* Deletes the null sink

* Moves all application output back to whatever device they were outputting to
  beforehand.

This has the effect of silencing all audio other than `kodi` whilst `kodi` is running

## Uninstalling

`sudo pip3 uninstall DElauncher4Kodi` will remove all files added by the
installer. If you installed without pip, you will need to delete them manually.

Installation performs the following actions:

* Installs Python package `DElauncher4Kodi`

* Adds a udev rule `/etc/udev/rules.d/99-DElauncher4Kodi-uinput-group-access.rules`

* Creates group `uinput` if it does not exist

* Adds the current user to the groups `uinput` and `input` 

* Adds a desktop file to `/usr/local/share/applications/DElauncher4Kodi.desktop`

Uninstalling with pip will not remove the user from the `uinput` and `input` groups
or delete the `uinput` group. Run `sudo delgroup uinput; sudo deluser $USER input`
to do this. However, it's possible that the user was already in the `input` group
for some other reason, so removing them from the group may interfere with other
software.

## Troubleshooting

Plugging in a keyboard or wireless remote after starting kodi? Sorry,
`DElauncher4Kodi` doesn't support hot-plugging - you'll have to restart kodi
before the media keys on a newly plugged in device will be correctly forwarded to
kodi.

Something else not working? Try running `DElauncher4Kodi` from the command line:

```bash
python3 -m DElauncher4Kodi kodi
```

And see if the output it produces explains what's wrong. For example, only one
instance of `DElauncher4Kodi` can run at a time, and if it doesn't shut down
properly, it will display an error because it thinks another instance is still
running. This can be fixed by rebooting or by deleting the lock file
`/tmp/DElauncher4Kodi.lock`. If you are seeing Python tracebacks in the terminal
output, this indicates either a bug in my code or something I didn't anticipate
might go wrong. Please report this as an issue on github so I can fix it.

### Example terminal output

This is what the terminal output should look like when everything is running
correctly:

```text
$ /usr/bin/python3 -m DElauncher4Kodi kodi
This is DElauncher4Kodi version 1.2.0.
Please report bugs to github.com/chrisjbillington/DElauncher4Kodi/

Initiating key capturing
  Capturing media keys from:
    /dev/input/event21: lircd-uinput
    /dev/input/event14: Dell WMI hotkeys
    /dev/input/event11: Intel HID events
    /dev/input/event4: AT Translated Set 2 keyboard
Key capturing setup complete

Initiating audio reconfiguration
  Getting current default sink info:
    name: alsa_output.pci-0000_00_1f.3.analog-stereo
    volume: 28 %
    mute: False
  Creating null sink as default sink:
    name: DElauncher4Kodi.nullsink_
    module #: 98
  Moving exising audio streams to null sink:
    Spotify
  Setting original default sink to 100 % volume
Audio reconfiguration complete pending kodi startup

Starting kodi...
Waiting for kodi audio stream to appear
  Audio stream has appeared
  moving kodi audio stream to original default sink
Kodi exited

Stopping key capturing
Key capturing stopped

Restoring audio configuration
  Setting original default sink to 0 % volume
  Restoring original default sink
  Moving streams back to default sink:
    Spotify
  Unloading null sink module
  Restoring original volume
Audio configuration restored

Done
```
Evil Pigeons
============

A 2-player game between an evil pigeon master that controls the pigeons, who wish to shit-load a fancy car, and a mad car owner who wishes to exterminate the nasty pigeons before they succeed.

Running from release
====================
A prebuilt binary is supplied for windows only for lack of resources and ease of installing required packages on linux (we didn't have access or time to access a mac).

The windows directory contains a single exe called "main.exe". Running it will run in fullscreen.

Game play
=========

Mad car owner: Mouse to move cursor, button to shoot. You can't kill a perched pigeon. Notice the lag between shots.
Piegons: keypad 1-4 to dive shit, keypad 1-4 and shift to mimic a dive without actually diving.

Command line parameters
=======================
Wether running from the exe or from run.sh / run.bat you can use the following command line parameters:
--window	run in windowed mode
--nomusic	run without the background music track (but with the birds flaps track and sounds)

Development options:
--setpos	run in a special setup mode (requires json)


Development and running from Source: Prerequisites
==================================================

Python version: The game was tested with python 2.6.4, but should work with 2.4 and above.

Ubuntu: sudo apt-get install python-numpy python-pygame

Linux (non ubuntu): install the python-pygame package

Window:

 Using python 2.6: (works, tested, py2exe doesn't work very well - produces executable that segfaults)
  get python and install: http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi
  get pygame and install: http://pygame.org/ftp/pygame-1.9.1.win32-py2.6.msi

 Using python 2.5:
  http://www.python.org/ftp/python/2.5.4/python-2.5.4.msi
  http://pygame.org/ftp/pygame-1.9.1.win32-py2.5.msi

Mac OS X:
 Untested. Should work fine since pygame is known to be supported on it.

Running from Source subdirectory
================================
running from the src subdirectory:

Linux and Mac: ./run.sh
Windows: run.bat (or just run)

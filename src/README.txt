Evil Pigeons Development README
===============================

The main readme for game play and running is provided in the release directory, ../release/README.txt

Getting the Source
==================

The source is hosted on github at.
    Repository page:    http://github.com/alon/evilpigeons
    The git url is:     git://github.com/alon/evilpigeons.git

To get:
 1. install git
  Ubuntu: sudo apt-get install git-core
  Linux: use the package manager
  Windows: Install using the installer here: http://code.google.com/p/msysgit
 2. clone:
  git clone git://github.com/alon/evilpigeons.git

Python version: The game was tested with python 2.6.4, and 2.5.4, but should work with 2.4 and above.

Ubuntu: sudo apt-get install python-pygame
Other Linux: install the python-pygame package

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

Program Credits
===============
Assets:              Maya for 3d, Photoshop
Asset Tweaking:      gimp, Imagemagick, SoX
Programming:         python, pygame
Development tools:   ipython, vim
Windows Executable:  py2exe


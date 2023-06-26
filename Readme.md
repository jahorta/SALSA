SALSA - Skies of Arcadia Legends Script Assistant
===================================================
SALSA is a GUI-based tool to assist in editing sct files in Skies of Arcadia Legends. Currently, SALSA allows for .sct file import and export and  


Requirements
------------
* [Python](https://www.python.org/) 3.10+
* Skies of Arcadia Legends script files (.sct).
  * Supports aklz compressed files

Getting Started
---------------
With Python 3.10+ installed, running SALSA.py should run the program. In the event that this does not start the program, make sure it is running with Python 3.10+.

Upon startup, a project should first be created or loaded. A project can contain an arbitrary number of scripts. Scripts can be imported using Project->Import Script, and exported using Project-> Export Script.

Features (Completed)
--------
* Instructions with editable paramter names and default parameters
* Parameter values can be displayed within instruction descriptions
* Script file import and export
* Script file addressing by setting starting memory address for script file for use with Dolphin Emulator. (change headers to include offset)
* Dialog string editing (Project->String Editor)

Features (In Progress)
--------
* Adding, removing, and changing instructions
* Moving instructions around within a section
* Program help

Features (Planned)
--------
* Grouping and moving sections around within a script
* Saving groups of sections separately
* Saving groups of instructions separately


Credits
-------
See credits.md for full credits

License
-------
Copyright (C) 2023. SALSA is licensed under the GNU General Public License, Version 3.0. See [LICENSE.md](/LICENSE.md) for full license text

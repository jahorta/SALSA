SALSA - Skies of Arcadia Legends Script Assistant
===================================================
SALSA is a GUI-based tool to assist in parsing and decoding the script system in Skies of Arcadia Legends. Currently, SALSA features two modes, an Instruction Edit mode and a Script Parsing mode.


Requirements
------------
* [Python](https://www.python.org/) 3.8+
* Extracted and Decrypted Skies of Arcadia Legends script files (.sct).
  * At this time, there is no support for decrypting the script files within SALSA. Information on how to extract and decrypt the .sct files can be found on the [Skies of Arcadia community discord](https://discord.gg/wMnXkhu)


Features
--------
* Definable instructions
* Parameter values can be displayed within instruction descriptions
* Script file parsing using instructions
* Script file addressing by setting starting memory address for script file for use with Dolphin Emulator.

Getting Started
---------------
With Python 3.8+ installed, running SALSA.py should run the program. Upon startup, Instruction Edit view will show up first. Here the tree on the left contains a list of instructions which can be annotated, while annotations can be displayed/edited on the right. In order to start parsing scripts, the script directory should be set first (File->Select Script Directory). Then, a script file can be selected to parse in the (File->Select SCT File). While encoded script files are visible in the sct file select window, an error will be produced if they are selected.

Credits
-------
See credits.md for full credits

License
-------
Copyright (C) 2021. SALSA is licensed under the GNU General Public License, Version 3.0. See [LICENSE.md](/LICENSE.md) for full license text

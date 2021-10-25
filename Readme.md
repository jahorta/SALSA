SALSA - Skies of Arcadia Legends Script Assistant
===================================================
SALSA is a GUI-based tool to assist in parsing and decoding the script system in Skies of Arcadia Legends. Currently, SALSA features two modes, an Instruction Edit mode and a Script Parsing mode.


Requirements
------------
* [Python](https://www.python.org/) 3.8+
* Extracted and Decrypted SoAL script files (*.sct). 
  * At this time, there is no support for decrypting the script files within SALSA


Features
--------
* Definable instructions
* Parameter values can be displayed within instruction descriptions
* Script file parsing using instructions

Getting Started
---------------
Upon startup, Instruction Edit view will show up first. In order to start parsing scripts, the script directory should be set first (File->Select Script Directory). Then, a script file can be selected to parse in the (File->Select SCT File). While encoded script files are visible in the sct file select window, an error will be produced if they are selected.

Credits
-------
See credits.md for full credits

License
-------
Copyright (C) 2021. SALSA is licensed under the GNU General Public License, Version 3.0. See [LICENSE.md](/LICENSE.md) for full license text

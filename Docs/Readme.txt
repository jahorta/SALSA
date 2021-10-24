SALSA - Skies of Arcadia Legends - Script Assistant
===================================================

SALSA is a GUI-based tool to assist in parsing and decoding the script system in Skies of Arcadia Legends. Currently, SALSA features two modes, an Instruction Edit mode and a Script Parsing mode.


Requirements
------------

* Python 3.8 was used to create this program. Previous versions of Python may not work.
* Decrypted SoAL script files (*.sct). At this time, there is no support for decrypting the script files within SALSA.


Features
--------

* Definable instructions
* Parameter values can be displayed within instruction descriptions
* Script file parsing using instructions


Instruction Descriptions
------------------------

Instruciton descriptions are flexible, in that certain modifiers can be used to display the result of parameters from the instruction, or even perform basic manipulation of those parameter values.

- Displaying a parameter value -
By enclosing a parameter name with greater and less than signs, e.g. <offset> for the parameter named offset, the text will be replaced by the result of the parameter. This is performed first, and can be used in other operations

- Basic Operations -
Certain basic operations are available 


Other notes
-----------

Hardcoded param 1 and the param1 referred to in some of the instruction notes are different parameters. Since instructions are able to take place over multiple frames, Param1 appears to be sent as a sort of indicator on the state of the instruction so that the desired function can continue where it left off. Bits within param1 are used to 
param1 & 1: initialize instruction
param1 & 2: run function
param1 & 8: terminate function

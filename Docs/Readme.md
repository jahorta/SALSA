SALSA - Skies of Arcadia Legends - Script Assistant
===================================================
SALSA is a GUI-based tool to assist in parsing and decoding the script system in Skies of Arcadia Legends. Currently, SALSA features two modes, an Instruction Edit mode and a Script Parsing mode.


Requirements
------------
* Python 3.8+
* Extracted and Decrypted SoAL script files (*.sct). 
  * At this time, there is no support for decrypting the script files within SALSA


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
Certain basic operations are available: add, subtract, multiply, and link. These operations all use a similar syntax and take in two parameters and can read hex, float, or ints. The format of the first parameter determines the format of the output.

- add - *add[(1),(2)]* - the value of (2) will be added to (1). The resultant number will be in the style of (1). All floats will be converted to ints before use.
  * e.g. *add[1,2]* -> 3

- subtract - *sub[(1),(2)]* - the value of (2) will be subtracted from (1). The resultant number will be in the style of (1). All floats will be converted to ints before use.
  * e.g. *sub[5,2]* -> 3
  
- multiply - *mul[(1),(2)]* - the value of (2) will be multiplied to (1). The resultant number will be in the style of (1). Multiplication of floats is allowed.
  * e.g. *mul[1,2]* -> 2
  
- link - *lnk[(1),(2)]* - Link determines the target of an offset. (1) is the name of the parameter to use as the start position. (2) is the offset. With instructions which link to other positions in the script file, a parameter is used to determine the jump offset to the linked data. The position of the offset parameter is used as the start point, with the value of the parameter being the offset itself
  *e.g. *lnk[offset,<offset>]* -> Target instruction/string. 


Other notes
-----------
Hardcoded param 1 and the param1 referred to in some of the instruction notes are different parameters. Since instructions are able to take place over multiple frames, Param1 appears to be sent as a sort of indicator on the state of the instruction so that the desired function can continue where it left off. Bits within param1 are used to 
param1 & 1: initialize instruction
param1 & 2: run function
param1 & 8: terminate function

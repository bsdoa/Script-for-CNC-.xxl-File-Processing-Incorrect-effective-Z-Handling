# Script-for-CNC-.xxl-File-Processing-Incorrect-effective-Z-Handling

I have a CNC file (with a .xxl extension) that contains code structured in the following way:

Pre-lines:
These lines begin with XG0 and can appear in one of the following six formats:

(1) XG0 X=... Y=... Z=-1.000 T=xx
(2) XG0 X=... Z=-1.000 T=xx
(3) XG0 Y=... Z=-1.000 T=xx
(4) XG0 X=... T=xx
(5) XG0 Y=... T=xx
(6) XG0 X=... Y=... T=xx
Following Triple of Lines:
Immediately after each pre-line, there is a triple of lines with the following structure:

First line: XG0 Z=-2.000 T=xx
Second line: XL2P Z=<positive number> T=xx Vxxxxxx
(This line provides the "effective Z" value.)
Third line: XG0 Z=-1.000 T=xx
Script Requirements:

Detection & Extraction:
The script should detect a pre-line (matching one of the six formats) and then immediately check for a following triple of lines matching the structure above.
From the second line of the triple (the one beginning with XL2P), the script must extract the effective Z value.

Pre-line Conversion:
The pre-line should then be converted into a line starting with XB where:

The X and/or Y values (if present) are preserved.
The effective Z extracted from the triple is inserted (i.e., Z=<effective Z>).
The T value remains unchanged.
The converted line ends with V1800 G=0.
Triple Replacement:
The entire triple of lines is to be replaced with a single line containing only the symbol ;.

Dynamic Effective Z:
The effective Z value must update for each triple. If the Z value in a new triple is different from the previous one, the script must use the new effective Z for converting subsequent pre-lines.

Preservation Rule:
Any lines containing a three-digit T value (e.g., T=123) should remain unmodified.

Issue:
Despite my efforts, the script currently does not update the effective Z correctly when a new triple with a different Z is encountered. The converted pre-lines continue to use the old effective Z even when a subsequent triple indicates a change. I am looking for suggestions or corrections that ensure the effective Z is updated dynamically and applied correctly to each pre-line conversion.

I made this script in chatgpt, however if anyone thinks I can make it simpler or has a better idea I am open to suggestions since I don't know much about python programming and other programming languages.
thanks in advance

I am sending a sample file which has its original format, the format after editing the script and finally how it should be correct..


--------------
original file:
--------------

H DX=799.000 DY=689.000 DZ=12.000 -A C=0 R1 *MM /def.TLG  BX=0 BY=0 BZ=0
XG0 X=162.656 Y=-450.985 Z=-1.000 T=8
XG0   Z=-2.000 T=8
XL2P   Z=5.000 T=8 V1000000
XG0   Z=-1.000 T=8
XG0  Y=-396.258  T=8
XG0   Z=-2.000 T=8
XL2P   Z=5.000 T=8 V1000000
XG0   Z=-1.000 T=8
XG0 X=116.289 Y=-450.985  T=8
XG0   Z=-2.000 T=8
XL2P   Z=5.000 T=8 V1000000
XG0   Z=-1.000 T=8
XG0 X=162.656   T=8
XG0   Z=-2.000 T=8
XL2P   Z=6.000 T=8 
XG0   Z=-1.000 T=8
XG0  Y=-396.258  T=8
XG0   Z=-2.000 T=8
XL2P   Z=6.000 T=8 
XG0   Z=-1.000 T=8
XG0 X=116.289 Y=-450.985  T=8
XG0   Z=-2.000 T=8
XL2P   Z=6.000 T=8 
XG0   Z=-1.000 T=8
XG0 X=212.733 Y=-396.258  T=8
XG0   Z=-2.000 T=8
XL2P   Z=5.000 T=8 
XG0   Z=-1.000 T=8
XG0 X=162.656   T=8
XG0   Z=-2.000 T=8
XL2P   Z=5.000 T=8 
XG0   Z=-1.000 T=8
XN X=4920

---------------------
after script editing: 
---------------------

H DX=799.000 DY=689.000 DZ=12.000 -A C=0 R1 *MM /def.TLG  BX=0 BY=0 BZ=0
XB X=162.656 Y=-450.985 Z=5.0 T=8 V1800 G=0
;
XB Y=-396.258 Z=5.0 T=8 V1800 G=0
;
XB X=116.289 Y=-450.985 Z=5.0 T=8 V1800 G=0
;
XB X=162.656 Z=5.0 T=8 V1800 G=0
XB Z=5.0 T=8 V1800 G=0
XL2P   Z=6.000 T=8 
XB Z=5.0 T=8 V1800 G=0
XB Y=-396.258 Z=5.0 T=8 V1800 G=0
XB Z=5.0 T=8 V1800 G=0
XL2P   Z=6.000 T=8 
XB Z=5.0 T=8 V1800 G=0
XB X=116.289 Y=-450.985 Z=5.0 T=8 V1800 G=0
XB Z=5.0 T=8 V1800 G=0
XL2P   Z=6.000 T=8 
XB Z=5.0 T=8 V1800 G=0
XB X=212.733 Y=-396.258 Z=5.0 T=8 V1800 G=0
XB Z=5.0 T=8 V1800 G=0
XL2P   Z=5.000 T=8 
XB Z=5.0 T=8 V1800 G=0
XB X=162.656 Z=5.0 T=8 V1800 G=0
XB Z=5.0 T=8 V1800 G=0
XL2P   Z=5.000 T=8 
XB Z=5.0 T=8 V1800 G=0
XN X=4920

------------------------
how would be as correct:
------------------------

H DX=799.000 DY=689.000 DZ=12.000 -A C=0 R1 *MM /def.TLG  BX=0 BY=0 BZ=0
XB X=162.656 Y=-450.985 Z=5.0 T=8 V1800 G=0
;
XB Y=-396.258 Z=5.0 T=8 V1800 G=0
;
XB X=116.289 Y=-450.985 Z=5.0 T=8 V1800 G=0
;
XB X=162.656 Z=6.0 T=8 V1800 G=0
;
XB Y=-396.258 Z=6.0 T=8 V1800 G=0
:
XB X=116.289 Y=-450.985 Z=6.0 T=8 V1800 G=0
:
XB X=212.733 Y=-396.258 Z=5.0 T=8 V1800 G=0
;
XB X=162.656 Z=5.0 T=8 V1800 G=0
;
XN X=4920



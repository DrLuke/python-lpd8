.. python-lpd8 documentation master file, created by
   sphinx-quickstart on Fri Mar  2 15:49:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Callbacks
=========

Python-lpd8 works with callbacks to let you know that a pad has been pressed or a knob has been turned.
Information about which program's pad/knob has been actuated is passed to the callback.

Signature
---------
Any callback function must have a signature compatible to the following:

.. py:function:: callback(programNum: int, padNum: int, knobNum: int, value: int, noteon: int, noteoff: int, cc: int, pc: int)

   :param programNum: Index of program pad/knob belongs to
   :param padNum: Index of pad that triggered call
   :param knobNum: Index of knob that triggered call
   :param value: Velocity for pads, value for knobs
   :param noteon: midi note of noteon message
   :param noteoff: midi note of noteoff message
   :param cc: midi control of control change message
   :param pc: midi program of program change message

The signature allows you to attach the same callback to all pads and knobs in all three modes.
There are four possible calling schemes depending on the modes used:

Pad in PAD mode
^^^^^^^^^^^^^^^
In pad mode you will get one call on pad press, and another one on pad release. You can differentiate between the two
by checking if noteon/noteoff is None. They will always be mutually exclusive.

==========  =========== =============
Param       Value press Value release
==========  =========== =============
programNum  0-3         0-3
padNum      0-7         0-7
knobNum     None        None
value       1-127       0
noteon      0-127       None
noteoff     None        0-127
cc          None        None
pc          None        None
==========  =========== =============

Pad in CC mode
^^^^^^^^^^^^^^
In cc mode you will get one call on pad press, and another one on pad release. The only way to differentiate between the
 two is to check if value is 0.

==========  =========== =============
Param       Value press Value release
==========  =========== =============
programNum  0-3         0-3
padNum      0-7         0-7
knobNum     None        None
value       1-127       0
noteon      None        None
noteoff     None        None
cc          0-127       0-127
pc          None        None
==========  =========== =============

Pad in PROG CHNG mode
^^^^^^^^^^^^^^^^^^^^^
In program change mode you will only get a call when the button is pressed. You also get no velocity data.

==========  ===========
Param       Value press
==========  ===========
programNum  0-3
padNum      0-7
knobNum     None
value       None
noteon      None
noteoff     None
cc          None
pc          0-127
==========  ===========

Knob
^^^^
The knob behaves the same way in all three modes. You get the position of the knob as the value.

==========  ===========
Param       Value turn
==========  ===========
programNum  0-3
padNum      None
knobNum     0-7
value       0-127
noteon      None
noteoff     None
cc          0-127
pc          None
==========  ===========
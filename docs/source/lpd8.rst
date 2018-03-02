.. python-lpd8 documentation master file, created by
   sphinx-quickstart on Fri Mar  2 15:49:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LPD8
====

The `Akai LPD8 <https://www.akaipro.de/lpd8>`_ is a midi controller with 8 velocity-sensitive pads and 8 knobs.

Programs
--------
The LPD8 memory bank can store 4 different programs. A program consists out of a configuration of notes and controls associated with each pad and knob.

Pads
----
The pads can operate in three different modes: Pad (Notes), CC (Control Change) and Prog Chng (Program Change).
Depending on the mode you are using, different midi events are emitted when you press and release buttons.
They also differ in how the velocity is handled.

================= ========= ============== ==============
Action            Pad       CC             Prog Chng
================= ========= ============== ==============
Pad Down          note_on   control_change program_change
Pad Release       note_off  control_change N/A
Velocity Down     0-127     0-127          N/A
Velocity Release  127       0              N/A
================= ========= ============== ==============

All pads can be put into toggle mode. When in toggle mode, you have to press the pad a second time to trigger the release event.

When in Pad mode you can turn on and off the lights of each pad by sending a note_on or note_off midi message with the corresponding note.
The state of the light will be overwritten on the next button press, so you need to resend note_on messages after a button press if you want the button to be permanently lit.


Knobs
-----
Each knob emits a control_change message when it is turned. The value ranges from 0 to 127.
It is possible to change upper and lower value limit, but this comes with a reduction in resolution and is thus not suggested.

.. python-lpd8 documentation master file, created by
   sphinx-quickstart on Fri Mar  2 15:49:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Quickstart
==========

Python-lpd8 works by handling all the midi communication with the lpd8 device for you.
All you have to do is decide which callback you want attached to which pad or knob.
This quickstart will show you how to use python-lpd8 with `mido <https://mido.readthedocs.io/>`_, a MIDI library.
The mido interface is currently the only one that is currently available.


Opening device
--------------

First we need to create a device instance:

.. code-block:: python

   from lpd8mido import LPD8DeviceMido

   lpd8 = LPD8DeviceMido()

Python-lpd8 will fetch the first LPD8 device that isn't yet occupied. If it can't find a free device, it throws an exception.

Attaching Callbacks
-------------------
Callbacks are called with the following signature:

.. code-block:: python

   def callback(programNum: int,
                padNum: int,
                knobNum: int,
                value: int,
                noteon: int,
                noteoff: int,
                cc: int,
                pc: int) -> None:
      pass

`programNum`, `padNum` and `knobNum` refer to the indices of the program and pad/knob of the pad/knob that triggered the callback.

.. note::

   In python-lpd8 all indices are 0-indexed, while LPD8 is 1-indexed. For example: Program 1 has the index 0, pad 7 has the index 6!

`value` refers to either the velocity with which pads were hit or the value a knob has been turned to.

The additional parameters shall not concern us for now.

A simple callback function might look like this:

.. code-block:: python

   def exampleCallback(programNum: int, padNum: int, knobNum: int, value: int, noteon: int, noteoff: int, cc: int, pc: int):
       print("CB program: %s pad: %s knob: %s value: %s" % (programNum, padNum, knobNum, value))

It does nothing more than to print the program index, pad/knob index and value it receives.
To have this callback called everytime we press or release pad 1, we do the following:

.. code-block:: python

   lpd8.addPadCB(0, 0, exampleCallback)
   #lpd8.addKnobCB(0, 0, exampleCallback) # For knobs

If you press and release pad 1 you will see the following printed:

.. code-block:: none

   CB program: 0 pad: 0 knob: None value: 63
   CB program: 0 pad: 0 knob: None value: 127

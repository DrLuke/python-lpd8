.. python-lpd8 documentation master file, created by
   sphinx-quickstart on Fri Mar  2 15:49:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Intro
=====

python-lpd8 is a pythonic abstraction for the Akai LPD8 midi controller.
It allows you to attach callback functions to each pad and knob, making integration into your application extremely easy.

This is a minimal working example:

.. code-block:: python

   from lpd8mido import LPD8DeviceMido

   from time import sleep

   def exampleCallback(programNum: int, padNum: int, knobNum: int, value: int, noteon: int, noteoff: int, cc: int, pc: int):
       print("CB program: %s pad: %s knob: %s value: %s" % (programNum, padNum, knobNum, value))

   lpd8 = LPD8DeviceMido()
   for i in range(8):
       lpd8.addPadCB(0, i, exampleCallback)
       lpd8.addKnobCB(0, i, exampleCallback)

   while(True):
       lpd8.tick()
       sleep(0.01)

While you've activated the first program and are in PAD-mode you should get messages that looks like this every time you hit a pad or turn a knob:

.. code-block:: none

   CB program: 0 pad: 0 knob: None value: 19
   CB program: 0 pad: 1 knob: None value: 4
   CB program: 0 pad: 2 knob: None value: 20
   CB program: 0 pad: 3 knob: None value: 7
   CB program: 0 pad: None knob: 5 value: 37
   CB program: 0 pad: None knob: 5 value: 38
   CB program: 0 pad: None knob: 5 value: 39
   CB program: 0 pad: None knob: 5 value: 40


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   lpd8
   ambiguity
   callbacks
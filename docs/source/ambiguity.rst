.. python-lpd8 documentation master file, created by
   sphinx-quickstart on Fri Mar  2 15:49:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Control Ambiguities
===================
To prevent ambiguities, python-lpd8 checks that each pad and knob has a unique note/control/program associated with it.
If an ambiguity is detected, you are left with a choice: Shall python-lpd8 throw an exception or shall it attemt to fix the problem?

By default python-lpd8 will throw an exception letting you know that there is a problem.
If you want it to be fixed, call the constructor like this:

.. code-block:: python

   lpd8 = LPD8Device(solveAmbiguity=True)

python-lpd8 will then try to fix any ambiguity by increasing the note/control/program until it is unique across the entire device.
Additionally all pad toggles will be set to off and all knob ranges are set to 0-127.

.. warning::

   All programs on the device will be (partially) overwritten by this! Backup your programs before enabling this setting.


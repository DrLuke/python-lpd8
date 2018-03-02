from typing import List

from lpd8 import LPD8Device

import mido
import time

class LPD8DeviceMido(LPD8Device):
    occupiedDevicenames = []

    def getDevice(self):
        portnames = mido.get_ioport_names()

        # Filter for LPD8 devices that aren't yet occupied by class-instances
        portnames = [x for x in portnames if x.startswith("LPD8:LPD8") and x not in type(self).occupiedDevicenames]

        if portnames:
            self.port = mido.open_ioport(portnames[0])
        else:
            raise Exception("No free LPD8 devices left")

    def writeSysex(self, data: List[int]):
        msg = mido.Message("sysex", data=data)
        self.port.send(msg)

    def readMidi(self, waitForProgram: bool = False):
        starttime = time.time()
        timeout = float(waitForProgram)     # Wait one second if waitForProgram is True
        receivedProgram = False
        while 1:
            for msg in self.port.iter_pending():
                # print("RECV: %s" % msg)
                if msg.type == "sysex":
                    receivedProgram = self.parseSysex(msg.data)
                if self.setupComplete:
                    if msg.type == "note_on":
                        self.triggerCallback(msg.note, None, None, None, msg.velocity)
                    elif msg.type == "note_off":
                        self.triggerCallback(None, msg.note, None, None, msg.velocity)
                    elif msg.type == "control_change":
                        self.triggerCallback(None, None, msg.control, None, msg.value)
                    elif msg.type == "program_change":
                        self.triggerCallback(None, None, None, msg.program, None)
            if receivedProgram or time.time() > (starttime + timeout):
                return

    def writeNote(self, note: int, on: bool = True):
        if on:
            msg = mido.Message("note_on", channel=6, note=note)
        else:
            msg = mido.Message("note_off", channel=6, note=note)
        self.port.send(msg)

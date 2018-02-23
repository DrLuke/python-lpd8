from typing import List

import mido

class LPD8Program():
    class Pad():
        def __init__(self, note:int=0, programChange:int=0, controlChange:int=0, toggle:int=0):
            self.note = note                    # type: int
            self.programChange = programChange  # type: int
            self.controlChange = controlChange  # type: int
            self.toggle = toggle                # type: int

        def __str__(self):
            return "LPD8 Pad; Note=%s; progChange=%s; cc=%s; toggle=%s" % (self.note, self.programChange, self.controlChange, self.toggle)

    class Knob():
        def __init__(self, controlChange:int=0, low:int=0, high:int=0):
            self.controlChange = controlChange  # type: int
            self.low = low                      # type: int
            self.high = high                    # type: int

        def __str__(self):
            return "LPD8 Knob; cc=%s; low=%s; high=%s" % (self.controlChange, self.low, self.high)

    def __init__(self):
        self.programIndex = 0
        self.pads = []      # type: List[LPD8Program.Pad]
        self.knobs = []     # type: List[LPD8Program.Knob]
        for i in range(8):
            self.pads.append(LPD8Program.Pad(note=i))
            self.knobs.append(LPD8Program.Knob())

    def readProgram(self, sysexData: List[int]):
        # Reference: https://github.com/charlesfleche/lpd8-editor/blob/d3c312e226f55ab0082b66e4732f5b860dc7b5fb/doc/SYSEX.md
        if not sysexData[0] == 0x47:
            raise Exception("Manufacturerbyte (1) invalid: 0x%X (should be 0x47)" % sysexData[0])
        if not sysexData[1:3] == [0x7F, 0x75]:
            raise Exception("Modelbytes (2:3) invalid: 0x%X 0x%X (should be 0x7F 0x75)" % (sysexData[1], sysexData[2]))
        if not sysexData[3:6] == [0x63, 0x00, 0x3A] and 1 <= sysexData[7] <= 4:
            raise Exception("Commandbytes (3:6) invalid: 0x%X 0x%X 0x%X 0x%X (should be 0x63 0x00 0x3A 0x0X with X=[0..3])" % tuple(sysexData[3:6]))

        self.programIndex = sysexData[6]
        self.pads = []  # type: List[LPD8Program.Pad]
        self.knobs = []  # type: List[LPD8Program.Knob]
        for i in range(8):
            self.pads.append(LPD8Program.Pad(note=sysexData[8 + 4*i],
                                             programChange=sysexData[9 + 4*i],
                                             controlChange=sysexData[10 + 4*i],
                                             toggle=sysexData[11 + 4*i]))
            self.knobs.append(LPD8Program.Knob(controlChange=sysexData[40 + 3*i],
                                               low=sysexData[41 + 3*i],
                                               high=sysexData[42 + 3*i]))

    def writeProgram(self) -> List[int]:
        # Reference: https://github.com/charlesfleche/lpd8-editor/blob/d3c312e226f55ab0082b66e4732f5b860dc7b5fb/doc/SYSEX.md
        data = []
        data += [0x47, 0x7F, 0x75, 0x61, 0x00, 0x3A]

        if not 1 <= self.programIndex <= 4:
            raise Exception("Program index out of range: %s (must be 1-4)" % self.programIndex)
        data += [self.programIndex]

        data += [0x06]  # ???

        if not len(self.pads) == 8:
            raise Exception("Program has too few or too many pads: %s (must be 8)" % len(self.pads))
        for pad in self.pads:
            if not 0 <= pad.note <= 127:
                raise Exception("Note for pad %s out of range: %s (must be 0-127)" % (self.pads.index(pad), pad.note))
            if not 0 <= pad.programChange <= 127:
                raise Exception("Program change for pad %s out of range: %s (must be 0-127)" % (self.pads.index(pad), pad.programChange))
            if not 0 <= pad.controlChange <= 127:
                raise Exception("Control change for pad %s out of range: %s (must be 0-127)" % (self.pads.index(pad), pad.controlChange))
            if not 0 <= pad.toggle <= 1:
                raise Exception("Toggle for pad %s out of range: %s (must be 0-1)" % (self.pads.index(pad), pad.oggle))
            data += [pad.note, pad.programChange, pad.controlChange, pad.toggle]

        if not len(self.knobs) == 8:
            raise Exception("Program has too few or too many knobs: %s (must be 8)" % len(self.knobs))
        for knob in self.knobs:
            if not 0 <= knob.controlChange <= 127:
                raise Exception("Control change for knob %s out of range: %s (must be 0-127)" % (self.knobs.index(knob), knob.controlChange))
            if not 0 <= knob.low <= 127:
                raise Exception("Control change for knob %s out of range: %s (must be 0-127)" % (self.knobs.index(knob), knob.low))
            if not 0 <= knob.high <= 127:
                raise Exception("Control change for knob %s out of range: %s (must be 0-127)" % (self.knobs.index(knob), knob.high))
            data += [knob.controlChange, knob.low, knob.high]

        return data

class LPD8Device():
    pass


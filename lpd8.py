from typing import List, Union, Tuple, Callable
import time

class LPD8Program():
    """LPD8 Program Abstraction
    Implements an LPD8 program which defines which notes and control change signals etc. each pad and knob is emitting.
    The LPD8 can store 4 different programs which can be enabled from the device."""
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
        self.programIndex = 0   # type: int
        self.pads = []      # type: List[LPD8Program.Pad]
        self.knobs = []     # type: List[LPD8Program.Knob]
        for i in range(8):
            self.pads.append(LPD8Program.Pad(note=i))
            self.knobs.append(LPD8Program.Knob())

    def readProgram(self, sysexData: List[int]):
        """Reads sysex program message from LPD8 device"""
        # Reference: https://github.com/charlesfleche/lpd8-editor/blob/d3c312e226f55ab0082b66e4732f5b860dc7b5fb/doc/SYSEX.md
        if not sysexData[0] == 0x47:
            raise Exception("Manufacturerbyte (1) invalid: 0x%X (should be 0x47)" % sysexData[0])
        if not sysexData[1:3] == [0x7F, 0x75]:
            raise Exception("Modelbytes (2:3) invalid: 0x%X 0x%X (should be 0x7F 0x75)" % (sysexData[1], sysexData[2]))
        if not sysexData[3:6] == [0x63, 0x00, 0x3A] and 1 <= sysexData[7] <= 4:
            raise Exception("Commandbytes (3:6) invalid: 0x%X 0x%X 0x%X 0x%X (should be 0x63 0x00 0x3A 0x0X with X=[0..3])" % tuple(sysexData[3:6]))

        self.programIndex = sysexData[6] - 1
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
        """Writes sysex program message for LPD8 device"""
        # Reference: https://github.com/charlesfleche/lpd8-editor/blob/d3c312e226f55ab0082b66e4732f5b860dc7b5fb/doc/SYSEX.md
        data = []
        data += [0x47, 0x7F, 0x75, 0x61, 0x00, 0x3A]

        if not 0 <= self.programIndex <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % self.programIndex)
        data += [self.programIndex + 1]

        data += [0x06]  # Midi channel fixed to 6   # TODO: Make settable?

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
    class CB():
        def __init__(self):
            self.funcs = []

    class PadNoteCB(CB):
        def __init__(self, program: int, pad: int, note:int):
            super(LPD8Device.PadNoteCB, self).__init__()
            self.program = program
            self.pad = pad
            self.note = note

    class PadCCCB(CB):
        def __init__(self, program: int, pad: int, cc: int):
            super(LPD8Device.PadCCCB, self).__init__()
            self.program = program
            self.pad = pad
            self.cc = cc

    class PadPCCB(CB):
        def __init__(self, program: int, pad: int, pc: int):
            super(LPD8Device.PadPCCB, self).__init__()
            self.program = program
            self.pad = pad
            self.pc = pc

    class KnobCCCB(CB):
        def __init__(self, program: int, knob: int, cc: int):
            super(LPD8Device.KnobCCCB, self).__init__()
            self.program = program
            self.knob = knob
            self.cc = cc


    def __init__(self, solveAmbiguity: bool=False):
        self.programs = [None, None, None, None]  # type: List[LPD8Program]
        self.solveAmbiguity = solveAmbiguity

        self.setupComplete = False
        self.lastProgramWrite = time.time()
        self.lastProgramQuery = time.time()
        self.programChangeCB = None
        self.currentProgram = 0

        self.getDevice()
        self.getPrograms()
        self.checkAmbiguity()

        # From this point programs must not be changed
        self.setupComplete = True

        self.cbList = []

    def getDevice(self):
        """Open midi IO to LPD8"""
        raise NotImplementedError

    def getPrograms(self):
        for i in range(4):
            self.writeSysex([0x47, 0x7F, 0x75, 0x63, 0x00, 0x01, 1+i])  # Request program 1 to 4
            self.readMidi(True)    # Wait up to one second for response
            if self.programs[i] is None:    # If response came within one second, program slot will be filled
                raise Exception("Reading Program data timed out")
            for pad in self.programs[i].pads:       # Set toggle to off for all pads
                pad.toggle = False
            for knob in self.programs[i].knobs:     # Set knob range to 0-127
                knob.low = 0
                knob.high = 127

        self.writeSysex(data=[0x47, 0x7F, 0x75, 0x64, 0x00, 0x00])  # Query active program


    def checkAmbiguity(self):
        # Iterate over all settings and make sure they're unique. Otherwise throw exception
        for program in self.programs:
            for pad in program.pads:
                ambiguities = self.findAmbiguity(pad)
                if ambiguities:
                    if self.solveAmbiguity:
                        self.fixAmbiguity(self.programs.index(program), pad)
                    else:
                        raise Exception("Ambiguity between program %s/%s and %s" % (self.programs.index(program), pad, ambiguities))
            for knob in program.knobs:
                ambiguities = self.findAmbiguity(knob)
                if ambiguities:
                    if self.solveAmbiguity:
                        self.fixAmbiguity(self.programs.index(program), knob)
                    else:
                        raise Exception("Ambiguity between program %s/%s and %s" % (self.programs.index(program), knob, ambiguities))


        for program in self.programs:
            self.writeSysex(program.writeProgram())
            time.sleep(0.3)     # If write commands are sent too fast, it won't work :/

        self.setActiveProgram(0)

    def findAmbiguity(self, toCheck: Union[LPD8Program.Pad, LPD8Program.Knob]) -> List[Union[LPD8Program.Pad, LPD8Program.Knob]]:
        ambiguities = []
        for program in self.programs:
            if type(toCheck) is LPD8Program.Pad:
                for pad in program.pads:
                    if toCheck.note == pad.note or toCheck.controlChange == pad.controlChange or toCheck.programChange == pad.programChange:
                        ambiguities.append(pad)
                for knob in program.knobs:
                    if toCheck.controlChange == knob.controlChange:
                        ambiguities.append(knob)
            elif type(toCheck) is LPD8Program.Knob:
                for knob in program.knobs:
                    if toCheck.controlChange == knob.controlChange:
                        ambiguities.append(knob)
                for pad in program.pads:
                    if toCheck.controlChange == pad.controlChange:
                        ambiguities.append(pad)

        if toCheck in ambiguities:
            ambiguities.remove(toCheck)
        return ambiguities

    def fixAmbiguity(self, programIndex: int, toFix: Union[LPD8Program.Pad, LPD8Program.Knob]):
        """Increase pad/knob values until no ambiguity is present."""
        print("fixing ambiguity of: %s (Program %s)" % (toFix, programIndex))
        if type(toFix) is LPD8Program.Pad:
            for i in range(127):    # Fix all note conflicts
                ambiguities = self.findAmbiguity(toFix)
                if not [x for x in [x for x in ambiguities if type(x) is LPD8Program.Pad] if x.note == toFix.note]:
                    break
                toFix.note = (toFix.note + 1) % 128
            else:
                raise Exception("Couldn't fix note ambiguity between program %s/%s and %s" % (programIndex, toFix, ambiguities))

            for i in range(127):    # Fix all controlchange conflicts
                ambiguities = self.findAmbiguity(toFix)
                if not [x for x in ambiguities if x.controlChange == toFix.controlChange]:
                    break
                toFix.controlChange = (toFix.controlChange + 1) % 128
            else:
                raise Exception("Couldn't fix controlChange ambiguity between program %s/%s and %s" % (programIndex, toFix, ambiguities))

            for i in range(127):    # Fix all controlchange conflicts
                ambiguities = self.findAmbiguity(toFix)
                if not [x for x in [x for x in ambiguities if type(x) is LPD8Program.Pad] if x.programChange == toFix.programChange]:
                    break
                toFix.programChange = (toFix.programChange + 1) % 128
            else:
                raise Exception("Couldn't fix programChange ambiguity between program %s/%s and %s" % (programIndex, toFix, ambiguities))

        elif type(toFix) is LPD8Program.Knob:
            for i in range(127):    # Fix all note conflicts
                ambiguities = self.findAmbiguity(toFix)
                if not [x for x in ambiguities if x.controlChange == toFix.controlChange]:
                    break
                toFix.controlChange = (toFix.controlChange + 1) % 128
            else:
                raise Exception("Couldn't fix controlChange ambiguity between program %s/%s and %s" % (programIndex, toFix, ambiguities))

        print("                -> %s" % toFix)

    def triggerCallback(self, noteon: int, noteoff: int, cc: int, pc: int, value: int=None):
        # Callback signature: callback(programNum: int, padNum: int, knobNum: int, value: int, noteon: int, noteoff: int, cc: int, pc: int) -> None
        for cb in self.cbList:
            if type(cb) == LPD8Device.PadNoteCB and noteon is not None and cb.note == noteon:
                for func in cb.funcs:
                    func(cb.program, cb.pad, None, value, noteon, None, None, None)
                return
            elif type(cb) == LPD8Device.PadNoteCB and noteoff is not None and cb.note == noteoff:
                for func in cb.funcs:
                    func(cb.program, cb.pad, None, value, None, noteoff, None, None)
                return
            elif type(cb) == LPD8Device.PadPCCB and pc is not None and cb.pc == pc:
                for func in cb.funcs:
                    func(cb.program, cb.pad, None, None, None, None, None, pc)
                return
            elif type(cb) == LPD8Device.KnobCCCB and cc is not None and cb.cc == cc:
                for func in cb.funcs:
                    func(cb.program, None, cb.knob, value, None, None, cc, None)
                return

    def tick(self, queryInterval: float=0.1) -> None:
        self.readMidi()

        if time.time() > self.lastProgramQuery + queryInterval:
            self.writeSysex(data=[0x47, 0x7F, 0x75, 0x64, 0x00, 0x00])  # Query current program
            self.lastProgramQuery = time.time()

    def writeProgram(self, data: List[int]):
        """If programs are written too quickly, they won't be saved. Thanks Akai!"""
        while self.lastProgramWrite + 0.3 < time.time():
            pass
        self.writeSysex(data)
        self.lastProgramWrite = time.time()

    def lightPad(self, pad:int, on:bool =True):
        if not 0 <= pad <= 7:
            raise("Pad out of range: %s (must be 0-7)" % pad)
        curProg = self.programs[self.currentProgram]
        pad = curProg.pads[pad]

        self.writeNote(pad.note, on)

    def addPadCB(self, programNum: int, padNum: int, CB: Callable[[int, int, int, int, int], None], note: bool=True, cc: bool=False, pc: bool=False):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        if not 0 <= padNum <= 7:
            raise("Pad out of range: %s (must be 0-7)" % padNum)

        pad = self.programs[programNum].pads[padNum]

        if note:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadNoteCB and cb.note == pad.note:
                    if CB not in cb.funcs:
                        cb.funcs.append(CB)
                    break
            else:
                newCB = LPD8Device.PadNoteCB(programNum, padNum, pad.note)
                newCB.funcs.append(CB)
                self.cbList.append(newCB)

        if cc:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadCCCB and cb.cc == pad.controlChange:
                    if CB not in cb.funcs:
                        cb.funcs.append(CB)
                    break
            else:
                newCB = LPD8Device.PadCCCB(programNum, padNum, pad.controlChange)
                newCB.funcs.append(CB)
                self.cbList.append(newCB)

        if pc:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadPCCB and cb.pc == pad.programChange:
                    if CB not in cb.funcs:
                        cb.funcs.append(CB)
                    break
            else:
                newCB = LPD8Device.PadPCCB(programNum, padNum, pad.controlChange)
                newCB.funcs.append(CB)
                self.cbList.append(newCB)

    def removePadCB(self, programNum: int, padNum: int, CB: Callable[[int, int, int, int, int], None], note: bool=True, cc: bool=False, pc: bool=False):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        if not 0 <= padNum <= 7:
            raise("Pad out of range: %s (must be 0-7)" % padNum)

        pad = self.programs[programNum].pads[padNum]

        if note:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadNoteCB and cb.note == pad.note:
                    if CB in cb.funcs:
                        cb.funcs.remove(CB)

        if cc:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadCCCB and cb.cc == pad.controlChange:
                    if CB in cb.funcs:
                        cb.funcs.remove(CB)

        if pc:
            for cb in self.cbList:
                if type(cb) == LPD8Device.PadPCCB and cb.pc == pad.programChange:
                    if CB in cb.funcs:
                        cb.funcs.remove(CB)

    def addKnobCB(self, programNum: int, knobNum: int, CB: Callable[[int, int, int, int, int], None]):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        if not 0 <= knobNum <= 7:
            raise("Pad out of range: %s (must be 0-7)" % knobNum)

        knob = self.programs[programNum].knobs[knobNum]
        for cb in self.cbList:
            if type(cb) == LPD8Device.KnobCCCB and cb.cc == knob.controlChange:
                if CB not in cb.funcs:
                    cb.funcs.append(CB)
                    break
            else:
                newCB = LPD8Device.KnobCCCB(programNum, knobNum, knob.controlChange)
                newCB.funcs.append(CB)
                self.cbList.append(newCB)

    def removeKnobCB(self, programNum: int, knobNum: int, CB: Callable[[int, int, int, int, int], None]):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        if not 0 <= knobNum <= 7:
            raise("Pad out of range: %s (must be 0-7)" % knobNum)

        knob = self.programs[programNum].knobs[knobNum]
        for cb in self.cbList:
            if type(cb) == LPD8Device.KnobCCCB and cb.cc == knob.controlChange:
                if CB in cb.funcs:
                    cb.funcs.remove(CB)

    def setPadToggle(self, programNum: int, padNum: int, toggle: bool=False):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        if not 0 <= padNum <= 7:
            raise("Pad out of range: %s (must be 0-7)" % padNum)

        program = self.programs[programNum]
        pad = program.pads[padNum]
        pad.toggle = toggle
        self.writeSysex(program.writeProgram())

    def setActiveProgram(self, programNum: int):
        if not 0 <= programNum <= 3:
            raise Exception("Program index out of range: %s (must be 0-3)" % programNum)
        self.writeSysex(data=[0x47, 0x7F, 0x75, 0x62, 0x00, 0x00, 0x01, programNum])

    def writeSysex(self, data: List[int]):
        raise NotImplementedError

    def writeNote(self, note: int, on: bool=True):
        raise NotImplementedError

    def readMidi(self, waitForProgram: bool=False):
        raise NotImplementedError

    def parseSysex(self, data: Tuple[int, ...]) -> bool:
        """Parse an incoming sysex message
        data is the raw sysex data without the start and stop bytes
        Returns true if a program was received"""
        try:
            # Try to parse message as lpd8-program
            newProgram = LPD8Program()
            newProgram.readProgram(list(data))
            self.programs[newProgram.programIndex] = newProgram
            return True
        except:
            pass

        if data[:-1] == (0x47, 0x7F, 0x75, 0x64, 0x00, 0x01):
            newprog = data[6] - 1   # return value is 1-indexed
            if not newprog == self.currentProgram and callable(self.programChangeCB):
                self.programChangeCB(newprog)
            self.currentProgram = newprog
            return False

        return False
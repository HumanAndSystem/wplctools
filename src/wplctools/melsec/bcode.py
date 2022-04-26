from io import SEEK_CUR, BytesIO
import struct
from functools import lru_cache

from ..utils import to_zerohex
from .device import DEV, DeviceLexer


__all__ = [
    "Instruction",
    "decode",
    "encode",
]


class Instruction:
    __slots__ = ("opcode", "step", "mnemonic", "operands")

    def __init__(self, mnemonic=None, operands=None, step=None):
        if operands is None:
            operands = []
        if step is None:
            step = len(operands) or 1
        self.mnemonic = mnemonic
        self.operands = operands
        self.step = step

    def __str__(self):
        if self.operands:
            try:
                operands = " ".join([str(operand) for operand in self.operands])
            except:
                print(self.operands)
                breakpoint()
                print()
            return f"{self.mnemonic} {operands}"
        return f"{self.mnemonic}"


def _statement(code, *, encoding, **kwds):
    step = code[2]
    star = "*" if step == 1 else ""
    statement = code[3:-1].decode(encoding)
    return Instruction(mnemonic=f";{star}{statement}", step=step)


def _note(code, *, encoding, **kwds):
    step = code[2]
    star = "*" if step == 1 else ""
    note = code[3:-1].decode(encoding)
    return Instruction(mnemonic=f"<{star}{note}", step=step)


def _extension(code, target):
    return Instruction()
    # if main in (0x70, 0x71, 0x72, 0x73):
    #     # print(code)
    #     # print(main, step, sub, flag)
    
    # command = code[5:-1].decode("latin1")

    #     args = []
    #     if main in (0x72, 0x73):
    #         module = self.read_device()
    #         args = [module]
    #     for i in range(sub):
    #         args.append(self.read_device())
    #     args = " ".join(args)
    #     if main == 0x70:  # S.
    #         instruction.mnemonic = f"S{P}.{command}"
    #         return instruction
    #         return f"S{P}.{command} {args}"
    #     elif main == 0x71:  # Z.
    #         instruction.mnemonic = f"Z{P}.{command}"
    #         return instruction
    #         return f"Z{P}.{command} {args}"
    #     elif main == 0x72:  # G.
    #         instruction.mnemonic = f"G{P}.{command}"
    #         return instruction
    #         return f"G{P}.{command} {args}"
    #     elif main == 0x73:  # J.
    #         instruction.mnemonic = f"J{P}.{command}"
    #         return instruction
    #         return f"J{P}.{command} {args}"
    # return code


def _extension_s(code):
    return _extension(code, "S")


def _extension_z(code):
    return _extension(code, "Z")


def _extension_g(code):
    return _extension(code, "G")


def _extension_j(code):
    return _extension(code, "J")


"""
Relevant CPU module
CPU module                  Model
Basic model                 QCPU Q00JCPU, Q00CPU, Q01CPU
High Performance model      QCPU Q02CPU, Q02HCPU, Q06HCPU, Q12HCPU, Q25HCPU
Process CPU                 Q02PHCPU, Q06PHCPU, Q12PHCPU, Q25PHCPU
Redundant CPU               Q12PRHCPU, Q25PRHCPU
Universal model             QCPU Q00UJCPU, Q00UCPU, Q01UCPU, Q02UCPU, Q03UDCPU, Q03UDVCPU, Q03UDECPU,
                            Q04UDHCPU, Q04UDVCPU, Q04UDPVCPU, Q04UDEHCPU, Q06UDHCPU, Q06UDVCPU,
                            Q06UDPVCPU, Q06UDEHCPU, Q10UDHCPU, Q10UDEHCPU, Q13UDHCPU, Q13UDVCPU,
                            Q13UDPVCPU, Q13UDEHCPU, Q20UDHCPU, Q20UDEHCPU, Q26UDHCPU, Q26UDVCPU,
                            Q26UDPVCPU, Q26UDEHCPU, Q50UDEHCPU, Q100UDEHCPU
LCPU                        L02SCPU, L02SCPU-P, L02CPU, L02CPU-P, L06CPU, L06CPU-P, L26CPU, L26CPU-P, L26CPU-BT,
                            L26CPU-PBT
"""


class InstructionError(Exception):
    pass


_instruction_code_to_mnemonic_table = {
    # 5 SEQUENCE INSTRUCTIONS
    # 5.1 Contact Instructions
    0x00: { None: ("LD", 1) },
    0x01: { None: ("LDI", 1) },
    0x02: { None: ("LDP", 1) },
    0x03: { None: ("LDF", 1) },
    0x04: { None: ("LDPI", 1) },
    0x05: { None: ("LDFI", 1) },
    0x06: { None: ("OR", 1) },
    0x07: { None: ("ORI", 1) },
    0x08: { None: ("ORP", 1) },
    0x09: { None: ("ORF", 1) },
    0x0a: { None: ("ORPI", 1) },
    0x0b: { None: ("ORFI", 1) },
    0x0c: { None: ("AND", 1) },
    0x0d: { None: ("ANI", 1) },
    0x0e: { None: ("ANDP", 1) },
    0x0f: { None: ("ANDF", 1) },
    # 5.2 Association Instructions
    0x10: { None: ("EGP", 1) },
    0x11: { None: ("EGF", 1) },
    0x12: { None: ("MEP", 0) },
    0x13: { None: ("MEF", 0) },
    0x14: { None: ("INV", 0) },
    # 5.1 Contact Instructions
    0x15: { None: ("ANDPI", 1) },
    0x16: { None: ("ANDFI", 1) },
    # 5.2 Association Instructions
    0x18: { None: ("ORB", 0) },
    0x19: { None: ("ANB", 0) },
    0x1a: { None: ("MPS", 0) },
    0x1b: { None: ("MRD", 0) },
    0x1c: { None: ("MPP", 0) },
    # 5.3 Output Instructions
    0x20: { None: ("OUT", 1) },
    0x21: { None: ("OUT", 2) },
    0x22: { None: ("OUTH", 2) },
    0x23: { None: ("SET", 1) },
    0x24: { None: ("RST", 1) },
    0x25: { None: ("PLS", 1) },
    0x26: { None: ("PLF", 1) },
    0x27: { None: ("FF", 1) },
    0x28: { None: ("DELTA", 1) },
    # 5.4 Shift Instructions
    0x2a: { None: ("SFT", 1) },
    # 5.6 Termination Instructions
    0x33: { None: ("FEND", 0) },
    0x34: { None: ("END", 0) },
    # 5.7 Other Instructions
    0x2d: { None: ("STOP", 0) },
    0x32: { None: ("PAGE", 1) },
    0x38: { None: ("NOPLF", 0) },
    #
    0x3c: { None: ("LABEL", 1) },

    # 6 BASIC INSTRUCTIONS
    # 6.1 Comparison Operation Instructions
    0x40: {
        0x00: ("=", 2),
        0x01: ("<>", 2),
        0x02: ("<", 2),
        0x03: ("<=", 2),
        0x04: (">", 2),
        0x05: (">=", 2),
        0x06: ("D=", 2),
        0x07: ("D<>", 2),
        0x08: ("D<", 2),
        0x09: ("D<=", 2),
        0x0a: ("D>", 2),
        0x0b: ("D>=", 2),
        0x0c: ("E=", 2),
        0x0d: ("E<>", 2),
        0x0e: ("E<", 2),
        0x0f: ("E<=", 2),
        0x10: ("E>", 2),
        0x11: ("E>=", 2),
        0x12: ("$=", 2),
        0x13: ("$<>", 2),
        0x14: ("$<", 2),
        0x15: ("$<=", 2),
        0x16: ("$>", 2),
        0x17: ("$>=", 2),
        0x18: ("ED=", 2),
        0x19: ("ED<>", 2),
        0x1a: ("ED<", 2),
        0x1b: ("ED<=", 2),
        0x1c: ("ED>", 2),
        0x1d: ("ED>=", 2),
        0x1e: ("DT=", 3),
        0x1f: ("DT<>", 3),
        0x20: ("DT<", 3),
        0x21: ("DT<=", 3),
        0x22: ("DT>", 3),
        0x23: ("DT>=", 3),
        0x24: ("TM=", 3),
        0x25: ("TM<>", 3),
        0x26: ("TM<", 3),
        0x27: ("TM<=", 3),
        0x28: ("TM>", 3),
        0x29: ("TM>=", 3),
    },
    0x41: {
        0x00: ("PCHK", 1),
    },
    0x48: {
        0x00: ("BKCMP=", 4),
        0x01: ("BKCMP<>", 4),
        0x02: ("BKCMP<", 4),
        0x03: ("BKCMP<=", 4),
        0x04: ("BKCMP>", 4),
        0x05: ("BKCMP>=", 4),
        0x06: ("CMP", 3),
        0x07: ("DCMP", 3),
        0x08: ("ZCP", 4),
        0x09: ("DZCP", 4),
        # 0x0a:
        # 0x0b:
        0x0c: ("DBKCMP=", 4),
        0x0d: ("DBKCMP<>", 4),
        0x0e: ("DBKCMP<", 4),
        0x0f: ("DBKCMP<=", 4),
        0x10: ("DBKCMP>", 4),
        0x11: ("DBKCMP>=", 4),
        0x12: ("ECMP", 3),
        0x13: ("EDCMP", 3),
        0x14: ("EZCP", 4),
        0x15: ("EDZCP", 4),
    },
    # 6.2 Arithmetic Operation Instructions
    0x49: {
        0x00: ("+", 2),
        0x01: ("+", 3),
        0x02: ("-", 2),
        0x03: ("-", 3),
        0x04: ("D+", 2),
        0x05: ("D+", 3),
        0x06: ("D-", 2),
        0x07: ("D-", 3),
        0x08: ("*", 3),
        # 0x09:
        0x0a: ("/", 3),
        # 0x0b:
        0x0c: ("D*", 3),
        # 0x0d:
        0x0e: ("D/", 3),
        # 0x0f:
        0x10: ("B+", 2),
        0x11: ("B+", 3),
        0x12: ("B-", 2),
        0x13: ("B-", 3),
        0x14: ("DB+", 2),
        0x15: ("DB+", 3),
        0x16: ("DB-", 2),
        0x17: ("DB-", 3),
        0x18: ("B*", 3),
        0x19: ("B/", 3),
        0x1a: ("DB*", 3),
        0x1b: ("DB/", 3),
        0x1c: ("E+", 2),
        0x1d: ("E+", 3),
        0x1e: ("E-", 2),
        0x1f: ("E-", 3),
        0x20: ("E*", 3),
        0x21: ("E/", 3),
        0x22: ("$+", 2),
        0x23: ("$+", 3),
        # 0x24:
        # 0x25:
        0x26: ("BK+", 4),
        0x27: ("BK-", 4),
        # 0x28:
        # ...
        # 0x33:
        0x34: ("DBK+", 4),
        0x35: ("DBK-", 4),
        0x36: ("ED+", 2),
        0x37: ("ED+", 3),
        0x38: ("ED-", 2),
        0x39: ("ED-", 3),
        0x3a: ("ED*", 3),
        0x3b: ("ED/", 3),
    },
    0x4a: {
        0x00: ("INC", 1),
        0x01: ("DINC", 1),
        0x02: ("DEC", 1),
        0x03: ("DDEC", 1),
    },
    # 6.3 Data Conversion Instructions
    0x4b: {
        0x00: ("BCD", 2),
        0x01: ("DBCD", 2),
        0x02: ("BIN", 2),
        0x03: ("DBIN", 2),
        0x04: ("INT", 2),
        0x05: ("DINT", 2),
        0x06: ("FLT", 2),
        0x07: ("DFLT", 2),
        0x08: ("DBL", 2),
        0x09: ("WORD", 2),
        0x0a: ("GRY", 2),
        0x0b: ("DGRY", 2),
        0x0c: ("GBIN", 2),
        0x0d: ("DGBIN", 2),
        0x0e: ("NEG", 1),
        0x0f: ("DNEG", 1),
        0x10: ("ENEG", 1),
        0x11: ("BKBCD", 3),
        0x12: ("BKBIN", 3),

        0x16: ("FLTD", 2),
        0x17: ("DFLTD", 2),
        0x18: ("INTD", 2),
        0x19: ("DINTD", 2),
        0x1a: ("EDNEG", 1),
        0x1b: ("ECON", 2),
        0x1c: ("EDCON", 2),
    },
    # 6.4 Data Transfer Instructions
    0x4c: {
        0x00: ("MOV", 2),
        0x01: ("DMOV", 2),
        0x02: ("EMOV", 2),
        0x03: ("$MOV", 2),
        0x04: ("CML", 2),
        0x05: ("DCML", 2),
        0x06: ("BMOV", 3),
        0x07: ("FMOV", 3),
        0x08: ("XCH", 2),
        0x09: ("DXCH", 2),
        0x0a: ("BXCH", 3),
        0x0b: ("SWAP", 1),
        0x0e: ("DFMOV", 3),
        0x10: ("EDMOV", 2),
    },
    # 6.5 Program Branch Instructions
    0x4d: {
        0x00: ("CJ", 1),
        0x01: ("SCJ", 1),
        0x06: ("GOEND", 0),
    },
    # 6.6 Program Execution Control Instructions
    # 6.7 I/O Refresh Instructions
    0x4e: {
        0x00: ("RFS", 2),
    },
    # 6.8 Other Convenient Instructions

    # 7 APPLICATION INSTRUCTIONS
    # 7.1 Logical Operation Instructions
    0x4f: {
        0x00: ("WAND", 2),
        0x01: ("WAND", 3),
        0x02: ("WOR", 2),
        0x03: ("WOR", 3),
        0x04: ("WXOR", 2),
        0x05: ("WXOR", 3),
        0x06: ("WXNR", 2),
        0x07: ("WXNR", 3),
        0x08: ("DAND", 2),
        0x09: ("DAND", 3),
        0x0a: ("DOR", 2),
        0x0b: ("DOR", 3),
        0x0c: ("DXOR", 2),
        0x0d: ("DXOR", 3),
        0x0e: ("DXNR", 2),
        0x0f: ("DXNR", 3),
        0x10: ("BKAND", 4),
        0x11: ("BKOR", 4),
        0x12: ("BKXOR", 4),
        0x13: ("BKXNR", 4),
    },
    # 7.2 Rotation Instructions
    0x50: {
        0x00: ("ROR", 2),
        0x01: ("RCR", 2),
        0x02: ("ROL", 2),
        0x03: ("RCL", 2),
        0x04: ("DROR", 2),
        0x05: ("DRCR", 2),
        0x06: ("DROL", 2),
        0x07: ("DRCL", 2),
    },
    # 7.3 Shift Instructions
    0x51: {
        0x00: ("SFR", 2),
        0x01: ("SFL", 2),
        0x02: ("BSFR", 2),
        0x03: ("BSFL", 2),
        0x04: ("DSFR", 2),
        0x05: ("DSFL", 2),
        0x0c: ("SFTBR", 3),
        0x0d: ("SFTBL", 3),
        0x0e: ("SFTWR", 3),
        0x0f: ("SFTWL", 3),
    },
    # 7.4 Bit Processing Instructions
    0x52: {
        0x00: ("BSET", 2),
        0x01: ("BRST", 2),
        0x02: ("TEST", 3),
        0x03: ("DTEST", 3),
        0x04: ("BKRST", 2),
    },
    # 7.5 Data Processing Instructions
    0x53: {
        0x02: ("SUM", 2),
        0x03: ("DSUM", 2),
        0x04: ("DECO", 3),
        0x05: ("ENCO", 3),
        0x0b: ("WTOB", 3),
        0x0c: ("BTOW", 3),
        0x13: ("WSUM", 3),
        0x14: ("DWSUM", 3),
    },
    # 7.6 Structure Creation Instructions
    0x54: {
        0x00: ("BREAK", 2),
        0x01: ("CALL", 1),
        0x02: ("CALL", 1+1),
        0x03: ("CALL", 1+2),
        0x04: ("CALL", 1+3),
        0x05: ("CALL", 1+4),
        0x06: ("CALL", 1+5),
        0x07: ("FCALL", 1),
        0x08: ("FCALL", 1+1),
        0x09: ("FCALL", 1+2),
        0x0a: ("FCALL", 1+3),
        0x0b: ("FCALL", 1+4),
        0x0c: ("FCALL", 1+5),
        0x0d: ("ECALL", 2),
        0x0e: ("ECALL", 2+1),
        0x0f: ("ECALL", 2+2),
        0x10: ("ECALL", 2+3),
        0x11: ("ECALL", 2+4),
        0x12: ("ECALL", 2+5),
        0x13: ("EFCALL", 2),
        0x14: ("EFCALL", 2+1),
        0x15: ("EFCALL", 2+2),
        0x16: ("EFCALL", 2+3),
        0x17: ("EFCALL", 2+4),
        0x18: ("EFCALL", 2+5),
        # 0x19:
        0x1a: ("XCALL", 1),
        0x1b: ("XCALL", 1+1),
        0x1c: ("XCALL", 1+2),
        0x1d: ("XCALL", 1+3),
        0x1e: ("XCALL", 1+4),
        0x1f: ("XCALL", 1+5),
        #
        0x24: ("CCOM", 0),
    },
    # 7.7 Data Table Operation Instructions
    0x55: {
        0x00: ("FIFW", 2),
        0x01: ("FIFR", 2),
        0x02: ("FPOP", 2),
        0x03: ("FINS", 3),
        0x04: ("FDEL", 3),
    },
    # 7.8 Buffer Memory Access Instructions
    0x56: {
        0x00: ("FROM", 4),
        0x01: ("DFRO", 4),
        0x02: ("TO", 4),
        0x03: ("DTO", 4),
    },
    # 7.9 Display Instructions
    0x57: {
        0x00: ("PR", 2),
        0x01: ("PRC", 2),
        0x04: ("LEDR", 0),
    },
    # 7.10 Debugging and Failure Diagnosis Instructions
    0x58: {
        0x00: ("CHKST", 0),
        0x01: ("CHK", 0),
        0x02: ("CHKCIR", 0),
        0x03: ("CHKEND", 0),
    },
    # 7.11 Character String Processing Instructions
    0x59: {
        0x00: ("BINDA", 2),
        0x01: ("DBINDA", 2),
        0x02: ("BINHA", 2),
        0x03: ("DBINHA", 2),
        0x04: ("BCDDA", 2),
        0x05: ("DBCDDA", 2),
        0x06: ("DABIN", 2),
        0x07: ("DDABIN", 2),
        0x08: ("HABIN", 2),
        0x09: ("DHABIN", 2),
        0x0a: ("DABCD", 2),
        0x0b: ("DDABCD", 2),
        0x0c: ("COMRD", 2),
        0x0d: ("LEN", 2),
        0x0e: ("STR", 3),
        0x0f: ("DSTR", 3),
        0x10: ("VAL", 3),
        0x11: ("DVAL", 3),
        0x12: ("ESTR", 3),
        0x13: ("EVAL", 2),
        0x14: ("ASC", 3),
        0x15: ("HEX", 3),
        0x16: ("RIGHT", 3),
        0x17: ("LEFT", 3),
        0x18: ("MIDR", 3),
        0x19: ("MIDW", 3),
        0x1a: ("INSTR", 4),
        0x24: ("STRINS", 3),
        0x25: ("STRDEL", 3),
    },
    # 7.12 Special Function Instructions
    0x5a: {
        0x00: ("SIN", 2),
        0x01: ("COS", 2),
        0x02: ("TAN", 2),
        0x03: ("ASIN", 2),
        0x04: ("ACOS", 2),
        0x05: ("ATAN", 2),
        0x06: ("RAD", 2),
        0x07: ("DEG", 2),
        0x08: ("SQR", 2),
        0x09: ("EXP", 2),
        0x0a: ("LOG", 2),
        0x0b: ("RND", 1),
        0x0c: ("SRND", 1),
        0x0d: ("BSQR", 2),
        0x0e: ("BDSQR", 2),
        0x0f: ("BSIN", 2),
        0x10: ("BCOS", 2),
        0x11: ("BTAN", 2),
        0x12: ("BASIN", 2),
        0x13: ("BACOS", 2),
        0x14: ("BATAN", 2),
        #
        0x22: ("SIND", 2),
        0x23: ("COSD", 2),
        0x24: ("TAND", 2),
        0x25: ("ASIND", 2),
        0x26: ("ACOSD", 2),
        0x27: ("ATAND", 2),
        0x28: ("RADD", 2),
        0x29: ("DEGD", 2),
        0x2a: ("SQRD", 2),
        0x2b: ("EXPD", 2),
        0x2c: ("LOGD", 2),
        0x2d: ("POW", 3),
        0x2e: ("POWD", 3),
        0x2f: ("LOG10", 2),
        0x30: ("LOG10D", 2),
    },
    # 7.13 Data Control Instructions
    0x5b: {
        0x00: ("LIMIT", 4),
        0x01: ("DLIMIT", 4),
        0x02: ("BAND", 4),
        0x03: ("DBAND", 4),
        0x04: ("ZONE", 4),
        0x05: ("DZONE", 4),
    },
    # 7.14 File Register Switching Instructions
    0x5c: {},
    # 7.15 Clock Instructions
    0x5d: {
        0x00: ("DATERD", 1),
        0x01: ("DATEWR", 1),
        0x02: ("DATE+", 3),
        0x03: ("DATE-", 3),
        0x04: ("SECOND", 2),
        0x05: ("HOUR", 2),
        0x06: ("TCMP", 5),
        0x07: ("TZCP", 4),
        0x12: ("HOURM", 3),
        0x13: ("DHOURM", 3),
        0x14: ("DATE2SEC", 2),
        0x15: ("SEC2DATE", 2),
    },
    # 7.16 Expansion Clock Instructions
    # 7.18 PID Instruction
    0x5e: {
        0x07: ("PID", 4),
    },
    # 7.17 Program Control Instructions
    0x60: {
        0x00: ("PSTOP", 1),
        0x01: ("POFF", 1),
        0x02: ("PSCAN", 1),
        0x03: ("PLOW", 1),
    },
    # 7.18 PID Instruction
    # 7.19 Other Instructions
    0x61: {
        0x00: ("WDT", 0),
        0x04: ("ADRSET", 2),
        0x0a: ("ZPUSH", 1),
        0x0b: ("ZPOP", 1),
    },
    # 7.13 Data Control Instructions
    0x63:{
        0x24: ("SCL", 3),
        0x25: ("DSCL", 3),
        0x2a: ("SCL2", 3),
        0x2b: ("DSCL2", 3),
    },
    # 6.5 Program Branch Instructions
    0x68: {
        0x00: ("JMP", 1),
    },
    # 6.6 Program Execution Control Instructions
    0x69: {
        0x00: ("DI", 0),
        0x01: ("EI", 0),
        0x02: ("IMASK", 1),
        0x03: ("IRET", 0),
    },
    # 7.6 Structure Creation Instructions
    0x6a: {
        0x00: ("FOR", 1),
        0x01: ("NEXT", 0),
        0x02: ("RET", 0),
        0x06: ("COM", 0),
    },

    # extension
    0x70: _extension_s,
    0x71: _extension_z,
    0x72: _extension_g,
    0x73: _extension_j,

    # statement
    0x80: _statement,
    0x82: _note,
}


_instruction_mnemonic_to_code_table = {}
class InstructionCodeTable(dict):
    def __init__(self):
        for main_code, sub_table in _instruction_code_to_mnemonic_table.items():
            for sub_code, (mnemonic, operand_count) in sub_table:
                if mnemonic not in self:
                    self[mnemonic] = {}
                self[mnemonic][operand_count] = (main_code, sub_code)

    def _get_code(self, mnemonic, operand_count):
        if mnemonic in self:
            count_table = self[mnemonic]
            if operand_count in count_table:
                return count_table[operand_count]
        return None

    @lru_cache
    def get_code(self, mnemonic, operand_count):
        code = self._get_code(mnemonic, operand_count)
        if code is not None:
            main, sub = code
            if sub is None:
                return [main]
            return [main, sub]
        if mnemonic.endswith("P"):
            code = self._get_code(mnemonic[:-1], operand_count)
            if code is not None:
                return [main, sub, 0x02]
        if mnemonic.startswith("LD"):
            code = self._get_code(mnemonic[2:], operand_count)
            if code is not None:
                return [main, sub, 0x10]
        elif mnemonic.startswith("AND"):
            code = self._get_code(mnemonic[3:], operand_count)
            if code is not None:
                return [main, sub, 0x11]
        elif mnemonic.startswith("OR"):
            code = self._get_code(mnemonic[2:], operand_count)
            if code is not None:
                return [main, sub, 0x12]
        raise InstructionError()
 
_instruction_mnemonic_to_code_table = InstructionCodeTable()
del InstructionCodeTable


_device_code_to_name_table = {
    # 0x2c: ("RD", 10),
    # 0x50: ("LTC", 10),
    # 0x51: ("LTS", 10),
    # 0x52: ("LTN", 10),
    # 0x54: ("LCC", 10),
    # 0x55: ("LCS", 10),
    # 0x56: ("LCN", 10),
    # 0x58: ("LSTC", 10),
    # 0x59: ("LSTS", 10),
    # 0x5a: ("LSTN", 10),
    # 0x62: ("LZ", 10),
    0x90: ("M", 10),
    0x91: ("SM", 10),
    0x92: ("L", 10),
    0x93: ("F", 10),
    0x94: ("V", 10),
    0x9c: ("X", 16),
    0x9d: ("Y", 16),
    0x9e: ("FX", 16),
    0x9f: ("FY", 16),
    0xa0: ("B", 16),
    0xa1: ("SB", 16),
    0xa2: ("DX", 16),
    0xa3: ("DY", 16),
    0xa8: ("D", 10),
    0xa9: ("SD", 10),
    0xaa: ("FD", 10),
    0xab: ("G", 10),
    0xaf: ("R", 10),
    0xb0: ("ZR", 16),
    0xb4: ("W", 16),
    0xb5: ("SW", 16),
    # 0xc0: ("TC", 10),
    # 0xc1: ("TS", 10),
    # 0xc2: ("TN", 10),
    0xc2: ("T", 10),
    # 0xc3: ("CC", 10),
    # 0xc4: ("CS", 10),
    # 0xc5: ("CN", 10),
    0xc5: ("C", 10),
    # 0xc6: ("STC", 10),
    # 0xc7: ("STS", 10),
    # 0xc8: ("STN", 10),
    0xc8: ("ST", 10),
    0xcc: ("Z", 10),
    0xd0: ("P", 10),
    0xd1: ("I", 10),
    0xd8: ("U", 16),
    0xd9: ("J", 10),
    0xe3: ("E", 10, "ED"),  # double
    0xe8: ("K", 10),
    0xe9: ("K", 10, "KD"),  # long
    0xea: ("H", 16),
    0xeb: ("H", 16, "HD"),  # long
    0xec: ("E", 10),  # float
    0xee: ('"', 10),  # string
    0xf0: ("Z", 10, "-Z"),  # index
    0xf1: ("K", 10, "K-"),  # digit
    0xf2: (".", 10),  # bit
    0xf3: ("@", 10),
    0xf8: ("U", 16),
    0xf9: ("J", 10),
}


class DeviceCodeTable(dict):
    def __init__(self):
        for code, (name, base, *aux) in _device_code_to_name_table.items():
            if aux:
                name = aux[0]
            if code in self:
                raise KeyError(f"duplicate name: {name}")
                # codes = self[name]
                # if not isinstance(codes, list):
                #     codes = [codes]
                #     self[name] = codes
                # codes.append(code)
            else:
                self[name] = code
_device_name_to_code_table = DeviceCodeTable()
del DeviceCodeTable


def _read_code(bs):
    data = bs.read(1)
    if data:
        size = ord(data)
        bs.seek(-1, SEEK_CUR)
        return size, bs.read(size)
    return 0, b""


def _read_address(code):
    return int.from_bytes(code[2:-1], "little")


def _read_device(code):
    name, base, *aux = _device_code_to_name_table.get(code[1], (None, None))
    if name is None:
        raise InstructionError(f"unknown device: {code}")
    address = _read_address(code)
    if base == 16:
        address = to_zerohex(address)
    return f"{name}{address}"


def _read_float(code, fmt="f", *, unpack=struct.unpack):
    size = (4 if fmt == "f" else 8)
    assert code[0] == size + 3
    return unpack(fmt, code[2:2+size])[0]


def _read_with_sep(bs, dev1):
    dev2 = _decode_device(bs)
    return f"{dev1}\\{dev2}"


def _decode_device(bs, *, encoding="mbcs"):
    size, code = _read_code(bs)
    match code[1]:
        case 0xf0:
            # indexing
            z = _read_address(code)
            size, code = _read_code(bs)
            dev = _read_device(code)
            dev = f"{dev}Z{z}"
            if code[1] in (0xf8, 0xf9):
                return _read_with_sep(bs, dev)
            return dev
        case 0xf1:
            # digit designation
            k = _read_address(code)
            dev = _decode_device(bs)
            return f"K{k}{dev}"
        case 0xf2:
            #  bit designation
            bit = _read_address(code)
            word = _decode_device(bs)
            return f"{word}.{bit:X}"
        case 0xf3:
            # indirect specification
            dev = _decode_device(bs)
            return f"@{dev}"
        case 0xf8:
            # Intelligent function module device
            u = _read_device(code)
            return _read_with_sep(bs, u)
        case 0xf9:
            # Link direct device
            j = _read_device(code)
            return _read_with_sep(bs, j)
        case 0xe3:
            # double
            value = _read_float(code, "d")
            return f"E{value}"
        case 0xec:
            # float
            value = _read_float(code, "f")
            return f"E{value}"
        case 0xee:
            # string
            b = 2
            e = b + size - 3
            value = code[b:e].decode(encoding)
            return f'"{value}"'
        case _:
            return _read_device(code)


def decode(bs, *, encoding="mbcs", read_code=_read_code, decode_device=_decode_device):
    # IL binary code format
    # 2 2 - only one, NOP
    # 3 main 3
    # 4 main step 4
    # 5 main step sub 5
    # 6 main step sub flag 6

    size, code = read_code(bs)
    if size == 0:
        raise EOFError()
    if size < 2 or code[0] != code[-1]:
        raise InstructionError()

    if size == 2:
        return Instruction("NOP", [], 1)

    info = _instruction_code_to_mnemonic_table.get(code[1], None)
    if info is None:
        raise InstructionError(f"unknown instruction: {code}")
    if callable(info):
        return info(code, encoding=encoding)

    code_size = size - 2
    step = code[2] if code_size > 1 else 1
    sub = code[3] if code_size > 2 else None
    sub_table = info
    if sub not in sub_table:
        raise InstructionError()
    mnemonic, operand_count = sub_table[sub]
    if code_size > 3:
        flag = code[4]
        match flag:
            case 0x02:
                mnemonic = f"{mnemonic}P"
            case 0x0a:
                raise InstructionError()
            case 0x10:
                mnemonic = f"LD{mnemonic}"
            case 0x11:
                mnemonic = f"AND{mnemonic}"
            case 0x12:
                mnemonic = f"OR{mnemonic}"
            case _:
                raise InstructionError(f"unknown flag: {flag}({flag:x})")
    operands = [decode_device(bs, encoding=encoding) for _ in range(operand_count)]
    return Instruction(mnemonic, operands, step)


def _write_int(bs: BytesIO, n: int):
    # bs = []
    # n = int(num, base)
    # while True:
    #     n, x = divmod(n, 0x100)
    #     bs.append(x)
    #     if n == 0:
    #         break
    return bs


def _write_float(bs: BytesIO, n: float):
    pass


def _to_byte_list(n):
    bs = []
    while True:
        n, x = divmod(n, 0x100)
        bs.append(x)
        if n == 0:
            break
    return bs


class DeviceEncoder:
    def __init__(self, bs: BytesIO, device: str, *, double=False):
        if bs is None:
            bs = BytesIO()
        self.bs = bs
        self.device = device
        self.double = double
        self.encode()

    def encode_dev(self, name, num=None):
        if isinstance(name, DEV):
            name = (dev := name).name
            num = dev.num
        if self.double and name in ("K", "H", "E"):
            name = f"{name}D"
        code = _device_name_to_code_table.get(name, None)
        if code is None:
            raise Exception(f"unknown device: {self.device}")
        if name in "E":
            num = struct.pack("f", num)
        elif name == "ED":
            num = struct.pack("d", num)
        else:
            num = _to_byte_list(num)
        size = len(num) + 3
        self.bs.write(bytes([size, code, *num, size]))

    def encode(self):
        devs = DeviceLexer(self.device).lex()
        dev_count = len(devs)
        if dev_count == 1:
            self.encode_dev(devs[0])
        elif dev_count == 2:
            dev1, dev2 = devs
            if dev2.name == ".":
                self.encode_dev(dev2)
                self.encode_dev(dev1)
            elif dev2.name == "Z":
                self.encode_dev("-Z", dev2.num)
                self.encode_dev(dev1)
            elif dev1.name == "K":
                self.encode_dev("K-", dev1.num)
                self.encode_dev(dev2)
            else:
                self.encode_dev(dev1)
                self.encode_dev(dev2)
        else:
            raise Exception(f"device error: {self.device}")


def _write_device(bs: BytesIO, device: str, *, double=False) -> BytesIO:
    encoder = DeviceEncoder(bs, device, double=double)
    return encoder.bs


def to_num(num, base=10):
    bs = []
    n = int(num, base)
    while True:
        n, x = divmod(n, 0x100)
        bs.append(x)
        if n == 0:
            break
    return bs


class ILCompiler:
    def __init__(self):
        self.codes = BytesIO()

    def code(self):
        return self.codes.getvalue()

    def write_code(self, code):
        w = self.codes.write
        size = struct.pack("B", len(code) + 2)
        w(size)
        w(code)
        w(size)

    def write_op(self, op):
        self.write_code(bytes(op))

    def write_device(self, device):
        _write_device(self.codes, device)

    def write_devices(self, devices):
        for device in devices:
            self.write_device(device)

    def LD(self, operands):
        self.write_op([0x00])
        self.write_devices(operands)

    def OUT(self, operands):
        self.write_op([0x20])
        self.write_devices(operands)

    def OUTH(self, operands):
        pass

    def compile(self, il):
        for mnemonic, *operands in il:
            method = getattr(self, mnemonic, None)
            if callable(method):
                method(operands)
            else:
                raise Exception(f"모르는 명령: {mnemonic}")
        return self

    @classmethod
    def from_string(cls, source):
        il = []
        for line in source.splitlines():
            line = line.strip()
            if not line:
                continue
            il.append([x.upper().strip() for x in line.split()])
        return cls().compile(il)


def encode(source: str) -> bytes:
    return ILCompiler.from_string(source).code()

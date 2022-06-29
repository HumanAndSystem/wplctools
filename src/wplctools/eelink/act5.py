import ctypes
import struct
from io import BytesIO
from functools import cache
from pathlib import Path
from ctypes import c_uint32, c_long, c_short, c_int, byref, create_string_buffer, cast, POINTER
from pprint import pp
import logging

import comtypes.client
try:
    from comtypes.gen import ActSupportMsg64Lib, ActUtlType64Lib, ActProgType64Lib
except ImportError:
    from winreg import HKEY_CLASSES_ROOT, OpenKeyEx, QueryValue, KEY_READ, KEY_WOW64_32KEY
    clsid = QueryValue(HKEY_CLASSES_ROOT, "ActUtlType.ActUtlType\\CLSID")
    clsid_key = OpenKeyEx(HKEY_CLASSES_ROOT, f"CLSID\\{clsid}", 0, KEY_READ | KEY_WOW64_32KEY)
    _dir = Path(QueryValue(clsid_key, "InprocServer32")).parent
    ActSupportMsg64Lib = comtypes.client.GetModule(str(_dir / "Wrapper" / "ActSupportMsg64.dll"))
    ActUtlType64Lib = comtypes.client.GetModule(str(_dir / "ActUtlType64.exe"))
    ActProgType64Lib = comtypes.client.GetModule(str(_dir / "ActProgType64.exe"))

from .ActDefine import *
from .mc import CommandPacket, ResponsePacket, CommandPacket_3E, ResponsePacket_3E


logger = logging.getLogger(__package__)


def _patch(interface):
    methods = interface._methods_
    for method_i, item in enumerate(methods):
        restype, name, argtypes, paramflags, idlflags, doc = item
        for prefix in ("_get_", "_set_"):
            # 새로 정의될 수 있도록 기존 이름을 지운다.
            # 지우지 않으면 '_'이 덧붙여진다.
            _name = name if not name.startswith(prefix) else name.removeprefix(prefix)
            if hasattr(interface, _name):
                delattr(interface, _name)
        if name.startswith("Read"):
            paramflags = list(paramflags)
            for i, paramflag in enumerate(paramflags):
                pflags, argname, *defval = paramflag
                # 배열의 크기가 반영되지 않으므로
                # 버퍼를 직접 전달할 수 있도록 in으로 바꾼다.
                if argname in {"lplData", "lpsData"} and pflags == 2:
                    pflags = 1  # out -> in
                    paramflags[i] = (pflags, argname, *defval)
            paramflags = tuple(paramflags)
            methods[method_i] = (restype, name, argtypes, paramflags, idlflags, doc)
    interface._methods_ = methods  # 다시 만든다.
_patch(ActUtlType64Lib.IActUtlType64)
_patch(ActProgType64Lib.IActProgType64)
del _patch


__all__ = ["ActUtlType", "ActProgType"]


def act_get_error_message(error_code):
    obj = comtypes.client.CreateObject(ActSupportMsg64Lib.ActSupportMsg64)
    error_message, retval = obj.GetErrorMessage(error_code)
    if retval != 0:
        raise Exception(f"cannot get error message: {retval:08x}")
    return error_message


class ActError(Exception):
    def __init__(self, error_code: int, error_message: str = None):
        self.error_code = error_code
        if error_message is None:
            error_message = act_get_error_message(error_code)
        super().__init__(error_message)


class ActCommon:
    def __init__(self, *, error_check=True):
        self._object = None
        self.error_check = error_check

    def _call(self, method, *args, **kwds):
        retval = method(*args, **kwds)
        if self.error_check:
            error_code = retval[-1] if isinstance(retval, tuple) else retval
            if error_code != 0:
                raise ActError(error_code)
        return retval

    def close(self):
        obj = self._object
        self._call(obj.Close)

    def get_device(self, device):
        obj = self._object
        value, retval = self._call(obj.GetDevice2, device)
        return value

    def set_device(self, device, value):
        obj = self._object
        retval = self._call(obj.SetDevice2, device, value)

    def get_cpu_type(self):
        obj = self._object
        cpu_name, cpu_code, retval = self._call(obj.GetCpuType)
        return cpu_name, cpu_code

    def read_device_random2(self, device_list):
        device_count = len(device_list)
        data = create_string_buffer(device_count * 2)
        retval = self._call(self._object.ReadDeviceRandom2, "\n".join(device_list), device_count, cast(data, POINTER(c_short)))
        return data.raw

    def read_device_random(self, device_list):
        device_count = len(device_list)
        data = create_string_buffer(device_count * 4)
        retval = self._call(self._object.ReadDeviceRandom, "\n".join(device_list), device_count, cast(data, POINTER(c_int)))
        return data.raw

    def write_device_block2(self, device, data):
        device_count = len(data) // 2
        # TODO: 읽기만 하면 되는데...
        if isinstance(data, bytes):
            data = bytearray(data)
        data = (c_short*device_count).from_buffer(data)
        retval = self._call(self._object.WriteDeviceBlock2, device, device_count, data)

    def write_device_block(self, device, data):
        # 비트 디바이스인 시작 디바이스 번호는 16의 배수여야 한다.
        device_count = len(data) // 4
        data = create_string_buffer(data, len(data))
        data_p = cast(data, POINTER(c_int))
        retval = self._call(self._object.WriteDeviceBlock, device, device_count, data_p)

    get_error_message = staticmethod(act_get_error_message)


class ActUtlType(ActCommon):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self._object = comtypes.client.CreateObject(ActUtlType64Lib.ActUtlType64)

    def open(self, stno: int):
        obj = self._object
        obj.ActLogicalStationNumber = stno
        self._call(obj.Open)
        return self


class ActProgType(ActCommon):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self._object = comtypes.client.CreateObject(ActProgType64Lib.ActProgType64)

    def open_simulator2(self, target = 0):
        """
        Specify the connection destination GX Simulator2 in start status.
        When connecting to FXCPU, specify "0" (0x00).
        ■Property value
            0 (0x00): None
            (When only one simulator is in start status, connects to the simulator in start status. When
            multiple simulators are in start status, search for the simulators in start status and connect them in
            alphabetical order.)
            1 (0x01): Simulator A
            2 (0x02): Simulator B
            3 (0x03): Simulator C
            4 (0x04): Simulator D
        ---
        Specify the PLC number of the connection destination GX Simulator3 in start status.
        ---
        Specify the connection destination MT Simulator2 in start status.
        ■Property value
            2 (0x02): Simulator No.2
            3 (0x03): Simulator No.3
            4 (0x04): Simulator No.4
        """
        obj = self._object
        obj.ActUnitType = UNIT_SIMULATOR2
        obj.ActTargetSimulator = target
        self._call(obj.Open)
        return self


_device_name_table = {
    0x90: "M",
    0x92: "L",
    0xa8: "D",
    0xaf: "R",
    0xb0: "ZR",
    0xb4: "W"}

_hex_device_set = {
    0x9c,  # X
    0x9d,  # Y
    0x9e,  # FX
    0x9f,  # FY
    0xa0,  # B
    0xa1,  # SB
    0xa2,  # DX
    0xa3,  # DY
    0xb4,  # W
    0xb5,  # SW
    0xf8,  # U
}

def _device_code_to_name(code: int, num: int, *, device_names=_device_name_table, hex_devices=_hex_device_set):
    name = device_names.get(code, "?")
    if code in hex_devices:
        return f"{name}{num:x}"
    else:
        return f"{name}{num}"


class MCRepeater:
    def __init__(self, target):
        self.target = target

    @cache
    def _get_method(self, command: int, subcommand: int):
        method_name = f"_command_{command:04x}_{subcommand:04x}"
        return getattr(self, method_name, None)

    def _command_0101_0000(self, command: CommandPacket, response: ResponsePacket):
        logger.debug("CPU model name read")
        cpu_name, cpu_code = self.target.get_cpu_type()
        cpu_name = f"{cpu_name:16}".encode("latin")
        response.data = struct.pack("<16sH", cpu_name, cpu_code)

    def _command_0403_0000(self, command: CommandPacket, response: ResponsePacket):
        logger.debug("Random read in word units")
        word, dword = command.decode_random_read_data()
        data = BytesIO()
        if word:
            data.write(self.target.read_device_random2(word))
        if dword:
            data.write(self.target.read_device_random(dword))
        response.data = data.getvalue()

    def _command_1401_0000(self, command: CommandPacket, response: ResponsePacket):
        logger.debug("Batch write in word units")
        device_code, count, value_data = command.decode_1401_0000_data()
        device_name = _device_code_to_name(*device_code)
        self.target.write_device_block2(device_name, value_data)

    def _command_1401_0001(self, command: CommandPacket, response: ResponsePacket):
        logger.debug("Batch write in bit units")
        device, count, value_list = command.decode_1401_0001_data()
        code, num = device
        target = self.target
        value_i = 0

        def next_bit():
            nonlocal value_i
            n, m = divmod(value_i, 2)
            value_i += 1
            value = value_list[n]
            return (value if m else value >> 4) & 0x1
 
        def next_word():
            nonlocal value_i
            v = value_list
            i0 = value_i
            i1 = i0 + 1
            i2 = i0 + 2
            i3 = i0 + 3
            i4 = i0 + 4
            i5 = i0 + 5
            i6 = i0 + 6
            i7 = i0 + 7
            value_i += 8
            return (
                  (((v[i7] >> 4) & 0x1) << 14) | ((v[i7] & 0x1) << 15)
                | (((v[i6] >> 4) & 0x1) << 12) | ((v[i6] & 0x1) << 13)
                | (((v[i5] >> 4) & 0x1) << 10) | ((v[i5] & 0x1) << 11)
                | (((v[i4] >> 4) & 0x1) <<  8) | ((v[i4] & 0x1) <<  9)
                | (((v[i3] >> 4) & 0x1) <<  6) | ((v[i3] & 0x1) <<  7)
                | (((v[i2] >> 4) & 0x1) <<  4) | ((v[i2] & 0x1) <<  5)
                | (((v[i1] >> 4) & 0x1) <<  2) | ((v[i1] & 0x1) <<  3)
                | (((v[i0] >> 4) & 0x1) <<  0) | ((v[i0] & 0x1) <<  1))

        while count:
            if (num % 16 != 0) or count < 16:
                device_name = _device_code_to_name(code, num)
                target.set_device(device_name, next_bit())
                num += 1
                count -= 1
            else:
                device_name = _device_code_to_name(code, num)
                data = ctypes.c_uint16(next_word())
                target.write_device_block2(device_name, 1, byref(data))

    def _process_command(self, command: CommandPacket, response: ResponsePacket):
        method = self._get_method(command.command, command.subcommand)
        if callable(method):
            return method(command, response)
        response.complete_code = 0x1234
        print(f"unknown {command.command:04x} {command.subcommand:04x}")

    def _3e(self, data: bytes) -> bytes:
        command = CommandPacket_3E.from_data(data)
        response = ResponsePacket_3E()
        self._process_command(command, response)
        return response.encode(command)

    def _4e(self, data: bytes) -> bytes:
        raise NotImplementedError()

    def process(self, data: bytes) -> bytes:
        subheader = data[:2]
        if subheader == b"\x50\x00":
            return self._3e(data)
        elif subheader == b"\x54\x00":
            return self._4e(data)
        else:
            raise Exception(f"unknown subheader: {subheader}")



"""
0000   02 00 00 00 45 00 00 45 4d e6 00 00 80 11 00 00
0010   7f 00 00 01 7f 00 00 01 13 89 13 89 00 31 4f 23
0020   

51 01 
00 00 00 11 11 07 00 
01 
0a 
ff 03 
01 
01 
fe 03 
00 00 

14 00 
1c 08 0a 08 00 00 00 00 
00 00 00 04 01 01 01 00 
00 00 00 01


51 01 subheader

00 00 00 11 11 07 00

01 plc network no
04 plc station no
e0 03 cpu

01 pc network no
02 pc station no
fe 03 ?
00 00

14 00
1c 08 0a 08 00 00 00 00
00 00 00 04 01 01 01 00
00 00 00 01



02 00 00 00 45 00 00 45 8f 7c 00 00 80 11 00 00
7f 00 00 01 7f 00 00 01 13 89 13 89 00 31 45 21

51 01
00 00 00 11 11 07 00
02 0b ff 03
02 0a fe 03
00 00
14 00
1c 08 0a 08 00 00 00 00
00 00 00 04 01 01 01 00
00 00 00 01

0000   02 00 00 00 45 00 00 51 91 25 00 00 80 11 00 00
0010   7f 00 00 01 7f 00 00 01 17 70 13 89 00 3d 35 e6

51 01
00 00 00 11 11 07 00
02 0b 23 3d
02 0a fe 03
00 00
20 00
1c aa 16 14 ff 03 00 00
00 00 00 04 00 00 00 00
00 00 00 00 00 00 00 00
01 21 01 00 00 00 00 01


51 01
00 0b 0a 91 91 07 00
07 08 e0 03
02 0a fe 03
00 00
14 00
1c 08 0a 08 00 00 00 00 00 00 00
04 01 01 01 00 00 00 00 01


0000   02 00 00 00 45 00 00 45 92 9b 00 00 80 11 00 00
0010   7f 00 00 01 7f 00 00 01 17 70 13 89 00 31 c5 c3

51 01
00 0f 04 91 91 07 00
07 08 e1 03
02 04 fe 03
00 00
14 00
1c 08 0a 08 00 00 00 00 00 00 00
04 01 01 01 00 00 00 00 01

0000   02 00 00 00 45 00 00 45 92 cd 00 00 80 11 00 00
0010   7f 00 00 01 7f 00 00 01 17 70 13 89 00 31 7f 13

51 01 00 00 00 11 11 07 00 
02 0f 44 24 
02 04 fe 03 00 00

14 00
1c a8 0a 08 e1 03 00 00 00 00 00
04 01 01 01 00 00 00 00 01

"""


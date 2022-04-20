"""
"""

import re

from numpy import isin


class Device:
    pass


def to_zerohex(n, lower=False):
    """주어진 수를 16진수 문자열로 바꾼다.

    `n` 16진수로 바꿀 수.

    `lower`가 True이면 바꿀 때 소문자를 사용한다.
    기본값은 False로 대문자를 사용한다.

    첫 문자가 숫자가 아니면 앞에 0을 추가한다.
    그래서 함수 이름에 zero가 들어간 것이다.
    """
    hex = f"{n:x}" if lower else f"{n:X}"
    if hex[:1] in "ABCEDFabcdef":
        return f'0{hex}'
    return hex


def int_to_byte_list(n):
    bs = []
    while True:
        n, x = divmod(n, 0x100)
        bs.append(x)
        if n == 0:
            break
    return bs


def float_to_byte_list(n):
    bs = []
    while True:
        n, x = divmod(n, 0x100)
        bs.append(x)
        if n == 0:
            break
    return bs


class DEV:
    __slots__ = ("name", "num")

    def __init__(self, name, num):
        self.name = name
        self.num = num

    def __eq__(self, other):
        if isinstance(other, DEV):
            return self.name == other.name and self.num == other.num
        elif isinstance(other, (list, tuple)):
            return self.name == other[0] and self.num == other[1]
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, DEV):
            other = other.to_tuple()
        elif isinstance(other, (list, tuple)):
            other = tuple(other)
        else:
            raise TypeError(f"'<' not supported between instances of {type(self).__name__!r} and {type(other).__name__!r}")
        return self.to_tuple() < other

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, num={self.num!r})"

    def __str__(self):
        name = self.name
        if name == "\\" or name == "@":
            return name
        if self.is_hex_device(name):
            if name == ".":
                return f".{self.num:X}"
            return f"{name}{to_zerohex(self.num)}"
        return f"{name}{self.num}"

    def to_tuple(self):
        return (self.name, self.num)

    @staticmethod
    def from_string(device):
        devs = DeviceLexer(device).lex()
        if len(devs) == 1:
            return devs[0]
        raise Exception(f"device is not one: {device}")

    @classmethod
    def from_tuple(cls, dev):
        if len(dev) != 2:
            raise Exception(f"is not device: {dev}")
        return cls(dev[0], dev[1])

    @staticmethod
    def is_bit_device(name):
        return name in {"SM", "X", "Y", "M", "L", "B", "F", "SB", "DX", "DY", "V", "TS", "TC", "CS", "CC", "SS", "SC", "STS", "STC"}

    @staticmethod
    def is_hex_device(name):
        return name in {"X", "Y", "B", "W", "SB", "SW", "DX", "DY", "."}


DECDEV_re = re.compile(r"LST|BL|FD|LC|LT|LZ|RD|SD|SM|ST|ZR|ZZ|A|C|D|F|G|I|J|K|L|M|N|P|R|S|T|V|Z", re.I)
HEXDEV_re = re.compile(r"DX|DY|FX|FY|LB|LW|LX|LY|SB|SW|B|H|U|W|X|Y|\.", re.I)
FLOATDEV_re = re.compile(r"ED|E", re.I)
DEC_re = re.compile(r'[+-]?[0-9_]+')
HEX_re = re.compile(r'[+-]?[0-9A-Fa-f_]+')


class InvalidDevice(Exception):
    def __init__(self, device):
        super().__init__(f"invalid device: {device}")


class DeviceLexer:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def match(self, _re):
        m = _re.match(self.data, self.index)
        if m is None:
            return
        self.index = m.end()
        return m.group()

    def lex(self) -> list[DEV]:
        devs = []
        end = len(self.data)
        while self.index < end:
            if (name := self.match(DECDEV_re)):
                m = self.match(DEC_re)
                if m is None:
                    raise InvalidDevice(self.data)
                num = int(m, 10)
            elif (name := self.match(HEXDEV_re)):
                m = self.match(HEX_re)
                if m is None:
                    raise InvalidDevice(self.data)
                num = int(m, 16)
            elif (name := self.data[self.index]) in "@/\\":
                self.index += 1
                if name == "/":
                    name = "\\"
                num = 0
            else:
                raise InvalidDevice(self.data)
            devs.append(DEV(name, num))
        return devs

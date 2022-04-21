from io import StringIO, BytesIO, SEEK_SET, SEEK_END
import datetime
import struct


__all__ = [
    "to_zerohex",
    "dump_binary",
    "BinaryIO",
]


def to_zerohex(n: int, lower=False):
    """convert specified number to hex.

    `n`: number to be changed to hex.
    `lower`: if True use lowercase. default is False, use uppercase.

    if first char is not number, prepend '0'.
    """
    hex = f"{n:x}" if lower else f"{n:X}"
    if hex[:1] in "ABCEDFabcdef":
        return f'0{hex}'
    return hex


def remove_stringio_last_lf(ss: StringIO):
    size = ss.seek(0, SEEK_END)
    if size:
        last = size - 1
        c = ss.seek(last, SEEK_SET)
        if c == "\n":
            ss.truncate(last)


def _printable_char(n):
    if 0x20 <= n < 0x7f:
        return chr(n)
    return "."


def _hexlify(data):
    return " ".join(f"{n:02x}" for n in data)


def dump_binary(data, *, indent=0, allow_last_lf=False):
    if indent:
        if isinstance(indent, int):
            INDENT = " "*indent
        else:
            INDENT = str(indent)
    else:
        INDENT = ""
    mv = memoryview(data)
    i = 0
    end = len(data)
    ss = StringIO()
    w = ss.write
    while i < end:
        line_data = mv[i:i+16]
        line_data_count = len(line_data)
        hex = _hexlify(line_data[:8])
        pad_count = 3 * (16 - line_data_count)
        if line_data_count > 8:
            hex = hex + " - " + _hexlify(line_data[8:])
        else:
            pad_count += 2
        pad = "" if line_data_count == 16 else " "*pad_count
        ascii = "".join(_printable_char(n) for n in line_data)
        w(f"{INDENT}{i:04x}: {hex}{pad}   {ascii}\n")
        i += 16
    if not allow_last_lf:
        remove_stringio_last_lf(ss)
    return ss.getvalue()


class BinaryIO(BytesIO):
    def __init__(self, data):
        super().__init__(data)

    def read_format(self, format, *, calcsize=struct.calcsize, unpack=struct.unpack):
        size = calcsize(format)
        data = unpack(format, self.read(size))
        if len(data) == 1:
            return data[0]
        return data

    def read_wstring(self):
        size = self.read_format("L")
        s = self.read(size * 2)
        return s.decode("utf-16")

    def read_date(self):
        y, m, w, d = self.read_format("4H")
        return datetime.date(year=y, month=m, day=d)

    def read_time(self):
        H, M, S = self.read_format("3H")
        return datetime.time(hour=H, minute=M, second=S)

    def read_datetime(self):
        y, m, w, d, H, M, S = self.read_format("7H")
        return datetime.datetime(year=y, month=m, day=d, hour=H, minute=M, second=S)

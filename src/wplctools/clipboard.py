from io import StringIO
from functools import lru_cache

from win32clipboard import (
    OpenClipboard,
    CountClipboardFormats,
    EnumClipboardFormats,
    GetClipboardFormatName,
    EmptyClipboard,
    GetClipboardData,
    SetClipboardData,
    RegisterClipboardFormat,
    CloseClipboard)

from .utils import dump_binary, remove_stringio_last_lf


__all__ = [
    "ClipboardData",
    "clipboard_format_id_to_name",
    "clipboard_format_name_to_id",
]


standard_format_id_to_name_table = {
    1: "CF_TEXT",
    2: "CF_BITMAP",
    3: "CF_METAFILEPICT",
    4: "CF_SYLK",
    5: "CF_DIF",
    6: "CF_TIFF",
    7: "CF_OEMTEXT",
    8: "CF_DIB",
    9: "CF_PALETTE",
    10: "CF_PENDATA",
    11: "CF_RIFF",
    12: "CF_WAVE",
    13: "CF_UNICODETEXT",
    14: "CF_ENHMETAFILE",
    15: "CF_HDROP",
    16: "CF_LOCALE",
    17: "CF_DIBV5",
    0x0081: "CF_DSPTEXT",
    0x0082: "CF_DSPBITMAP",
    0x0083: "CF_DSPMETAFILEPICT",
    0x008E: "CF_DSPENHMETAFILE",
}
standard_foramt_name_to_id_table = {value: key for key, value in standard_format_id_to_name_table.items()}


@lru_cache
def clipboard_format_name_to_id(name: str) -> int:
    if name in standard_foramt_name_to_id_table:
        return standard_foramt_name_to_id_table[name]
    return RegisterClipboardFormat(name)


@lru_cache
def clipboard_format_id_to_name(id: int) -> str:
    if id in standard_format_id_to_name_table:
        return standard_format_id_to_name_table[id]
    return GetClipboardFormatName(id)


class ClipboardData(dict):
    def __init__(self, formats=None, names=None):
        super().__init__(formats if formats is not None else {})
        self.names = names if names is not None else {}

    def __getitem__(self, format):
        if isinstance(format, str) and format in self.names:
            format = self.names[format]
        return self[format]

    @classmethod
    def read_from_clipboard(cls):
        formats = {}
        names = {}
        OpenClipboard(None)
        format = 0
        for _ in range(CountClipboardFormats()):
            format = EnumClipboardFormats(format)
            try:
                format_name = clipboard_format_id_to_name(format)
            except:
                format_name = f"_{format}_"
            names[format_name] = format
            names[format] = format_name
            try:
                formats[format] = GetClipboardData(format)
            except Exception as exc:
                print(f"{format}({format:x}) {format_name}")
                raise
        CloseClipboard()
        return cls(formats, names)

    def write_to_clipboard(self):
        if not self:
            return
        OpenClipboard(None)
        EmptyClipboard()
        for format, data in self.items():
            SetClipboardData(format, data)
        CloseClipboard()

    def dump(self):
        ss = StringIO()
        w = ss.write
        for format, data in self.items():
            format_name = self.names[format]
            w(f"=== {format}({format:x}) {format_name}\n")
            if isinstance(data, bytes):
                w(dump_binary(data))
            else:
                w(data)
            w("\n")
        remove_stringio_last_lf(ss)
        return ss.getvalue()

from io import StringIO, BytesIO
import struct
import tkinter as tk

from ..clipboard import ClipboardData
from ..melsec import (
    bcode_decode,
    bcode_encode,
    get_gxw2_mid_data,
    set_gxw2_mid_data,
)


def dump_il(data):
    bs = BytesIO(data[257:])
    il = []
    while True:
        try:
            inst = bcode_decode(bs)
        except EOFError:
            break
        il.append(str(inst))
    return "\n".join(il)


class MainFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.button_frame = tk.Frame(self)
        self.read_button = tk.Button(self.button_frame, text="read", command=self.do_read)
        self.write_button = tk.Button(self.button_frame, text="write", command=self.do_write)
        self.output_frame = tk.Frame(self)
        self.v_scrollbar = tk.Scrollbar(self.output_frame)
        self.output_text = tk.Text(self.output_frame, yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar["command"] = self.output_text.yview

        self.read_button.pack(side="left")
        self.write_button.pack()
        self.output_text.pack(side="left", expand=True, fill="both")
        self.v_scrollbar.pack(expand=True, fill="y")
        self.button_frame.pack()
        self.output_frame.pack(expand=True, fill="both")

    def do_read(self):
        data = ClipboardData.read_from_clipboard()
        if not data:
            return

        mid_data = get_gxw2_mid_data(data)
        if mid_data is None:
            s = data.dump()
        else:
            s = dump_il(mid_data)

        self.output_text.delete(1.0, "end")
        self.output_text.insert(1.0, s)

    def do_write(self):
        il = self.output_text.get(1.0, "end")
        mid_data = bcode_encode(il)

        data = ClipboardData()
        set_gxw2_mid_data(data, mid_data)
        data.write_to_clipboard()


def clipboard_viewer():
    root = tk.Tk()
    root.title("clipboard viewer")
    root.geometry("640x480")
    main = MainFrame(root)
    main.pack(expand=True, fill="both")
    root.mainloop()

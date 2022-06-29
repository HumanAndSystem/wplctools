from io import BytesIO
import struct


__all__ = ["CommandPacket_3E", "ResponsePacket_3E"]


class CommandPacket:
    subheader: int
    network_no: int
    pc_no: int
    dest_module_io: int
    dest_module_stno: int
    monitoring_timer: int
    command: int
    subcommand: int
    data: bytes


class ResponsePacket:
    subheader: int
    network_no: int
    pc_no: int
    dest_module_io: int
    dest_module_stno: int
    complete_code: int
    data: bytes


def _code_to_name(code: int):
    return {
        0x90: "M",
        0x92: "L",
        0xa8: "D",
        0xaf: "R",
        0xb0: "ZR",
        0xb4: "W",
    }.get(code, "?")


def _is_hex_device(code):
    return code in {
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


def device_code_to_name(device_code: int):
    code = (device_code >> 24) & 0xff
    num = device_code & 0xff_ffff
    name = {
        0x90: "M",
        0x92: "L",
        0xa8: "D",
        0xaf: "R",
        0xb0: "ZR",
        0xb4: "W"}.get(code, "?")
    if code in {
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
    }:
        return f"{name}{num:x}"
    else:
        return f"{name}{num}"


def split_device_code(device_code: int) -> tuple[int, int]:
    return ((device_code >> 24) & 0xff, device_code & 0xff_ffff)


class CommandPacket_3E(CommandPacket):
    def encode(self):
        pass

    def decode(self, data, *, unpack_from=struct.unpack_from):
        self.subheader = unpack_from(">H", data, 0)
        (self.network_no,
            self.pc_no,
            self.dest_module_io,
            self.dest_module_stno,
            data_length) = unpack_from("<BBHBH", data, 2)
        (self.monitoring_timer,
            self.command,
            self.subcommand,
            self.data) = unpack_from(f"<HHH{data_length - 6}s", data, 9)
        return self

    def decode_random_read_data(self, *,
            unpack_from=struct.unpack_from,
            device_code_to_name=device_code_to_name):
        data = self.data
        word_device_count, dword_device_count = unpack_from("BB", data, 0)
        code_list = unpack_from(f"<{word_device_count}L", data, 2)
        word_device_list = [device_code_to_name(code) for code in code_list]
        code_list = unpack_from(f"<{dword_device_count}L", data, 2 + 4*word_device_count)
        dword_device_list = [device_code_to_name(code) for code in code_list]
        return (word_device_list, dword_device_list)

    def decode_0403_0000_data(self, *, unpack_from=struct.unpack_from, split_device_code=split_device_code):
        data = self.data
        word_device_count, dword_device_count = unpack_from("BB", data, 0)
        code_list = unpack_from(f"<{word_device_count}L", data, 2)
        word_device_list = [split_device_code(code) for code in code_list]
        code_list = unpack_from(f"<{dword_device_count}L", data, 2 + 4*word_device_count)
        dword_device_list = [split_device_code(code) for code in code_list]
        return (word_device_list, dword_device_list)

    def decode_1401_0000_data(self, *, unpack_from=struct.unpack_from, split_device_code=split_device_code):
        # batch write in word units
        data = self.data
        device_code, count = unpack_from(f"<LH", data, 0)
        device = split_device_code(device_code)
        value_data = data[6:]
        return (device, count, value_data)

    def decode_1401_0001_data(self, *, unpack_from=struct.unpack_from, split_device_code=split_device_code):
        # batch write in bit units
        data = self.data
        device_code, count = unpack_from(f"<LH", data, 0)
        device = split_device_code(device_code)
        value_data = data[6:]
        return (device, count, value_data)

    @classmethod
    def from_data(cls, data: bytes):
        return cls().decode(data)


class ResponsePacket_3E(ResponsePacket):
    def __init__(self):
        self.complete_code = 0
        self.data = b""

    def encode(self, command: CommandPacket, *, pack=struct.pack):
        if self.complete_code != 0:
            self.data = pack("<BBHBHH",
                # 11,
                # self.complete_code,
                command.network_no,
                command.pc_no,
                command.dest_module_io,
                command.dest_module_stno,
                command.command,
                command.subcommand)
        data_length = len(self.data)

        data = BytesIO()
        w = data.write
        # w(pack(">H", command.subheader | 0x8000))
        w(b"\xd0\x00")  # subheader
        w(pack(f"<BBHBHH{data_length}s",
            command.network_no,
            command.pc_no,
            command.dest_module_io,
            command.dest_module_stno,
            data_length + 2,
            self.complete_code,
            self.data))
        return data.getvalue()

    @classmethod
    def decode(cls, data):
        pass

    @classmethod
    def from_data(cls, data: bytes):
        return cls().decode(data)

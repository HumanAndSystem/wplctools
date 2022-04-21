import struct

from ..clipboard import (
    ClipboardData,
    clipboard_format_name_to_id,
)


__all__ = [
    "get_gxw2_mid_data",
    "set_gxw2_mid_data",
]


GXW2_MIDDATA_FORMAT_NAME = "SWnDN-GPPW2 MLDWnd::MidData"
GXW2_CIRDATA_FORMAT_NAME = "SWnDN-GPPW2 MLDWnd::CirData"
GXW3_BLOCKDATA_FORMAT_NAME = "Melco.GXW3.WorkWindow.Program.Ladder.Editor.Controller.CopyPaste.Data.CopyPasteBlocks"
GXW3_CELLDATA_FORMAT_NAME = "Melco.GXW3.WorkWindow.Program.Ladder.Editor.Controller.CopyPaste.Data.CopyPasteCells"


def get_gxw2_mid_data(data: ClipboardData) -> bytes:
    format = clipboard_format_name_to_id(GXW2_MIDDATA_FORMAT_NAME)
    return data.get(format, None)


"""
    PLC Type이 맞지 않으면 붙여넣기 할 때 다음과 같은 에러가 발생한다.
        PLC series is different between copy source and paste target.
        Are you sure you want to continue?

        Caution
        Pasting may not be done correctly if the target PLC series is different one.
        In that situation, correcting program may be required after pasting operation.

        Remark
        Please change PLC type to execute pasting operation correctly.

    스텝관련 정보는 없어도 붙여넣는데는 문제가 없다.
    하지만 잘못된 스텝수는 붙여넣기 후 undo할 때 영향을 준다.
    스텝수에 기록된 갯수만큼만 undo하는 것으로 보인다.
    즉, 스텝수가 맞지 않으면 깔끔하게 undo가 되지 않는다.
    스텝수가 적으면 지저분하게 남을 것이고,
    스텝수가 많으면 붙여넣기 하지 않는 것까지 지워버린다.
    심지어 마지막 END도 지워버린다.
"""

def set_gxw2_mid_data(data: ClipboardData, code: bytes):
    head = bytearray(257)

    struct.pack_into("H", head, 0x00, 0)
    struct.pack_into("L", head, 0x04, 3)  # PLC type
    # struct.pack_into("w", head, 0x08, "MAIN")  # program name
    struct.pack_into("LL", head, 0x8a, 0, 0)  # 시작과 끝 스텝
    struct.pack_into("B", head, 0xeb, 0xc4)  # CPU type
    struct.pack_into("LL", head, 0xf3, len(code), 0)  # 코드크기 스텝수

    format = clipboard_format_name_to_id(GXW2_MIDDATA_FORMAT_NAME)
    data[format] = head + code + b"\x00"*5


"""
SWnDN-GPPW2 MLDWnd::CirData

왼쪽 세로선만 복사된다.
양쪽의 세로선을 모두 복사하려면 

head size: 254
프로그램의 이름 외에 다른 것들은 무슨 의미인지 모르겠다.

device 부분의 크기 long
device

ladder
한 칸은 8바이트
0: 선의 0000
  b0
  b1
  b2 아래 세로선
  b3 위 세로선

  0001 1
  0011 3  가로선과 연관이 있는 것 같은데... 모르겠다.
  0111 7
  1111 f
  1011 b

선 명령 인수위치 위치번호
"""
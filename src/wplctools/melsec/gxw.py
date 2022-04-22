from io import BytesIO, SEEK_CUR
import xml.etree.ElementTree as ET
from pprint import pformat
import logging

import olefile

from ..utils import BinaryIO


logger = logging.getLogger(__package__)


class BinaryStream(BinaryIO):
    def read_string(self):
        return self.read_wstring()

    def read_code(self):
        data = self.read(1)
        if data:
            size = ord(data)
            self.seek(-1, SEEK_CUR)
            return size, self.read(size)
        return 0, b""

    def read_device(self):
        pass
        # return DeviceReader(self).read_device()

    def read_ladder(self):
        pass
        # size, code = self.read_code()
        # if size == 0:
        #     return None
        # return LadderReader(self).read(code)


class Program:
    def __init__(self, name, files):
        self.name = name
        prefix = f"{name}."
        lst = {}
        for filename, data in files.items():
            if filename.startswith(prefix):
                lst[filename.removeprefix(prefix)] = data
        self.file_list = lst

    def dump_ladder(self, code):
        size = len(code)
        print(f"{size}({size:x})")
        f = BinaryStream(code)
        print(f.read_format("LL"))
        print(f.read_code())
        step = 0
        while True:
            instruction = f.read_ladder()
            if instruction is None:
                break
            print(f"{step}:\t{instruction}")
            step += instruction.step

    def dump_program(self):
        data = self.file_list["Program.pou"]
        print(len(data))
        f = BinaryStream(data)
        print("Title:", f.read_string())
        print("Comment:", f.read_string())
        print(f.read(22))
        # print("Type:",)
        print("Last Change:", f.read_datetime())

        print(f.read(6))  # 0 0 1 0 0 0
        lang = ord(f.read(1))
        print(f"Language: {lang}({lang:x})")
        # print(f.read(12))

        # language
        # 1: Ladder
        # 193(c1): ST
        # 208(d0): Structured Ladder/FBD
        # 240(f0): SFC MELSAP3
        if lang == 1:
            size = f.read_format("L")
            self.dump_ladder(f.read(size))
        elif lang == 193:
            # code
            print(repr(f.read_string()))
        elif lang == 208:
            code = f.read()
            print(code[:100])
        else:
            code = f.read()
            print(code[:100])

        # rest
        rest = f.read()
        print(len(rest), rest)

    def dump(self):
        self.dump_program()
        # for i in ("Labels.lh", "tsk", "res"):
        #     print(f"=== {i}")
        #     print(self.file_list[i])

    def __getitem__(self, key):
        return self.file_list[key]


class GXWFile:
    def __init__(self):
        pass

    def load(self, path):
        self.doc = olefile.OleFileIO(path)
        logger.debug(self.doc.listdir())
        return self

    def open(self, path):
        return self.doc.openstream(path)

    def close(self):
        self.doc.close()

    def test(self):
        stream = self.open("projectdatalist.xml")
        with BytesIO(stream.read()) as f:
            tree = ET.parse(f)
        root = tree.getroot()

        files = {}
        pou = {}
        data_list = root.findall("*//D_Projectdata")
        pou_suffix = ".Program.pou"
        for data in data_list:
            id = data.find("iID").text
            name = data.find("szName").text
            files[name] = id
            if name.endswith(pou_suffix):
                pou[name.removesuffix(pou_suffix)] = id
        logger.debug(pformat(files.keys()))

        _hdb = self.open("_hdb")
        with BytesIO(_hdb.read()) as f:
            hdb = olefile.OleFileIO(f)
            try:
                logger.debug(hdb.listdir())
                for name, fileid in files.items():
                    logger.debug(f"{name} {fileid}")
                    try:
                        stream = hdb.openstream(fileid)
                    except OSError as exc:
                        if not (str(exc) == "file not found" and name == "Project.gd2"):
                            raise
                    files[name] = stream.read()
            finally:
                hdb.close()

        logger.debug(pformat(pou.keys()))
        for name in pou.keys():
            print(f"=== {name}")
            pou[name] = Program(name, files)
            pou[name].dump()


if __name__ == "__main__":
    level = logging.INFO
    # level = logging.DEBUG
    logging.basicConfig(level=level)

    gxw = GXWFile().load("d:/sandbox/plc/test.gxw")
    # gxw = GXWFile().load("배포-211125_155307\lamirail.gxw")
    gxw.test()
    gxw.close()

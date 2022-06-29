from io import StringIO
from itertools import groupby
from collections import namedtuple
from pprint import pp
from textwrap import dedent
from string import ascii_uppercase


device_list = """
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    BL
    DX DY
    FD FX FY
    LB LW LX LY LZ LC LT LST
    RD
    SM SD SB SW ST
    ZZ ZR
    KD HD ED
    TC TS TN LTC LTS LTN
    CC CS CN LCC LCS LCN
    STC STS STN LSTC LSTS LSTN
    . @ \\
"""
hex_list = "X Y B W . DX DY FX FY"
word_list = "D R ZR W FD SD"
bit_list = "M L B X Y"


def rename(name):
    return {
        ".": "Dot",
        "@": "At",
        "\\": "Sep",
    }.get(name, name)


def indent(prefix, text, first=1):
    def prefixed_lines():
        nonlocal first
        for line in text.splitlines(True):
            yield (prefix + line if first else line)
            first = 1
    return "".join(prefixed_lines())


DevInfo = namedtuple("DevInfo", "name code code_name".split())


def to_num(c):
    if c in "0123456789":
        return ord(c) - ord("0")
    if c in "ABCDEF":
        return 10 + ord(c) - ord("A")
    if c in "abcdef":
        return 10 + ord(c) - ord("a")
    raise ValueError("뭐냐!")


def output(f):
    def output_f(*args, **kwds):
        sb = StringIO()
        return f(*args, **kwds, w=sb.write), sb.getvalue()
    return output_f


class Gen:
    @output
    def gen_device_enum(self, device_list, w):
        device_list = sorted(device_list, key=lambda x: (len(x), x))
        w("enum Device {\n")
        w(f"    DevSkip = -2,\n")
        w(f"    DevError = -1,\n")
        w(f"    DevNone = 0,\n")
        device_dict = {}
        for i, device_name in enumerate(device_list, 1):
            code_name = f"Dev{rename(device_name)}"
            w(f"    {code_name} = {i},\n")
            device_dict[device_name] = DevInfo(device_name, i, code_name)
        w("};\n")
        return device_dict

    @output
    def gen_code_to_name(self, device_dict, w):
        w("char* code_to_name(int code) {\n")
        w("    switch (code) {\n")
        for name, info in device_dict.items():
            if name == "\\":
                name = "\\\\"
            w(f"        case {info.code_name}: return \"{name}\";\n")
        w("    };\n")
        w("    return \"?\";\n")
        w("};\n")
        return device_dict

    @output
    def gen_scan_name(self, device_dict, w):
        error = DevInfo("", 0, "DevError")

        def _remove_first(c: str, g: list[str]):
            return [x.removeprefix(c) for x in sorted(g)][1:]

        @output
        def _switch(level: int, prefix: str, lst: list, w):
            data = {c: _remove_first(c, g) for c, g in groupby(sorted(lst), lambda k: k[:1])}
            w(f"switch (this->p({level}))" " {\n")
            for c, g in data.items():
                device = prefix + c
                if c == "\\":
                    w("    case '/':\n")
                if c in ascii_uppercase:
                    w(f"    case {c.lower()!r}:\n")
                w(f"    case {c!r}: ")
                if g:
                    _, text = _switch(level+1, device, g)
                    w(indent("        ", text, 0))
                else:
                    res = device_dict[device].code_name
                    w(f"this->seek({level+1}); return {res};\n")
            if level == 0:
                for n in "012345678":
                    w(f"    case {n!r}:\n")
                w(f"    case '9': return DevNone;\n")
                w(f"    case '%': this->seek(1); return DevSkip;\n")
            w("    default: ")
            if prefix in device_dict:
                res = device_dict[prefix].code_name
                w(f"this->seek({level}); return {res};\n")
            else:
                w("return DevError;\n")
            w("}\n")
            w("return DevError;\n")

        _, text = _switch(0, "", device_dict.keys())
        w("int scan_name() {\n")
        w(indent("    ", text))
        w("}\n")

    @output
    def gen_scan_n(self, name, base, lst, w):
        @output
        def _body(w):
            w("int n = -1;\n")
            w("while (!this->end()) {\n")
            w("    int c = this->p(0);\n")
            w("    switch (c) {\n")
            for c in lst:
                w(f"        case {c!r}: c = {to_num(c)}; break;\n")
            w(f"        default: return n;\n")
            w("    }\n")
            w(f"    n = (n < 0) ? c : (n * {base} + c);\n")
            w(f"    this->seek(1);\n")
            w("}\n")
            w("return n;\n")

        _, body = _body()
        w(f"int scan_{name}() " "{\n")
        w(indent("    ", body))
        w("}\n")

    @output
    def gen_scan_device(self, device_dict, w):
        @output
        def _switch(w):
            w("int code = this->scan_name();\n")
            w("int num = -1;\n")
            w("switch (code) {\n")
            w("    case DevError:\n")
            w("        return 0;\n")
            w("    case DevSkip:\n")
            w("        continue;\n")
            w("    case DevAt:\n")
            w("    case DevSep:\n")
            w("        num = 0;\n")
            w("        break;\n")
            for name in hex_list.split():
                info = device_dict[name]
                w(f"    case {info.code_name}:\n")
            w("        num = this->scan_hex();\n")
            w("        break;\n")
            w("    default:\n")
            w("        num = this->scan_dec();\n")
            w("        break;\n")
            w("}\n")

        @output
        def _while(w):
            _, switch = _switch()
            w("while (!this->end()) {\n")
            w(indent("    ", switch))
            w(indent("    ", dedent("""\
                devs.add(code, num);
            """)))
            w("}\n")

        _, text = _while()
        w("int scan_device(DEVs& devs) {\n")
        w(indent("    ", text))
        w("}\n")

    @output
    def gen_lexer_class(self, device_dict, w):
        w("class lexer {\n")
        w(indent("", dedent("""\
        private:
            char* _p;
            char* _end;
            int end() {
                return this->_p >= this->_end;
            }
            int p(int i = 0) {
                return this->_p[i];
            }
            void seek(int n = 1) {
                this->_p += n;
            }
        """)))
        _, text = self.gen_scan_name(device_dict)
        w(indent("    ", text))
        _, text = self.gen_scan_n("dec", 10, "0123456789")
        w(indent("    ", text))
        _, text = self.gen_scan_n("hex", 16, "0123456789ABCDEFabcdef")
        w(indent("    ", text))
        _, text = self.gen_scan_device(device_dict)
        w(indent("    ", text))
        w(indent("", dedent("""\
        public:
            int scan(char* p, int length, DEVs& devs) {
                this->_p = p;
                if (length < 0) {
                    length = (int)strlen(p);
                }
                this->_end = p + length;
                return this->scan_device(devs);
            }
        """)))
        w("};\n")

    @output
    def gen_lexer(self, w):
        # w("#define PY_SSIZE_T_CLEAN\n")
        # w("#include <Python.h>\n")
        # w("\n")
        _device_list = device_list.split()
        device_dict, text = self.gen_device_enum(_device_list)
        w(text)
        w("\n")
        _, text = self.gen_code_to_name(device_dict)
        w(text)
        w("\n")
        _, text = self.gen_lexer_class(device_dict)
        w(text)

    def run(self):
        _, text = self.gen_lexer()
        with open("_lexer.h", "w", encoding="utf-8") as f:
            f.write(text)


Gen().run()

#include <iostream>
#include <sstream>
#include <exception>
#include <pybind11/pybind11.h>

namespace py = pybind11;

char* code_to_name(int code);
bool is_hex_device(int code);


class DEV {
private:
    int code;
    int num;
public:
    DEV(int code, int num) : code(0), num(num) {}
    DEV(py::str name, int num) : code(0), num(num) {}
    DEV(py::str name) : code(0), num(num) {}

    py::str get_name() { return ""; }
};


class DEVs {
public:
    const int MAX = 10;
    int _devs[10];
    int _count;
    DEVs(): _count(0) {}
    void add(int code, int num) {
        if (this->_count >= MAX) {
            throw new std::exception();
        }
        this->_devs[this->_count++] = code;
        this->_devs[this->_count++] = num;
    }
    py::object to_object() {
        py::list devs;
        for (int i = 0; i < this->_count; i += 2) {
            int code = this->_devs[i];
            int num = this->_devs[i+1];
            devs.append(py::make_tuple(code_to_name(code), num));
        }
        return devs;
    }
    void dump() {
        for (int i = 0; i < this->_count; i += 2) {
            int code = this->_devs[i];
            int num = this->_devs[i+1];
            std::cout << code_to_name(code) << " " << num << " ";
            std::cout << std::endl;
        }
    }
};

#include "_lexer.h"

// class DeviceLexer {
// public:
//     const char* data;
//     int index;
//     DeviceLexer(const char* data): data(data), index(0) {
//     }
//     char next() {
//         return this->data[this->index++];
//     }
//     char peek() {
//         return this->data[this->index];
//     }
//     int scan_name(std::string s) {
//         auto device_code = ::scan_name(s)
//     }
//     int scan_hex(std::string s) {
//         return 0;
//     }
//     int scan_dec(std::string s) {
//         return 0;
//     }
//     int is_hex() {
//         return 0;
//     }
//     int is_dec() {
//         return 0;
//     }
//     int is_word() {
//         return 0;
//     }
//     int is_bit() {
//         return 0;
//     }
//     int lex();
// };

// py::object device_lex(py::args device) {
py::object device_lex(py::str device) {
    // DEVs devs;
    // std::cout << (char*)device << std::endl;
    py::print(device);

    // PyUnicode_ device.ptr()

    std::cout << "PyUnicode_WCHAR_KIND: " << PyUnicode_WCHAR_KIND << std::endl;
    std::cout << "PyUnicode_1BYTE_KIND: " << PyUnicode_1BYTE_KIND << std::endl;
    std::cout << "PyUnicode_2BYTE_KIND: " << PyUnicode_2BYTE_KIND << std::endl;
    std::cout << "PyUnicode_4BYTE_KIND: " << PyUnicode_4BYTE_KIND << std::endl;
    PyObject* op = device.ptr();
    int type = PyUnicode_KIND(op);
    std::cout << "PyUnicode_KIND: " << type << std::endl;
    size_t size = PyUnicode_GET_LENGTH(op);
    std::cout << "length: " << size << std::endl;

    auto s = (std::string)device;
    std::cout << "length: " << s.length() << std::endl;
    std::cout << "text: " << s.c_str() << std::endl;

    // if (type == PyUnicode_1BYTE_KIND) {
    //     auto s = PyUnicode_1BYTE_DATA(op);
    //     s[0] = 'A';
    // } else if (type == PyUnicode_2BYTE_KIND) {
    //     auto s = PyUnicode_2BYTE_DATA(op);
    //     s[0] = 'A';
    // } else if (type == PyUnicode_4BYTE_KIND) {
    //     auto s = PyUnicode_4BYTE_DATA(op);
    //     s[0] = 'A';
    // } else {
    //     return py::str("return");
    // }

    return py::none();

    // lexer().scan("K1D2.3", -1, devs);
    // devs.dump();
    // return devs.to_object();
}

    // devs = []
    // end = len(self.data)
    // while self.index < end:
    //     if (name := self.match(DECDEV_re)):
    //         m = self.match(DEC_re)
    //         if m is None:
    //             raise InvalidDevice(self.data)
    //         num = int(m, 10)
    //     elif (name := self.match(HEXDEV_re)):
    //         m = self.match(HEX_re)
    //         if m is None:
    //             raise InvalidDevice(self.data)
    //         num = int(m, 16)
    //     elif (name := self.data[self.index]) in "@/\\":
    //         self.index += 1
    //         if name == "/":
    //             name = "\\"
    //         num = 0
    //     else:
    //         raise InvalidDevice(self.data)
    //     devs.append(DEV(name, num))
    // return devs
//     return py::none();

PYBIND11_MODULE(_device, m) {
    m.def("device_lex", &device_lex);
}
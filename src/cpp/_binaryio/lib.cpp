#include <iostream>
#include <stdexcept>
#include <pybind11/pybind11.h>

namespace py = pybind11;

// typedef char i8;
// typedef short i16;
// typedef long i32;
// typedef long long i64;
// typedef unsigned char u8;
// typedef unsigned short u16;
// typedef unsigned long u32;
// typedef unsigned long long u64;

using i8 = int8_t;
using i16 = int16_t;
using i32 = int32_t;
using i64 = int64_t;

using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;

template <typename T>
static T read_n(void* p) {
    return *((T*)p);
}

template <typename T, typename std::enable_if<sizeof(T) == 2, u16>::type>
static T read_n_be(void* p) {
    using U = std::enable_if<sizeof(T) == 2, u16>::type;
    return (T)_byteswap_ushort(*((U*)p));
}

template <typename T, typename std::enable_if<sizeof(T) == 4, u32>::type>
static T read_n_be(void* p) {
    using U = std::enable_if<sizeof(T) == 4, u32>::type;
    return (T)_byteswap_ulong(*((U*)p));
}

template <typename T, typename std::enable_if<sizeof(T) == 8, u64>::type>
static T read_n_be(void* p) {
    using U = std::enable_if<sizeof(T) == 8, u64>::type;
    return (T)_byteswap_uint64(*((U*)p));
}

class BinaryIO {
public:
    py::object obj;
    Py_buffer data;
    intptr_t position;

    BinaryIO(py::object exporter): obj(exporter) {
        PyObject_GetBuffer(this->obj.ptr(), &this->data, PyBUF_SIMPLE);
        this->position = 0;
    }

    ~BinaryIO() {
        PyBuffer_Release(&this->data);
    }

    intptr_t length() { return this->data.len; }
    bool readonly() { return this->data.readonly; }

    void _resize(intptr_t size) {
        PyBuffer_Release(&this->data);
        PyByteArray_Resize(this->obj.ptr(), size);
        PyObject_GetBuffer(this->obj.ptr(), &this->data, PyBUF_SIMPLE);
    }

    u8* _p(intptr_t size = 0) {
        intptr_t i = this->position;
        intptr_t next_i = this->position + size;
        if (next_i > this->length()) {
            throw std::out_of_range("out of range");
        }
        this->position = next_i;
        return (u8*)this->data.buf + i;
    }

    u8* _wp(intptr_t size = 0) {
        if (this->readonly()) {
            throw py::type_error("cannot modify read-only memory");
        }
        intptr_t i = this->position;
        intptr_t next_i = this->position + size;
        if (next_i > this->length()) {
            if (PyByteArray_Check(this->data.obj)) {
                this->_resize(next_i);
            } else {
                throw std::out_of_range("out of range");
            }
        }
        this->position = next_i;
        return (u8*)this->data.buf + i;
    }

    void _move_position(intptr_t new_position) {
        this->position = new_position;
        if (this->position < 0) {
            this->position = 0;
        } else {
            intptr_t max = this->length();
            if (this->position > max) {
                this->position = max;
            }
        }
    }

    intptr_t seek(intptr_t offset, int whence = SEEK_SET) {
        switch (whence) {
            case SEEK_SET:
                this->_move_position(offset);
                break;
            case SEEK_CUR:
                this->_move_position(this->position + offset);
                break;
            case SEEK_END:
                this->_move_position(this->length() + offset);
                break;
        }
        return this->position;
    }

    intptr_t tell() {
        return this->position;
    }

    auto read(intptr_t size = -1) {
        intptr_t max_size = this->length() - this->position;
        if (size == -1 || size > max_size) size = max_size;
        return py::bytes((char*)(this->_p(size)), size);
    }

    i8  read_i8 () { return *((i8*) this->_p(1)); }
    i16 read_i16() { return *((i16*)this->_p(2)); }
    i32 read_i32() { return *((i32*)this->_p(4)); }
    i64 read_i64() { return *((i64*)this->_p(8)); }
    u8  read_u8 () { return *((u8*) this->_p(1)); }
    u16 read_u16() { return *((u16*)this->_p(2)); }
    u32 read_u32() { return *((u32*)this->_p(4)); }
    u64 read_u64() { return *((u64*)this->_p(8)); }

    i16 read_i16_be() { return (i16)_byteswap_ushort(this->read_i16()); }
    i32 read_i32_be() { return (i32)_byteswap_ulong (this->read_i32()); }
    i64 read_i64_be() { return (i64)_byteswap_uint64(this->read_i64()); }
    u16 read_u16_be() { return (u16)_byteswap_ushort(this->read_u16()); }
    u32 read_u32_be() { return (u32)_byteswap_ulong (this->read_u32()); }
    u64 read_u64_be() { return (u64)_byteswap_uint64(this->read_u64()); }

    void write(py::bytes data) {
        auto s = (std::string)data;
        intptr_t size = s.length();
        memmove(this->_wp(size), s.c_str(), size);
    }

    void write_i8 (i8  value) { *((i8*) this->_wp(1)) = value; }
    void write_i16(i16 value) { *((i16*)this->_wp(2)) = value; }
    void write_i32(i32 value) { *((i32*)this->_wp(4)) = value; }
    void write_i64(i64 value) { *((i64*)this->_wp(8)) = value; }
    void write_u8 (u8  value) { *((u8*) this->_wp(1)) = value; }
    void write_u16(u16 value) { *((u16*)this->_wp(2)) = value; }
    void write_u32(u32 value) { *((u32*)this->_wp(4)) = value; }
    void write_u64(u64 value) { *((u64*)this->_wp(8)) = value; }

    void write_i16_be(i16 value) { this->write_i16((i16)_byteswap_ushort((u16)value)); }
    void write_i32_be(i32 value) { this->write_i32((i32)_byteswap_ulong ((u32)value)); }
    void write_i64_be(i64 value) { this->write_i64((i64)_byteswap_uint64((u64)value)); }
    void write_u16_be(u16 value) { this->write_u16((u16)_byteswap_ushort((u16)value)); }
    void write_u32_be(u32 value) { this->write_u32((u32)_byteswap_ulong ((u32)value)); }
    void write_u64_be(u64 value) { this->write_u64((u64)_byteswap_uint64((u64)value)); }

    void truncate() {
        if (this->position < this->length()) {
            if (PyByteArray_Check(this->data.obj)) {
                this->_resize(this->position);
            } else {
                throw py::type_error("expect bytearray");
            }
        }
    }

    py::object getvalue() {
        return this->obj;
    }
};

PYBIND11_MODULE(_binaryio, m) {
    m.doc() = "BinaryIO";  // optional module docstring

    py::class_<BinaryIO>(m, "BinaryIO")
        .def(py::init<py::object>())
        .def("seek", &BinaryIO::seek, py::arg("offset"), py::arg("whence") = SEEK_SET)
        .def("tell", &BinaryIO::tell)
        .def("read", &BinaryIO::read, py::arg("size") = -1)
        .def("read_i8",  &BinaryIO::read_i8 )
        .def("read_i16", &BinaryIO::read_i16)
        .def("read_i32", &BinaryIO::read_i32)
        .def("read_i64", &BinaryIO::read_i64)
        .def("read_u8",  &BinaryIO::read_u8 )
        .def("read_u16", &BinaryIO::read_u16)
        .def("read_u32", &BinaryIO::read_u32)
        .def("read_u64", &BinaryIO::read_u64)
        .def("read_i16_be", &BinaryIO::read_i16_be)
        .def("read_i32_be", &BinaryIO::read_i32_be)
        .def("read_i64_be", &BinaryIO::read_i64_be)
        .def("read_u16_be", &BinaryIO::read_u16_be)
        .def("read_u32_be", &BinaryIO::read_u32_be)
        .def("read_u64_be", &BinaryIO::read_u64_be)
        .def("write", &BinaryIO::write)
        .def("write_i8",  &BinaryIO::write_i8 )
        .def("write_i16", &BinaryIO::write_i16)
        .def("write_i32", &BinaryIO::write_i32)
        .def("write_i64", &BinaryIO::write_i64)
        .def("write_u8",  &BinaryIO::write_u8 )
        .def("write_u16", &BinaryIO::write_u16)
        .def("write_u32", &BinaryIO::write_u32)
        .def("write_u64", &BinaryIO::write_u64)
        .def("write_i16_be", &BinaryIO::write_i16_be)
        .def("write_i32_be", &BinaryIO::write_i32_be)
        .def("write_i64_be", &BinaryIO::write_i64_be)
        .def("write_u16_be", &BinaryIO::write_u16_be)
        .def("write_u32_be", &BinaryIO::write_u32_be)
        .def("write_u64_be", &BinaryIO::write_u64_be)
        .def("truncate", &BinaryIO::truncate)
        .def("getvalue", &BinaryIO::getvalue);
}
